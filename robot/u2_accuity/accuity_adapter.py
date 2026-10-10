"""AccuityAdapter: giao tiếp web Accuity (mock) qua interface để test mock được.

Accuity là web mock: login (user/pass) + tra cứu + nút export PDF. Interface
AccuityPort cho phép thay hiện thực Playwright (production) bằng mock trong test
(NFR6). Credentials đọc từ config, không hardcode.
"""
from __future__ import annotations

import os
from typing import Any, Protocol

from robot.logging_setup import StructuredLogger
from robot.models import CustomerType


class AccuityError(Exception):
    """Lỗi khi thao tác với Accuity."""


class AccuityPort(Protocol):
    """Cổng trừu tượng tới Accuity (mock hoặc Playwright thật)."""

    def login(self) -> None: ...

    def lookup(self, entity_type: str, name: str) -> dict[str, Any]: ...

    def export_result_pdf(self, output_path: str) -> str: ...

    def export_record_pdf(self, output_path: str) -> str: ...


class AccuityResult:
    """Kết quả tra cứu Accuity."""

    def __init__(self, match_score: int, pdf_paths: list[str]) -> None:
        self.match_score = match_score
        self.pdf_paths = pdf_paths


class AccuityClient:
    """Điều phối luồng tra cứu Accuity qua AccuityPort, lưu PDF ra output_dir."""

    def __init__(self, port: AccuityPort, logger: StructuredLogger, output_dir: str) -> None:
        self.port = port
        self.logger = logger
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    @staticmethod
    def entity_type_for(customer_type: str) -> str:
        """Individual cho KHCN, Organization cho KHDN."""
        return "Individual" if customer_type == CustomerType.KHCN.value else "Organization"

    def lookup_customer(self, customer_type: str, name: str) -> AccuityResult:
        """Đăng nhập, tra cứu, export PDF. Raise AccuityError khi lỗi."""
        try:
            self.port.login()
            raw = self.port.lookup(self.entity_type_for(customer_type), name)
        except Exception as exc:  # noqa: BLE001 - gom lỗi cổng thành AccuityError
            raise AccuityError(f"Accuity lookup lỗi: {exc}") from exc

        pdf_paths: list[str] = []
        result_pdf = os.path.join(self.output_dir, "Tra cứu Accuity.pdf")
        pdf_paths.append(self.port.export_result_pdf(result_pdf))

        match_score = int(raw.get("match_score", 0))
        if match_score == 100:
            record_pdf = os.path.join(self.output_dir, "Tra cứu Accuity(1).pdf")
            pdf_paths.append(self.port.export_record_pdf(record_pdf))

        self.logger.info("Accuity tra cứu xong", name=name, match_score=match_score)
        return AccuityResult(match_score=match_score, pdf_paths=pdf_paths)


class PlaywrightAccuityPort:
    """Hiện thực AccuityPort bằng Playwright."""
    
    def __init__(self, config: Any, logger: StructuredLogger) -> None:
        self.config = config
        self.logger = logger
        self.base_url = getattr(config.accuity, "base_url", "http://localhost:5005")
        self.username = getattr(config.accuity, "username", "admin")
        self.password = getattr(config.accuity, "password", "admin")
        self._page: Any = None
        self._browser: Any = None
        self._playwright: Any = None
        self._match_score = 0
        
    def _ensure_page(self) -> Any:
        if self._page is None:
            from playwright.sync_api import sync_playwright # type: ignore
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=False,
                args=["--start-maximized"]
            )
            context = self._browser.new_context(no_viewport=True)
            self._page = context.new_page()
        return self._page
        
    def login(self) -> None:
        page = self._ensure_page()
        page.goto(self.base_url)
        page.fill("#username", self.username)
        page.fill("#password", self.password)
        page.wait_for_timeout(500)
        page.click("#loginBtn")
        page.wait_for_selector("#searchBtn")
        
    def lookup(self, entity_type: str, name: str) -> dict[str, Any]:
        page = self._ensure_page()
        page.select_option("#entityType", label=entity_type)
        page.fill("#name", name)
        page.check("#singleCheck")
        page.wait_for_timeout(1000)  # Thêm delay 1s để người dùng kịp nhìn form trước khi click
        page.click("#searchBtn")
        
        page.wait_for_selector(".matchScore")
        page.wait_for_timeout(2000)  # Thêm delay 2s để người dùng kịp nhìn kết quả
        match_score_text = page.inner_text(".matchScore")
        self._match_score = int(match_score_text.strip())
        return {"match_score": self._match_score}
        
    def export_result_pdf(self, output_path: str) -> str:
        page = self._ensure_page()
        with page.expect_download() as download_info:
            page.click("#exportPdfBtn")
        download = download_info.value
        download.save_as(output_path)
        return output_path
        
    def export_record_pdf(self, output_path: str) -> str:
        page = self._ensure_page()
        page.click("#openRecordBtn")
        page.wait_for_selector("#exportRecordPdfBtn")
        with page.expect_download() as download_info:
            page.click("#exportRecordPdfBtn")
        download = download_info.value
        download.save_as(output_path)
        return output_path
        
    def close(self) -> None:
        if self._browser is not None:
            self._browser.close()
        if self._playwright is not None:
            self._playwright.stop()
