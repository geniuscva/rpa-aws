"""Test IdempotencyStore: chống trùng theo eventID."""
from robot.u1_consume.idempotency import IdempotencyStore


def test_new_event_not_processed(tmp_path):
    store = IdempotencyStore(str(tmp_path / "seen.json"))
    assert store.is_processed("E1") is False


def test_marked_event_is_processed(tmp_path):
    store = IdempotencyStore(str(tmp_path / "seen.json"))
    store.mark_processed("E1")
    assert store.is_processed("E1") is True


def test_persisted_across_instances(tmp_path):
    path = str(tmp_path / "seen.json")
    store1 = IdempotencyStore(path)
    store1.mark_processed("E42")
    store2 = IdempotencyStore(path)
    assert store2.is_processed("E42") is True
