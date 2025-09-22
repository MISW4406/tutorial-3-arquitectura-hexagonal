from kafka import KafkaProducer
import json

import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
TOPIC_CLICKS = 'tracking.clicks'
TOPIC_CONVERSIONES = 'tracking.conversiones'
TOPIC_ATRIBUCIONES = 'tracking.atribuciones'

def get_kafka_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
