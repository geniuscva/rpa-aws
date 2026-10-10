"""EmailSender: dựng và gửi email trạng thái lô qua mail exchange (BR5.3, BR5.7).

EmailPort trừu tượng việc gửi để test mock được (NFR6). StatusEmail dựng From/To/
Cc + đính kèm Excel; From/Cc/endpoint/credentials đọc từ data/config.yaml, không
hardcode (BR5.7/NFR4). Gửi lỗi → trả SendResult(ok=False) chứ KHÔNG raise, để
BatchStatusReport đã dựng được giữ nguyên (BR5.3).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Protocol


class EmailError(Exception):
    """Lỗi khi gửi email."""


@dataclass
class StatusEmail:
    """Email trạng thái lô."""

    sender: str
    to: str
    cc: list[str]
    subject: str
    body: str
    attachment_path: str


@dataclass
class SendResult:
    """Kết quả gửi email."""

    ok: bool
    sent_at: str = ""
    error: str = ""


@dataclass
class MailConfig:
    """Cấu hình mail (đọc từ data/config.yaml, không hardcode)."""

    sender: str = ""
    cc: list[str] = field(default_factory=list)
    host: str = ""
    port: int = 25
    username: str = ""
    password: str = ""


class EmailPort(Protocol):
    """Cổng trừu tượng gửi email (mock hoặc SMTP thật)."""

    def send(self, email: StatusEmail) -> str:
        """Gửi email; trả timestamp gửi. Raise EmailError khi lỗi."""
        ...


DEFAULT_SUBJECT = "Trạng thái xử lý lô báo cáo STR"


def build_status_email(
    mail_cfg: MailConfig,
    to: str,
    attachment_path: str,
    subject: str = DEFAULT_SUBJECT,
    body: str = "Đính kèm file trạng thái xử lý lô báo cáo STR. Trân trọng.",
) -> StatusEmail:
    """Dựng StatusEmail từ cấu hình mail + người nhận (To = người lập báo cáo)."""
    return StatusEmail(
        sender=mail_cfg.sender,
        to=to,
        cc=list(mail_cfg.cc),
        subject=subject,
        body=body,
        attachment_path=attachment_path,
    )


class EmailSender:
    """Gửi StatusEmail qua EmailPort; không raise khi lỗi (BR5.3)."""

    def __init__(self, port: EmailPort, logger: Any) -> None:
        self.port = port
        self.logger = logger

    def send(self, email: StatusEmail) -> SendResult:
        try:
            sent_at = self.port.send(email)
            self.logger.info("Đã gửi email lô", to=email.to, cc=email.cc)
            return SendResult(ok=True, sent_at=sent_at)
        except Exception as exc:  # noqa: BLE001 - lỗi gửi không được làm hỏng report
            self.logger.error("Gửi email lô thất bại", to=email.to, error=str(exc))
            return SendResult(ok=False, error=str(exc))


class MockEmailPort:
    """Mock EmailPort cho test/dev: ghi lại email, không gửi thật."""

    def __init__(self, fail: bool = False, sent_at: str = "2026-01-01T00:00:00Z") -> None:
        self._fail = fail
        self._sent_at = sent_at
        self.sent: list[StatusEmail] = []

    def send(self, email: StatusEmail) -> str:
        if self._fail:
            raise EmailError("mail exchange không phản hồi")
        self.sent.append(email)
        return self._sent_at


class SmtpEmailPort:
    """Hiện thực EmailPort bằng SMTP cho mail exchange thật.

    Credentials/host/port đọc từ MailConfig (data/config.yaml), không hardcode,
    không log secret (BR5.7). Dùng ở production, không trong test.
    """

    def __init__(self, mail_cfg: MailConfig) -> None:
        self.mail_cfg = mail_cfg

    def send(self, email: StatusEmail) -> str:  # pragma: no cover - cần mail server thật
        import smtplib
        from datetime import datetime, timezone
        from email.message import EmailMessage

        msg = EmailMessage()
        msg["From"] = email.sender
        msg["To"] = email.to
        if email.cc:
            msg["Cc"] = ", ".join(email.cc)
        msg["Subject"] = email.subject
        msg.set_content(email.body)
        with open(email.attachment_path, "rb") as fh:
            data = fh.read()
        msg.add_attachment(
            data,
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=email.attachment_path.rsplit("/", 1)[-1],
        )
        with smtplib.SMTP(self.mail_cfg.host, self.mail_cfg.port) as server:
            if self.mail_cfg.username:
                server.login(self.mail_cfg.username, self.mail_cfg.password)
            server.send_message(msg)
        return datetime.now(timezone.utc).isoformat()
