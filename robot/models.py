"""Mô hình dữ liệu dùng chung của pipeline STR.

StrRecord là object truyền qua lại và cập nhật tuần tự giữa các cấu phần U1..U5.
Mỗi cấu phần nhận record, ghi các cột của mình, rồi chuyển tiếp. Khi gặp lỗi,
cấu phần ghi lỗi vào record và đặt processing_stopped=True; các cấu phần sau bỏ
qua record đã dừng và chuyển thẳng tới U5 để tổng hợp và gửi email.

Hợp đồng cột đầy đủ: xem contract-summary.md (Contract Design).
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional


class CustomerType(str, Enum):
    """Loại khách hàng."""

    KHCN = "KHCN"  # khách hàng cá nhân
    KHDN = "KHDN"  # khách hàng doanh nghiệp


@dataclass
class KafkaStrEvent:
    """Message việc nhận từ Kafka. Mỗi message là một CIF cần xử lý."""

    event_id: str
    event_name: str
    cif: str
    time_stamp: str

    EXPECTED_EVENT_NAME = "LIST_CUST_STR"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KafkaStrEvent":
        """Dựng event từ payload JSON đã parse. Raise ValueError nếu thiếu field."""
        missing = [k for k in ("eventID", "eventName", "cif", "timeStamp") if not data.get(k)]
        if missing:
            raise ValueError(f"Message Kafka thiếu field: {', '.join(missing)}")
        return cls(
            event_id=str(data["eventID"]),
            event_name=str(data["eventName"]),
            cif=str(data["cif"]),
            time_stamp=str(data["timeStamp"]),
        )

    def is_valid(self) -> bool:
        """Message hợp lệ khi đúng eventName và có đủ field (BR1.1)."""
        return (
            self.event_name == self.EXPECTED_EVENT_NAME
            and bool(self.event_id)
            and bool(self.cif)
            and bool(self.time_stamp)
        )


@dataclass
class CashFlowSide:
    """Một chiều dòng tiền (vào hoặc ra)."""

    customer_count: int = 0
    transaction_count: int = 0
    amount: Decimal = field(default_factory=lambda: Decimal("0"))


@dataclass
class StrRecord:
    """Bản ghi STR theo một CIF, truyền và cập nhật tuần tự qua U1..U5."""

    # --- khóa & control ---
    cif: str = ""
    processing_stopped: bool = False
    written_by: str = ""

    # --- U1 ConsumeData điền ---
    ngay_tiep_nhan: str = ""
    email_nguoi_lap_bao_cao: str = ""
    user_id_nguoi_lap_bao_cao: str = ""
    bot_ecm: str = ""
    ten_khach_hang: str = ""
    loai_khach_hang: str = ""  # CustomerType value
    ma_so_thue: str = ""
    so_luong_kh_thuhuong: Optional[int] = None
    so_luong_giaodich_ra: Optional[int] = None
    so_tien_giaodich_ra: Optional[Decimal] = None
    so_luong_kh_guitienvao: Optional[int] = None
    so_luong_giaodich_vao: Optional[int] = None
    so_tien_giaodich_vao: Optional[Decimal] = None
    str_stk: str = ""
    loaitien_sotien: str = ""
    str_ma_bao_cao: str = ""
    ten_chi_nhanh: str = ""
    so_nha_duong_pho_chi_nhanh: str = ""
    phuong_xa_chi_nhanh: str = ""
    tinh_thanh_pho_chi_nhanh: str = ""
    ten_nguoi_lap_bao_cao: str = ""
    sdt_lam_viec_nguoi_lap_bao_cao: str = ""
    sdt_dd_nguoi_lap_bao_cao: str = ""
    phan_iv_loai_bao_cao_dang_ngo: str = ""
    phan_iv_dau_hieu_dang_ngo: str = ""
    ngay_bat_dau: str = ""
    ngay_ket_thuc: str = ""
    phan_iv_3_phan_tich_ly_do_bao_cao: str = ""
    phan_iv_co_so_hop_ly_de_nghi_ngo: str = ""
    phan_iv_nhan_dinh_loai_toi_pham: str = ""
    phan_v_cong_viec_xu_ly: str = ""
    sdt_chi_nhanh: str = ""

    # --- U2 DataEntryAccuity điền ---
    bot_accuity: str = ""
    # --- U3 DataEntryTraCuuThue điền ---
    bot_tracuuthe: str = ""
    # --- U4 DataEntryAMLD điền ---
    bot_almd: str = ""
    bot_tinhtrangtrasoat: str = ""
    # --- U4/U5 điền ---
    bot_ghichu: str = ""

    # --- đường dẫn file sinh ra ở U1 (không phải cột StrRecord nghiệp vụ) ---
    cashflow_pdf_path: str = ""
    dossier_pdf_paths: list[str] = field(default_factory=list)

    def stop(self, stage: str, note: str) -> None:
        """Đánh dấu record dừng xử lý, ghi ghi chú lỗi (BR1.7)."""
        self.processing_stopped = True
        self.written_by = stage
        if self.bot_ghichu:
            self.bot_ghichu += f" | {note}"
        else:
            self.bot_ghichu = note

    def to_status_row(self) -> dict[str, Any]:
        """Hàng trạng thái cho file đính kèm email (U5)."""
        return {
            "STR_CIF": self.cif,
            "TrangThai": "Lỗi" if self.processing_stopped else "Thành công",
            "MaLoi": self.bot_tinhtrangtrasoat,
            "ChiTietLoi": self.bot_ghichu,
        }

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        for k, v in d.items():
            if isinstance(v, Decimal):
                d[k] = str(v)
        return d
