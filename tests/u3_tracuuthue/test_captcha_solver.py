"""Test CaptchaSolver (U3): giải bằng engine mock, giới hạn số lần thử.

Không cần ddddocr thật, không chạm web. Happy: giải đúng; edge: engine trả rỗng,
captcha bị từ chối vượt giới hạn → CaptchaError.
"""
import pytest

from robot.u3_tracuuthue.captcha_solver import CaptchaError, CaptchaSolver


class FakeEngine:
    """Engine ddddocr giả: trả lần lượt các chuỗi đã cho."""

    def __init__(self, outputs):
        self._outputs = list(outputs)
        self._i = 0

    def classification(self, image: bytes) -> str:
        value = self._outputs[min(self._i, len(self._outputs) - 1)]
        self._i += 1
        return value


def _solver(outputs, max_attempts=3) -> CaptchaSolver:
    return CaptchaSolver(engine_factory=lambda: FakeEngine(outputs), max_attempts=max_attempts)


def test_solve_returns_recognized_text():
    solver = _solver(["ABC123"])
    assert solver.solve(b"img") == "ABC123"


def test_solve_empty_output_raises():
    solver = _solver(["   "])
    with pytest.raises(CaptchaError):
        solver.solve(b"img")


def test_solve_with_retry_succeeds_on_second_try():
    solver = _solver(["wrong", "right"], max_attempts=3)
    attempts = {"n": 0}

    def verifier(text: str) -> bool:
        attempts["n"] += 1
        return text == "right"

    result = solver.solve_with_retry(image_provider=lambda: b"img", verifier=verifier)
    assert result == "right"
    assert attempts["n"] == 2


def test_solve_with_retry_fails_after_limit():
    solver = _solver(["no", "no", "no"], max_attempts=3)
    calls = {"img": 0}

    def image_provider() -> bytes:
        calls["img"] += 1
        return b"img"

    with pytest.raises(CaptchaError):
        solver.solve_with_retry(image_provider=image_provider, verifier=lambda t: False)
    # Thử đúng max_attempts lần rồi mới bỏ cuộc.
    assert calls["img"] == 3


def test_solve_with_retry_skips_empty_then_succeeds():
    # Lần đầu engine trả rỗng (CaptchaError nội bộ), lần sau giải được.
    solver = _solver(["", "good"], max_attempts=3)
    result = solver.solve_with_retry(image_provider=lambda: b"img", verifier=lambda t: t == "good")
    assert result == "good"
