"""Test KafkaConsumerAdapter: parse message, bỏ qua message lỗi."""
import json

from robot.config import KafkaConfig
from robot.logging_setup import StructuredLogger
from robot.u1_consume.kafka_consumer import KafkaConsumerAdapter


def _logger(tmp_path):
    return StructuredLogger(str(tmp_path / "log.json"), echo_stdout=False)


VALID = {
    "eventID": "AUTOTEST-d0bd209b15de",
    "eventName": "LIST_CUST_STR",
    "cif": "6670501",
    "timeStamp": "1790226266242",
}


def test_parse_valid_message():
    event = KafkaConsumerAdapter.parse_message(json.dumps(VALID))
    assert event is not None
    assert event.cif == "6670501"
    assert event.is_valid()


def test_parse_rejects_missing_field():
    bad = dict(VALID)
    del bad["cif"]
    assert KafkaConsumerAdapter.parse_message(json.dumps(bad)) is None


def test_parse_rejects_wrong_event_name():
    bad = dict(VALID)
    bad["eventName"] = "SOMETHING_ELSE"
    assert KafkaConsumerAdapter.parse_message(json.dumps(bad)) is None


def test_parse_rejects_non_json():
    assert KafkaConsumerAdapter.parse_message("not-json") is None


def test_events_skips_invalid_and_yields_valid(tmp_path):
    source = [json.dumps(VALID).encode("utf-8"), b"garbage", json.dumps(VALID).encode("utf-8")]
    adapter = KafkaConsumerAdapter(KafkaConfig(), _logger(tmp_path), source)
    events = list(adapter.events())
    assert len(events) == 2
    assert all(e.cif == "6670501" for e in events)
