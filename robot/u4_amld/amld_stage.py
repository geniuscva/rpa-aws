"""AmldStage (U4): nhập Mẫu số 01 lên AMLD Portal cho một CIF, cập nhật
StrRecord.BOT_ALMD + BOT_TINHTRANGTRASOAT.

Điểm hội tụ U2+U3. Nhập theo thứ tự Phần I → II → IV → V → VI, KHÔNG điền Phần III
(BR4.2). Mỗi bước bọc RetryPolicy (BR4.8); đăng nhập treo reload ≤ 3 (BR4.9);
kiểm tài liệu bắt buộc trước khi nộp (BR4.7); kiểm tick Phần IV/V trong tập cho
phép (BR4.6) và quy tắc 6/7/8→+4,5 (BR4.5). Lỗi/thiếu tài liệu/tick ngoài tập →
dừng record (processing_stopped) + BOT_GHICHU; U5 gửi email FAIL.
"""
from __future__ import annotations

import os
from typing import Callable, Optional

from robot.models import CustomerType, StrRecord
from robot.pipeline import StageContext
from robot.u4_amld.amld_portal_adapter import (
    AmldError,
    AmldLoginHung,
    AmldPortalPort,
    AmldSession,
)
from robot.u4_amld.attachment_uploader import AttachmentUploader, MissingAttachmentError
from robot.u4_amld.retry_policy import RetryExhausted, RetryPolicy
from robot.u4_amld.tick_validator import TickValidator, TickValueError

RESULT_OK = "OK"
RESULT_ERROR = "ERROR"

# Thứ tự nhập các Phần — Phần III CỐ TÌNH không có trong danh sách (BR4.2).
SECTION_ORDER = ("I", "II", "IV", "V", "VI")

# Tập giá trị tick hợp lệ mặc định cho Phần IV/V (số thứ tự công việc 1..8).
DEFAULT_ALLOWED_SECTION_IV = frozenset(range(1, 9))
DEFAULT_ALLOWED_SECTION_V = frozenset(range(1, 9))

MAX_LOGIN_ATTEMPTS = 3


