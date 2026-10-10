"""KafkaConsumerAdapter: nhận message từ topic, parse thành KafkaStrEvent.

Message không hợp lệ được ghi log và bỏ qua, không dừng consumer (BR1.1, REL-U1-4).
Adapter ẩn sau interface để mock trong test (NFR6).
"""
from __future__ import annotations

import json
from typing import Any, Iterator, Optional, Protocol

from robot.config import KafkaConfig
from robot.logging_setup import StructuredLogger
from robot.models import KafkaStrEvent


class MessageSource(Protocol):
    """Nguồn message trừu tượng (Kafka thật hoặc mock)."""

    def __iter__(self) -> Iterator[bytes]:
        ...


class RealKafkaMessageSource:
    """Implement nguồn message từ Kafka thật (kafka-python)."""
    
    def __init__(self, config: KafkaConfig) -> None:
        from kafka import KafkaConsumer
        
        import uuid
        kwargs = {
            "bootstrap_servers": config.bootstrap_servers,
            "group_id": f"{config.group_id}-{uuid.uuid4()}",
            "security_protocol": config.security_protocol,
            "auto_offset_reset": 'earliest',
            "consumer_timeout_ms": 10000, # Thoát nếu sau 10s không có message
            "enable_auto_commit": True,
            "api_version": (2, 5, 0),
        }
        if "SASL" in config.security_protocol:
            kwargs["sasl_mechanism"] = config.sasl_mechanism
            kwargs["sasl_plain_username"] = config.sasl_plain_username
            kwargs["sasl_plain_password"] = config.sasl_plain_password

        print(f"Đang kết nối Kafka tại {config.bootstrap_servers}, protocol={config.security_protocol}...")
        self.consumer = KafkaConsumer(config.topic, **kwargs)
        print("Kết nối Kafka thành công.")

    def __iter__(self) -> Iterator[bytes]:
        for msg in self.consumer:
            yield msg.value


class KafkaConsumerAdapter:
    """Bọc nguồn message, trả về các KafkaStrEvent hợp lệ."""

    def __init__(self, config: KafkaConfig, logger: StructuredLogger, source: MessageSource) -> None:
        self.config = config
        self.logger = logger
        self.source = source

    @staticmethod
    def parse_message(raw: bytes | str) -> Optional[KafkaStrEvent]:
        """Parse một message. Trả None nếu không hợp lệ."""
        try:
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            data: Any = json.loads(raw)
            if not isinstance(data, dict):
                return None
            event = KafkaStrEvent.from_dict(data)
        except (ValueError, json.JSONDecodeError):
            return None
        return event if event.is_valid() else None

    def events(self) -> Iterator[KafkaStrEvent]:
        """Lặp qua các event hợp lệ; message lỗi được log và bỏ qua."""
        for raw in self.source:
            raw_str = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
            self.logger.info("Raw Kafka message", raw=raw_str)
            event = self.parse_message(raw)
            if event is None:
                self.logger.error("Message Kafka không hợp lệ, bỏ qua", topic=self.config.topic)
                continue
            self.logger.info("Nhận message hợp lệ", event_id=event.event_id, cif=event.cif)
            yield event
