"""SourceFolderResolver: tìm thư mục nguồn của một CIF theo ngày hiện tại.

Cấu trúc: <source_root>/YYYYMM/YYYYMMDD/<cif> (BR cho FR2).
"""
from __future__ import annotations

import os
from datetime import date
from typing import Optional

REQUIRED_FILES_COMMON = [
    "bang_ke_giao_dich_tai_khoan_dang_ngo.xlsx",
    "thong_tin_giao_dich_dang_ngo.xlsx",
    "thong_tin_dau_vao_bao_cao_str.xlsx",
]
INDIVIDUAL_FILE = "ca_nhan_thuc_hien_giao_dich.xlsx"
ORG_FILE = "to_chuc_thuc_hien_giao_dich.xlsx"


class SourceFolderResolver:
    """Phân giải đường dẫn thư mục CIF theo ngày."""

    def __init__(self, source_root: str) -> None:
        self.source_root = source_root

    def resolve(self, cif: str, on_date: Optional[date] = None) -> Optional[str]:
        """Trả đường dẫn thư mục CIF nếu tồn tại, ngược lại None."""
        on_date = on_date or date.today()
        
        def _check_for_date(d: date) -> Optional[str]:
            month = d.strftime("%Y%m")
            day = d.strftime("%Y%m%d")
            base_folder = os.path.join(self.source_root, month, day)
            
            # Thử 1: CUS.T24.<cif>
            folder_with_prefix = os.path.join(base_folder, f"CUS.T24.{cif}")
            if os.path.isdir(folder_with_prefix):
                return folder_with_prefix
                
            # Thử 2: khớp chính xác
            folder_exact = os.path.join(base_folder, cif)
            if os.path.isdir(folder_exact):
                return folder_exact
                
            # Thử 3: chứa cif
            if os.path.isdir(base_folder):
                for d_name in os.listdir(base_folder):
                    if cif in d_name:
                        folder_contains = os.path.join(base_folder, d_name)
                        if os.path.isdir(folder_contains):
                            return folder_contains
            return None

        # Kiểm tra ngày hiện tại trước
        result = _check_for_date(on_date)
        if result:
            return result
            
        # Nếu không có, thử kiểm tra thư mục của ngày hôm qua (trường hợp qua nửa đêm)
        from datetime import timedelta
        return _check_for_date(on_date - timedelta(days=1))

    @staticmethod
    def missing_required_files(folder: str) -> list[str]:
        """Trả danh sách file bắt buộc còn thiếu (BR1.4).

        Cần: 3 file common + (file cá nhân HOẶC file tổ chức).
        """
        missing: list[str] = []
        for name in REQUIRED_FILES_COMMON:
            if not os.path.isfile(os.path.join(folder, name)):
                missing.append(name)
        has_individual = os.path.isfile(os.path.join(folder, INDIVIDUAL_FILE))
        has_org = os.path.isfile(os.path.join(folder, ORG_FILE))
        if not has_individual and not has_org:
            missing.append(f"{INDIVIDUAL_FILE} hoặc {ORG_FILE}")
        return missing
