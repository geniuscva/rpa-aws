"""Test RetryPolicy (U4): thử ≤ max_attempts lần rồi báo thất bại (BR4.8)."""
import pytest

from robot.u4_amld.retry_policy import RetryExhausted, RetryPolicy


def test_succeeds_first_try():
    calls = {"n": 0}

    def step():
        calls["n"] += 1
        return "ok"

    assert RetryPolicy(max_attempts=3).run(step) == "ok"
    assert calls["n"] == 1


def test_succeeds_within_limit():
    calls = {"n": 0}

    def step():
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("tạm thời lỗi")
        return "ok"

    assert RetryPolicy(max_attempts=3).run(step) == "ok"
    assert calls["n"] == 3


def test_fails_after_limit():
    calls = {"n": 0}

    def step():
        calls["n"] += 1
        raise RuntimeError("luôn lỗi")

    with pytest.raises(RetryExhausted):
        RetryPolicy(max_attempts=3).run(step, "bước X")
    assert calls["n"] == 3
