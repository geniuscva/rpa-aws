from kafka import KafkaProducer
import json
producer = KafkaProducer(
    bootstrap_servers="localhost:9093",
    security_protocol="SASL_PLAINTEXT",
    sasl_mechanism="PLAIN",
    sasl_plain_username="admin",
    sasl_plain_password="admin123",
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
producer.send("RPA_STR_NHNN_INPUT", {"eventID": "AUTOTEST-d0bd209b15de", "eventName": "LIST_CUST_STR", "cif": "6670501", "timeStamp": "1790226266242"})
producer.flush()
