"""Test TickValidator (U4): tập tick Phần IV/V (BR4.6) và quy tắc 6/7/8→+4,5 (BR4.5)."""
import pytest

from robot.u4_amld.tick_validator import TickValidator, TickValueError


def _validator():
    return TickValidator(allowed_section_iv=range(1, 9), allowed_section_v=range(1, 9))


def test_section_iv_valid_passes():
    assert _validator().validate_section_iv([1, 2, 3]) == [1, 2, 3]


def test_section_iv_outside_set_raises():
    with pytest.raises(TickValueError):
        _validator().validate_section_iv([1, 99])


def test_section_v_valid_without_trigger():
    # Không có 6/7/8 → giữ nguyên, không tự thêm 4,5.
    assert _validator().validate_section_v([1, 2]) == [1, 2]


def test_section_v_trigger_adds_4_and_5():
    # Có 6 → thêm 4 và 5 (BR4.5).
    result = _validator().validate_section_v([6])
    assert 4 in result and 5 in result and 6 in result


def test_section_v_trigger_does_not_duplicate():
    result = _validator().validate_section_v([5, 7])
    assert result.count(5) == 1
    assert 4 in result and 7 in result


def test_section_v_outside_set_raises():
    with pytest.raises(TickValueError):
        _validator().validate_section_v([6, 100])
