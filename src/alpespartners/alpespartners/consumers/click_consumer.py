import json
import logging
from kafka import KafkaConsumer

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Create Kafka consumer
    consumer = KafkaConsumer(
        'tracking.clicks',
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='click_logger_group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    logger.info("Click consumer started. Waiting for messages...")

    try:
        for message in consumer:
            click_data = message.value
            logger.info(f"New click detected!")
            logger.info(f"Partner ID: {click_data['id_partner']}")
            logger.info(f"Campaign: {click_data['id_campana']}")
            logger.info(f"Click ID: {click_data['id_click']}")
            logger.info(f"Origin URL: {click_data['url_origen']}")
            logger.info(f"Destination URL: {click_data['url_destino']}")
            logger.info(f"Timestamp: {click_data['timestamp']}")
            logger.info("Client Metadata:")
            logger.info(f"  - IP: {click_data['metadata_cliente']['ip_address']}")
            logger.info(f"  - User Agent: {click_data['metadata_cliente']['user_agent']}")
            logger.info(f"  - Device: {click_data['metadata_cliente']['device_info']}")
            logger.info(f"  - Location: {click_data['metadata_cliente']['location_info']}")
            logger.info("-" * 50)

    except KeyboardInterrupt:
        logger.info("Shutting down click consumer...")
    finally:
        consumer.close()
        logger.info("Consumer closed.")

if __name__ == "__main__":
    main()