class AmldStage:
    """Cấu phần U4 trong pipeline."""

    name = "U4-DataEntryAMLD"

    def __init__(
        self,
        port_factory: Callable[[StageContext], AmldPortalPort],
        retry_policy: Optional[RetryPolicy] = None,
        tick_validator: Optional[TickValidator] = None,
        attachment_uploader: Optional[AttachmentUploader] = None,
        section_iv_ticks: Optional[Callable[[StrRecord], list]] = None,
        section_v_ticks: Optional[Callable[[StrRecord], list]] = None,
    ) -> None:
        self._port_factory = port_factory
        self._retry = retry_policy or RetryPolicy()
        self._ticks = tick_validator or TickValidator(
            DEFAULT_ALLOWED_SECTION_IV, DEFAULT_ALLOWED_SECTION_V
        )
        self._attachments = attachment_uploader or AttachmentUploader()
        self._iv_ticks = section_iv_ticks or self._section_iv_ticks
        self._v_ticks = section_v_ticks or self._section_v_ticks

    def process(self, record: StrRecord, context: StageContext) -> StrRecord:
        # BR4.1: bỏ qua record đã dừng.
        if record.processing_stopped:
            return record

        logger = context.logger
        port = self._port_factory(context)

        try:
            # BR4.7: kiểm tài liệu bắt buộc TRƯỚC khi nộp — thiếu → không nộp.
            attachment_names = [os.path.basename(p) for p in record.dossier_pdf_paths]
            logger.info("Kiểm tra tài liệu bắt buộc", count=len(attachment_names))
            self._attachments.check_required(attachment_names)

            session = self._build_session(record, context)
            logger.info("Đăng nhập AMLD", url=session.endpoint)
            # BR4.9: đăng nhập, treo thì reload ≤ 3 lần.
            self._login_with_reload(port, session)
            logger.info("Đăng nhập thành công, mở mẫu 01")

            # Vào Mẫu số 01, nhập I→II→IV→V→VI, bỏ III (BR4.2).
            self._retry.run(port.open_form, "mở Mẫu số 01")
            
            logger.info("Nhập các phần của form AMLD")
            self._fill_sections(port, record)
            logger.info("Nhập form xong, chuẩn bị upload")

            # BR4.4: upload Phần VI đúng thứ tự.
            ordered_names = self._attachments.ordered(attachment_names)
            ordered_paths = []
            for name in ordered_names:
                for p in record.dossier_pdf_paths:
                    if os.path.basename(p) == name:
                        ordered_paths.append(p)
                        break

            for path in ordered_paths:
                logger.info("Upload file đính kèm", file=os.path.basename(path))
                self._retry.run(lambda p=path: port.upload([p]), f"upload {os.path.basename(path)}")

            # Nộp, ghi trạng thái tra soát (BR4.10).
            logger.info("Nộp báo cáo")
            trasoat = self._retry.run(port.submit, "nộp báo cáo")
            record.bot_almd = RESULT_OK
            record.bot_tinhtrangtrasoat = trasoat
            record.written_by = self.name
            logger.info("U4 hoàn tất", cif=record.cif, trasoat=trasoat)
            return record

        except MissingAttachmentError as exc:
            return self._fail(record, logger, f"Thiếu tài liệu bắt buộc: {exc}")
        except TickValueError as exc:
            return self._fail(record, logger, f"Tick ngoài tập cho phép: {exc}")
        except AmldLoginHung as exc:
            return self._fail(record, logger, f"Dang nhap AMLD treo qua gioi han: {exc}")
        except (RetryExhausted, AmldError) as exc:
            return self._fail(record, logger, f"Loi nhap AMLD: {exc}")
        finally:
            if hasattr(port, 'close'):
                port.close()

    # --- helpers -----------------------------------------------------------

    def _build_session(self, record: StrRecord, context: StageContext) -> AmldSession:
        amld_cfg = getattr(context.config, "amld", None)
        endpoint = getattr(amld_cfg, "almd_url", "") if amld_cfg else ""
        
        username = getattr(amld_cfg, "username_almd", "01311001I.02") if amld_cfg else "01311001I.02"
        password = getattr(amld_cfg, "password_almd", "Mb@12345") if amld_cfg else "Mb@12345"

        return AmldSession(
            username=username,
            endpoint=endpoint,
            password=password,
        )

    def _login_with_reload(self, port: AmldPortalPort, session: AmldSession) -> None:
        last: Optional[Exception] = None
        for _ in range(MAX_LOGIN_ATTEMPTS):
            try:
                port.login(session)
                return
            except AmldLoginHung as exc:
                last = exc  # reload và thử lại
        raise AmldLoginHung(
            f"đăng nhập treo quá {MAX_LOGIN_ATTEMPTS} lần"
        ) if last else AmldLoginHung("đăng nhập treo")

    def _fill_sections(self, port: AmldPortalPort, record: StrRecord) -> None:
        for section in SECTION_ORDER:
            data = record.as_dict()
            if section == "IV":
                values = self._ticks.validate_section_iv(self._iv_ticks(record))
                self._retry.run(
                    lambda s=section, d=data: port.fill_section(s, d), f"nhập Phần {section}"
                )
                port.set_ticks(section, values)
            elif section == "V":
                values = self._ticks.validate_section_v(self._v_ticks(record))
                self._retry.run(
                    lambda s=section, d=data: port.fill_section(s, d), f"nhập Phần {section}"
                )
                port.set_ticks(section, values)
            else:
                self._retry.run(
                    lambda s=section, d=data: port.fill_section(s, d),
                    f"nhập Phần {section}",
                )

    @staticmethod
    def _section_iv_ticks(record: StrRecord) -> list:
        """Giá trị tick Phần IV lấy từ record (ở đây rỗng = không có tick lạ)."""
        val = record.phan_iv_dau_hieu_dang_ngo
        if not val:
            return []
        return [int(x.strip()) for x in str(val).split(",") if x.strip().isdigit()]

    @staticmethod
    def _section_v_ticks(record: StrRecord) -> list:
        """Giá trị tick Phần V lấy từ record (quy tắc 6/7/8→+4,5 do validator áp)."""
        val = record.phan_v_cong_viec_xu_ly
        if not val:
            return []
        return [int(x.strip()) for x in str(val).split(",") if x.strip().isdigit()]

    def _fail(self, record: StrRecord, logger, note: str) -> StrRecord:
        # BR4.6/4.7/4.8/4.9: lỗi → dừng record, ghi BOT_ALMD/BOT_GHICHU/trạng thái.
        record.bot_almd = RESULT_ERROR
        record.bot_tinhtrangtrasoat = RESULT_ERROR
        record.stop(self.name, note)
        logger.error("U4 lỗi nhập AMLD", cif=record.cif, note=note)
        return record
