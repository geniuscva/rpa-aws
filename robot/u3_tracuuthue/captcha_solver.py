"""CaptchaSolver: giải captcha ảnh bằng ddddocr, giới hạn số lần thử (BR3.3).

ddddocr được import trễ (lazy) để test có thể mock mà không cần cài thư viện và
không chạm web thật (NFR6). Solver chỉ chịu trách nhiệm biến ảnh captcha thành
chuỗi; việc submit và kiểm tra đúng/sai do TaxAuthorityClient điều phối qua
nhiều lần thử.
"""
from __future__ import annotations

from typing import Any, Callable, Optional

DEFAULT_MAX_ATTEMPTS = 3


class CaptchaError(Exception):
    """Lỗi khi giải captcha (không giải được trong giới hạn số lần)."""


def _default_ddddocr_factory() -> Any:
    """Dựng engine ddddocr thật. Import trễ để test mock được, production mới cần."""
    import ddddocr  # type: ignore

    return ddddocr.DdddOcr(show_ad=False)


class CaptchaSolver:
    """Giải captcha bằng ddddocr với giới hạn số lần thử.

    `engine_factory` trả về object có method `classification(image_bytes) -> str`
    (ddddocr thật, hoặc fake trong test). Lazy: chỉ dựng engine ở lần giải đầu.
    """

    def __init__(
        self,
        engine_factory: Callable[[], Any] = _default_ddddocr_factory,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    ) -> None:
        self._engine_factory = engine_factory
        self._engine: Optional[Any] = None
        self.max_attempts = max(1, int(max_attempts))

    def _engine_instance(self) -> Any:
        if self._engine is None:
            self._engine = self._engine_factory()
        return self._engine

    def solve(self, image: bytes) -> str:
        """Giải một ảnh captcha, trả chuỗi đã nhận dạng.

        Raise CaptchaError nếu engine trả chuỗi rỗng (coi như không giải được).
        """
        engine = self._engine_instance()
        text = (engine.classification(image) or "").strip()
        if not text:
            raise CaptchaError("ddddocr trả chuỗi rỗng")
        return text

    def solve_with_retry(
        self,
        image_provider: Callable[[], bytes],
        verifier: Callable[[str], bool],
    ) -> str:
        """Giải captcha lặp lại tới khi `verifier` chấp nhận hoặc hết lượt.

        `image_provider()` lấy ảnh captcha hiện tại (có thể refresh mỗi lần thử);
        `verifier(text)` trả True khi captcha được chấp nhận (ví dụ submit không
        báo sai). Raise CaptchaError khi vượt `max_attempts` (BR3.3 → BR3.6).
        """
        last_error: Optional[Exception] = None
        for _ in range(self.max_attempts):
            try:
                text = self.solve(image_provider())
            except CaptchaError as exc:
                last_error = exc
                continue
            if verifier(text):
                return text
            last_error = CaptchaError("captcha bị từ chối")
        raise CaptchaError(
            f"Giải captcha thất bại sau {self.max_attempts} lần"
        ) from last_error
