"""ConsumeDataStage (U1): ghép toàn bộ bước xử lý input cho một CIF.

Nhận StrRecord (chỉ có CIF), xử lý: resolve folder -> phân loại KH -> kiểm file
-> đọc excel -> lấy hồ sơ ECM -> tính & xuất dòng tiền -> dựng StrRecord.
Lỗi ghi vào record và đặt processing_stopped=True (BR1.7).
"""
from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

from robot.models import CustomerType, StrRecord
from robot.pipeline import StageContext
from robot.u1_consume.cashflow import CashFlowCalculator, CashFlowPdfRenderer
from robot.u1_consume.classifier import CustomerClassifier
from robot.u1_consume.ecm_client import EcmClientAdapter, EcmError
from robot.u1_consume.excel_reader import ExcelReader
from robot.u1_consume.source_folder import SourceFolderResolver


class ConsumeDataStage:
    """Cấu phần U1 trong pipeline."""

    name = "U1-ConsumeData"

    def __init__(self, ecm_client_factory, resolver: Optional[SourceFolderResolver] = None) -> None:
        # ecm_client_factory(cif, output_dir) -> EcmClientAdapter (cho phép mock)
        self._ecm_client_factory = ecm_client_factory
        self._resolver = resolver

    def process(self, record: StrRecord, context: StageContext) -> StrRecord:
        logger = context.logger
        cfg = context.config
        cif = record.cif
        resolver = self._resolver or SourceFolderResolver(cfg.source_root)

        folder = resolver.resolve(cif)
        if folder is None:
            logger.error("Không tìm thấy thư mục CIF", cif=cif)
            record.stop(self.name, f"Khong tim thay thu muc CIF {cif}")
            return record

        customer_type = CustomerClassifier.classify(folder)
        if customer_type is None:
            logger.error("Không xác định được loại KH (thiếu file cá nhân/tổ chức)", cif=cif)
            record.stop(self.name, "Thieu file ca nhan/to chuc, khong xac dinh loai KH")
            return record
        record.loai_khach_hang = customer_type.value

        missing = resolver.missing_required_files(folder)
        if missing:
            logger.error("Thiếu file bắt buộc", cif=cif, missing=missing)
            record.stop(self.name, f"Thieu file bat buoc: {', '.join(missing)}")
            return record

        reader = ExcelReader(folder)
        try:
            input_rows = reader.read_input_str()
            statement_rows = reader.read_statement()
        except (FileNotFoundError, OSError) as exc:
            logger.error("Lỗi đọc file excel", cif=cif, error=str(exc))
            record.stop(self.name, f"Loi doc file excel: {exc}")
            return record

        self._fill_input_fields(record, input_rows)

        # Lấy hồ sơ PDF qua ECM mock
        output_dir = os.path.join(cfg.output_root, cif)
        os.makedirs(output_dir, exist_ok=True)
        try:
            ecm_client: EcmClientAdapter = self._ecm_client_factory(cif, output_dir)
            dossier_paths, extracted_mst = ecm_client.fetch_dossier(cif)
            
            if extracted_mst and not record.ma_so_thue:
                record.ma_so_thue = extracted_mst
                logger.info(f"Bổ sung MST từ ECM metadata: {extracted_mst}")
            
            # Copy tất cả file input sang output_dir và thêm các file cần thiết vào
            # danh sách đính kèm. Best-effort: thư mục nguồn không đọc được không
            # được làm hỏng cả stage (hồ sơ ECM mới là nguồn bắt buộc).
            import shutil
            try:
                source_files = os.listdir(folder)
            except OSError as copy_exc:
                logger.error("Khong liet ke duoc thu muc nguon de copy input", cif=cif, error=str(copy_exc))
                source_files = []
            for fname in source_files:
                src_path = os.path.join(folder, fname)
                if os.path.isfile(src_path):
                    dst_path = os.path.join(output_dir, fname)
                    shutil.copy2(src_path, dst_path)
                    if fname.startswith("bang_ke") or fname.startswith("HSMTK"):
                        dossier_paths.append(dst_path)

            record.dossier_pdf_paths = dossier_paths
            record.bot_ecm = "OK"
        except EcmError as exc:
            logger.error("Lỗi lấy hồ sơ ECM", cif=cif, error=str(exc))
            record.bot_ecm = "ERROR"
            record.stop(self.name, f"Loi ECM: {exc}")
            return record

        # Tính & xuất dòng tiền
        try:
            inflow, outflow = CashFlowCalculator.compute(statement_rows)
            record.so_luong_kh_guitienvao = inflow.customer_count
            record.so_luong_giaodich_vao = inflow.transaction_count
            record.so_tien_giaodich_vao = inflow.amount
            record.so_luong_kh_thuhuong = outflow.customer_count
            record.so_luong_giaodich_ra = outflow.transaction_count
            record.so_tien_giaodich_ra = outflow.amount
            renderer = CashFlowPdfRenderer(output_dir)
            cashflow_path = renderer.render(record.ten_khach_hang or cif, inflow, outflow)
            record.cashflow_pdf_path = cashflow_path
            record.dossier_pdf_paths.append(cashflow_path)
        except Exception as exc:  # noqa: BLE001 - lỗi tính/xuất coi là lỗi record
            logger.error("Lỗi tính/xuất dòng tiền", cif=cif, error=str(exc))
            record.stop(self.name, f"Loi dong tien: {exc}")
            return record

        record.written_by = self.name
        logger.info("U1 hoàn tất", cif=cif, loai_kh=record.loai_khach_hang)
        return record

    @staticmethod
    def _first(rows: list[dict[str, Any]]) -> dict[str, Any]:
        return rows[0] if rows else {}

    @classmethod
    def _fill_input_fields(cls, record: StrRecord, input_rows: list[dict[str, Any]]) -> None:
        """Điền các cột StrRecord từ thong_tin_dau_vao_bao_cao_str.xlsx."""
        row = cls._first(input_rows)

        def g(*keys: str) -> str:
            for k in keys:
                if row.get(k) not in (None, ""):
                    return str(row.get(k))
            return ""

        record.ten_khach_hang = g("STR_TEN_KH", "TENKHACHHANG")
        record.ma_so_thue = g("Ma_So_Doanh_Nghiep", "MASOTHUE")
        record.email_nguoi_lap_bao_cao = g("EMAIL_NGUOI_LAP_BAO_CAO")
        record.user_id_nguoi_lap_bao_cao = g("USER_ID_NGUOI_LAP_BAO_CAO")
        record.str_ma_bao_cao = g("STR_MA_BAO_CAO")
        record.str_stk = g("STR_STK")
        record.ngay_tiep_nhan = g("NGAYTIEPNHAN")
        record.ten_nguoi_lap_bao_cao = g("TEN_NGUOI_LAP_BAO_CAO")
        record.sdt_lam_viec_nguoi_lap_bao_cao = g("SDT_LAM_VIEC_NGUOI_LAP_BAO_CAO")
        record.sdt_dd_nguoi_lap_bao_cao = g("SDT_DD_NGUOI_LAP_BAO_CAO")
