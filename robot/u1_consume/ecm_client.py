"""EcmClientAdapter: lấy hồ sơ PDF khách hàng qua ECM mock API (FR14, BR1.5).

Luồng: lấy token (client_credentials) -> search theo customerCode với từng
business_code -> tải PDF theo doc_id. Có timeout + retry nhẹ (REL-U1-2).
Credentials đọc từ config (không hardcode, không log). Ẩn sau interface để mock.
"""
from __future__ import annotations

import os
import time
from typing import Any, Optional, Protocol

from robot.config import EcmConfig
from robot.logging_setup import StructuredLogger


class EcmTransport(Protocol):
    """Lớp giao tiếp HTTP trừu tượng (httpx thật hoặc mock trong test)."""

    def post_token(self, config: EcmConfig) -> str:
        ...

    def search_files(self, config: EcmConfig, token: str, business_code: str, cif: str) -> list[dict[str, Any]]:
        ...

    def download_content(self, config: EcmConfig, token: str, doc_id: str) -> bytes:
        ...


class EcmError(Exception):
    """Lỗi khi gọi ECM."""


class HttpxEcmTransport:
    """Implement giao tiếp ECM qua HTTP (httpx)."""
    
    def post_token(self, config: EcmConfig) -> str:
        import httpx
        url = f"{config.base_url}{config.token_path}"
        data = {
            "grant_type": "client_credentials",
            "client_id": config.client_id,
            "client_secret": config.client_secret,
        }
        with httpx.Client(timeout=config.timeout_seconds) as client:
            resp = client.post(url, data=data)
            resp.raise_for_status()
            return resp.json()["access_token"]

    def search_files(self, config: EcmConfig, token: str, business_code: str, cif: str) -> list[dict[str, Any]]:
        import httpx
        url = f"{config.base_url}/ecm-core-v1.0/businesses/{business_code}/files/search"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        payload = {
            "metadata": {
                "customerCode": {
                    "type": "eq",
                    "value": cif
                }
            },
            "pagination": {
                "page": 1,
                "size": 100
            }
        }
        with httpx.Client(timeout=config.timeout_seconds) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            response_data = resp.json()
            data_obj = response_data.get("data") or {}
            return data_obj.get("result", [])

    def download_content(self, config: EcmConfig, token: str, doc_id: str) -> bytes:
        import httpx
        url = f"{config.base_url}/ecm-core-v1.0/files/{doc_id}/content"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        with httpx.Client(timeout=config.timeout_seconds) as client:
            resp = client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.content


class EcmClientAdapter:
    """Điều phối luồng lấy hồ sơ qua ECM, lưu PDF ra output_dir."""

    def __init__(
        self,
        config: EcmConfig,
        logger: StructuredLogger,
        transport: EcmTransport,
        output_dir: str,
    ) -> None:
        self.config = config
        self.logger = logger
        self.transport = transport
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _with_retry(self, fn, what: str):
        last_exc: Optional[Exception] = None
        for attempt in range(1, max(1, self.config.retries) + 1):
            try:
                return fn()
            except Exception as exc:  # noqa: BLE001 - gom lỗi transport để retry
                last_exc = exc
                self.logger.error(f"ECM {what} lỗi lần {attempt}", attempt=attempt)
                if attempt < self.config.retries:
                    time.sleep(min(2 ** (attempt - 1), 5))
        raise EcmError(f"ECM {what} thất bại sau {self.config.retries} lần") from last_exc

    @staticmethod
    def _map_business_code_to_prefix(bc: str) -> str:
        mapping = {
            "mb_smart_channel": "HSMTK",
            "customer_info_ca": "GTTT",
            "ss_customer_doc": "HSMTK",
            "ss_auto_upload_customer_info": "HSMTK",
            "customer_information": "HSMTK",
            "biz_onboarding": "Giay phep thanh lap"
        }
        return mapping.get(bc, "HSMTK")

    def fetch_dossier(self, cif: str) -> tuple[list[str], str]:
        """Trả (danh sách đường dẫn PDF đã tải, MST). Raise EcmError nếu lỗi."""
        import json
        token = self._with_retry(lambda: self.transport.post_token(self.config), "lấy token")
        saved_paths: list[str] = []
        extracted_mst = ""
        for business_code in self.config.business_codes:
            try:
                files_list = self._with_retry(
                    lambda bc=business_code: self.transport.search_files(self.config, token, bc, cif),
                    f"search {business_code}",
                )
            except EcmError:
                continue

            if not isinstance(files_list, list):
                self.logger.warning("ECM search không trả về list hợp lệ", business_code=business_code, cif=cif)
                continue

            for item in files_list:
                if not isinstance(item, dict):
                    continue
                doc_id = str(item.get("fileId") or item.get("doc_id") or item.get("docId") or "").strip()
                if not doc_id:
                    continue
                
                # Bóc tách metadata để lấy MST/CCCD
                if not extracted_mst:
                    raw_meta = item.get("metadata", "")
                    meta_dict = {}
                    if isinstance(raw_meta, str) and raw_meta.strip():
                        try:
                            meta_dict = json.loads(raw_meta)
                        except json.JSONDecodeError:
                            pass
                    elif isinstance(raw_meta, dict):
                        meta_dict = raw_meta
                    mst = str(meta_dict.get("businessRegisNum") or meta_dict.get("customerNationalId") or "").strip()
                    if mst:
                        extracted_mst = mst

                content = self._with_retry(
                    lambda d=doc_id: self.transport.download_content(self.config, token, d),
                    f"download {doc_id}",
                )
                prefix = self._map_business_code_to_prefix(business_code)
                filename = f"{prefix}_{doc_id}.pdf"
                path = os.path.join(self.output_dir, filename)
                with open(path, "wb") as fh:
                    fh.write(content)
                saved_paths.append(path)
        self.logger.info("Lấy hồ sơ ECM xong", cif=cif, count=len(saved_paths), mst=extracted_mst)
        return saved_paths, extracted_mst
