"""
Event Generator - Produces realistic content download events to Kafka
"""

import time
import random
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer
from kafka.errors import KafkaError

from config import config
from models import CONTENT_CATALOG, REGIONS, DEVICES, CONNECTION_TYPES, ERROR_TYPES
from serializers import AvroSerializer

fake = Faker()

class ContentEventGenerator:
    """Generates and produces content download events"""
    
    def __init__(self):
        """Initialize Kafka producer and Avro serializer"""
        
        # Validate configuration
        config.validate()
        
        # Initialize Avro serializer
        self.serializer = AvroSerializer(config.SCHEMA_PATH)
        
        # Initialize Kafka producer
        producer_config = {
            'bootstrap_servers': [config.KAFKA_BOOTSTRAP_SERVERS],
            'value_serializer': self.serializer.serialize,
            'key_serializer': lambda k: k.encode('utf-8') if k else None,
        }
        
        # Add SASL authentication if credentials provided
        if config.KAFKA_USERNAME and config.KAFKA_PASSWORD:
            producer_config.update({
                'security_protocol': config.KAFKA_SECURITY_PROTOCOL,
                'sasl_mechanism': config.KAFKA_SASL_MECHANISM,
                'sasl_plain_username': config.KAFKA_USERNAME,
                'sasl_plain_password': config.KAFKA_PASSWORD,
            })
        
        try:
            self.producer = KafkaProducer(**producer_config)
            print("✅ Connected to Kafka")
        except KafkaError as e:
            print(f"❌ Failed to connect to Kafka: {e}")
            raise
    
    def weighted_choice(self, items):
        """Choose item based on popularity weights"""
        weights = [item.popularity for item in items]
        return random.choices(items, weights=weights)[0]
    
    def generate_event(self) -> dict:
        """
        Generate a single realistic content download event
        
        Returns:
            Event dictionary matching Avro schema
        """
        # Select content based on popularity
        content = self.weighted_choice(CONTENT_CATALOG)
        
        # Select random region and device
        region, city = random.choice(REGIONS)
        device, os_version = random.choice(DEVICES)
        
        # Determine download outcome
        # 90% success, 8% failed, 2% slow
        outcome = random.choices(
            ['success', 'failed', 'slow'],
            weights=[90, 8, 2]
        )[0]
        
        # Build event
        event = {
            "event_id": fake.uuid4(),
            "timestamp": int(datetime.utcnow().timestamp() * 1000),
            "user_id": fake.uuid4(),
            "content": {
                "content_id": content.id,
                "title": content.title,
                "type": content.type,
                "category": content.category,
                "size_mb": content.size_mb,
                "price": content.price
            },
            "user_context": {
                "region": region,
                "city": city,
                "device": device,
                "os_version": os_version,
                "connection_type": random.choice(CONNECTION_TYPES)
            }
        }
        
        # Add download details based on outcome
        if outcome == 'success':
            event["download"] = {
                "status": "success",
                "duration_seconds": random.randint(60, 180),
                "speed_mbps": round(random.uniform(25.0, 50.0), 1),
                "error_code": None,
                "error_message": None
            }
        elif outcome == 'failed':
            error = random.choice(ERROR_TYPES)
            event["download"] = {
                "status": "failed",
                "duration_seconds": random.randint(10, 60),
                "speed_mbps": round(random.uniform(1.0, 5.0), 1),
                "error_code": error['code'],
                "error_message": error['message']
            }
        else:  # slow
            event["download"] = {
                "status": "success",
                "duration_seconds": random.randint(300, 600),  # 5-10 minutes
                "speed_mbps": round(random.uniform(5.0, 10.0), 1),
                "error_code": None,
                "error_message": None
            }
        
        return event
    
    def produce_event(self, event: dict):
        """
        Send event to Kafka topic
        
        Args:
            event: Event dictionary to send
        """
        try:
            # Use region as partition key for ordered processing
            partition_key = event['user_context']['region']
            
            future = self.producer.send(
                config.KAFKA_TOPIC,
                key=partition_key,
                value=event
            )
            
            # Wait for send to complete (blocking for demo purposes)
            record_metadata = future.get(timeout=10)
            
            return record_metadata
            
        except KafkaError as e:
            print(f"❌ Failed to send event: {e}")
            return None
    
    def run(self):
        """Main event generation loop"""
        print("\n" + "="*60)
        print("🚀 StreamPulse Event Generator")
        print("="*60)
        print(f"📊 Target: {config.EVENTS_PER_MINUTE} events/minute")
        print(f"📍 Topic: {config.KAFKA_TOPIC}")
        print(f"🔐 Authentication: {'Enabled' if config.KAFKA_USERNAME else 'Disabled'}")
        print("="*60 + "\n")
        
        event_count = 0
        sleep_seconds = 60.0 / config.EVENTS_PER_MINUTE
        
        try:
            while True:
                # Generate and send event
                event = self.generate_event()
                metadata = self.produce_event(event)
                
                if metadata:
                    event_count += 1
                    
                    # Log every 10 events
                    if event_count % 10 == 0:
                        print(f"✅ Sent {event_count} events | "
                              f"Latest: {event['content']['title']} → "
                              f"{event['user_context']['region']} | "
                              f"Status: {event['download']['status']}")
                
                # Sleep to maintain target rate
                time.sleep(sleep_seconds)
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Stopped. Total events sent: {event_count}")
            self.producer.close()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.producer.close()
            raise


if __name__ == "__main__":
    generator = ContentEventGenerator()
    generator.run()