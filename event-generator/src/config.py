"""
Configuration management for Event Generator
Loads settings from environment variables
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'content-downloads')
    KAFKA_USERNAME = os.getenv('KAFKA_USERNAME', '')
    KAFKA_PASSWORD = os.getenv('KAFKA_PASSWORD', '')
    KAFKA_SECURITY_PROTOCOL = os.getenv('KAFKA_SECURITY_PROTOCOL', 'SASL_SSL')
    KAFKA_SASL_MECHANISM = os.getenv('KAFKA_SASL_MECHANISM', 'SCRAM-SHA-256')
    
    # Event Generation Configuration
    EVENTS_PER_MINUTE = int(os.getenv('EVENTS_PER_MINUTE', '7'))  # Stay under 10K/day free tier
    
    # Avro Schema Path
    SCHEMA_PATH = os.getenv('SCHEMA_PATH', '../schemas/event.avsc')
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = ['KAFKA_BOOTSTRAP_SERVERS']
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        print("✅ Configuration validated")
        print(f"   Kafka Servers: {cls.KAFKA_BOOTSTRAP_SERVERS}")
        print(f"   Topic: {cls.KAFKA_TOPIC}")
        print(f"   Events/min: {cls.EVENTS_PER_MINUTE}")

config = Config()