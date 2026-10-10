from kafka import KafkaProducer
import json

try:
    producer = KafkaProducer(
        bootstrap_servers="localhost:9093",
        security_protocol="SASL_PLAINTEXT",
        sasl_mechanism="PLAIN",
        sasl_plain_username="admin",
        sasl_plain_password="admin123",
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    producer.send("RPA_STR_NHNN_INPUT", {"cif": "12345678", "event_id": "test-event-1"})
    producer.flush()
    print("Message sent successfully.")
except Exception as e:
    print(f"Error: {e}")
