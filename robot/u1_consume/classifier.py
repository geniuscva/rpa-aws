"""CustomerClassifier: xác định loại khách hàng theo file hiện diện (BR1.3, FR4)."""
from __future__ import annotations

import os
from typing import Optional

from robot.models import CustomerType
from robot.u1_consume.source_folder import INDIVIDUAL_FILE, ORG_FILE


class CustomerClassifier:
    """Phân loại KHCN/KHDN dựa vào file nào có mặt trong folder CIF."""

    @staticmethod
    def classify(folder: str) -> Optional[CustomerType]:
        """Có file cá nhân -> KHCN; có file tổ chức -> KHDN; không có -> None."""
        if os.path.isfile(os.path.join(folder, INDIVIDUAL_FILE)):
            return CustomerType.KHCN
        if os.path.isfile(os.path.join(folder, ORG_FILE)):
            return CustomerType.KHDN
        return None
