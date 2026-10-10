"""Test AttachmentUploader (U4): tài liệu bắt buộc (BR4.7) + thứ tự upload (BR4.4)."""
import pytest

from robot.u4_amld.attachment_uploader import AttachmentUploader, MissingAttachmentError

REQUIRED = ["Bảng kê giao dịch.pdf", "Minh Họa Dòng Tiền.pdf", "HSMTK_001.pdf"]


def test_all_required_present_passes():
    AttachmentUploader().check_required(REQUIRED)  # không raise


def test_missing_required_raises():
    files = ["Bảng kê giao dịch.pdf", "HSMTK_001.pdf"]  # thiếu Minh Họa Dòng Tiền
    with pytest.raises(MissingAttachmentError):
        AttachmentUploader().check_required(files)


def test_missing_required_lists_missing():
    files = ["Bảng kê giao dịch.pdf"]
    missing = AttachmentUploader().missing_required(files)
    assert "Minh Họa Dòng Tiền" in missing
    assert "HSMTK" in missing


def test_order_follows_section_vi_sequence():
    files = [
        "Tra cứu Accuity.pdf",
        "HSMTK_001.pdf",
        "Bảng kê giao dịch.pdf",
        "Minh Họa Dòng Tiền.pdf",
    ]
    ordered = AttachmentUploader().ordered(files)
    # Bảng kê trước Minh Họa Dòng Tiền trước HSMTK trước Tra cứu Accuity.
    assert ordered[0].startswith("Bảng kê")
    assert ordered[1].startswith("Minh Họa Dòng Tiền")
    assert ordered[2].startswith("HSMTK")
    assert ordered[-1].startswith("Tra cứu Accuity")


def test_unknown_files_go_last_keeping_order():
    files = ["khac_1.pdf", "Bảng kê.pdf", "khac_2.pdf"]
    ordered = AttachmentUploader().ordered(files)
    assert ordered[0].startswith("Bảng kê")
    assert ordered[1] == "khac_1.pdf"
    assert ordered[2] == "khac_2.pdf"
