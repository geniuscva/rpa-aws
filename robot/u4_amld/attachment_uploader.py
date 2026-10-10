"""AttachmentUploader: kiểm đủ tài liệu bắt buộc trước khi nộp (BR4.7) và sắp
xếp upload Phần VI đúng thứ tự cố định (BR4.4).

Thiếu một trong các tài liệu bắt buộc (Bảng kê, Minh Họa Dòng Tiền.pdf, Hồ sơ mở
tài khoản) → raise MissingAttachmentError để stage KHÔNG nộp báo cáo, email FAIL
(ở U5). Đây là ràng buộc project.md đã affirmed.
"""
from __future__ import annotations

from typing import Iterable


class MissingAttachmentError(Exception):
    """Thiếu một hoặc nhiều tài liệu bắt buộc cho Phần VI."""


#: Prefix tên các tài liệu BẮT BUỘC phải có mới được nộp (BR4.7).
#: Dùng tên hiển thị tiếng Việt vì file nguồn mang tên hiển thị (vd
#: "Bảng kê giao dịch.pdf"), không phải snake_case.
REQUIRED_ATTACHMENT_PREFIXES = (
    "Bảng kê",
    "Minh Họa Dòng Tiền",
    "HSMTK",  # Hồ sơ mở tài khoản
)

#: Thứ tự ưu tiên upload Phần VI (BR4.4). Nhỏ hơn = upload trước.
UPLOAD_ORDER = (
    "Bảng kê",
    "Minh Họa Dòng Tiền",
    "HSMTK",  # Hồ sơ mở tài khoản
    "Giay phep thanh lap",  # Hồ sơ khách hàng
    "GTTT",
    "Tra cứu Accuity",  # Tài liệu khác
    "Tra cứu tình trạng người nộp thuế",
)


import unicodedata

def _matches(name: str, prefix: str) -> bool:
    def normalize(s: str) -> str:
        s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('utf-8')
        return s.strip().lower().replace('_', ' ')
    
    return normalize(name).startswith(normalize(prefix))


class AttachmentUploader:
    """Kiểm tra tài liệu bắt buộc và trả thứ tự upload Phần VI."""

    def __init__(
        self,
        required_prefixes: Iterable[str] = REQUIRED_ATTACHMENT_PREFIXES,
        upload_order: Iterable[str] = UPLOAD_ORDER,
    ) -> None:
        self.required_prefixes = tuple(required_prefixes)
        self.upload_order = tuple(upload_order)

    def missing_required(self, filenames: Iterable[str]) -> list[str]:
        """Trả danh sách prefix tài liệu bắt buộc còn thiếu (rỗng nếu đủ)."""
        names = list(filenames)
        return [
            prefix
            for prefix in self.required_prefixes
            if not any(_matches(name, prefix) for name in names)
        ]

    def check_required(self, filenames: Iterable[str]) -> None:
        """Raise MissingAttachmentError nếu thiếu tài liệu bắt buộc (BR4.7)."""
        missing = self.missing_required(filenames)
        if missing:
            raise MissingAttachmentError(
                f"Thiếu tài liệu bắt buộc: {', '.join(missing)}"
            )

    def ordered(self, filenames: Iterable[str]) -> list[str]:
        """Sắp xếp file theo thứ tự upload Phần VI (BR4.4).

        File khớp prefix xếp theo UPLOAD_ORDER (nhiều file cùng loại giữ thứ tự
        gốc); file không khớp prefix nào xếp cuối, giữ thứ tự gốc.
        """
        names = list(filenames)

        def rank(name: str) -> int:
            for i, prefix in enumerate(self.upload_order):
                if _matches(name, prefix):
                    return i
            return len(self.upload_order)

        return sorted(names, key=lambda n: (rank(n), names.index(n)))
