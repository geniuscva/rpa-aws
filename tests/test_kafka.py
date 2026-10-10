from kafka import KafkaConsumer
import logging
logging.basicConfig(level=logging.DEBUG)

print("Starting Kafka consumer test...")
try:
    consumer = KafkaConsumer(
        "RPA_STR_NHNN_INPUT",
        bootstrap_servers="localhost:9093",
        group_id="rpa-str-consumer",
        security_protocol="SASL_PLAINTEXT",
        sasl_mechanism="PLAIN",
        sasl_plain_username="admin",
        sasl_plain_password="admin123",
        auto_offset_reset="earliest",
        consumer_timeout_ms=5000,
        api_version=(2, 5, 0)
    )
    print("Kafka consumer created successfully.")
    for msg in consumer:
        print(f"Msg: {msg}")
except Exception as e:
    print(f"Error: {e}")
print("Done.")
