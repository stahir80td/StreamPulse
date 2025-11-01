"""
Configuration management for Flink Processor
Loads settings from environment variables
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Kafka Configuration
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'content-downloads')
    KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'flink-processor')
    KAFKA_USERNAME = os.getenv('KAFKA_USERNAME', '')
    KAFKA_PASSWORD = os.getenv('KAFKA_PASSWORD', '')
    KAFKA_SECURITY_PROTOCOL = os.getenv('KAFKA_SECURITY_PROTOCOL', 'SASL_SSL')
    KAFKA_SASL_MECHANISM = os.getenv('KAFKA_SASL_MECHANISM', 'SCRAM-SHA-256')
    
    # PostgreSQL Configuration
    PG_HOST = os.getenv('PG_HOST', 'localhost')
    PG_PORT = int(os.getenv('PG_PORT', '5432'))
    PG_DATABASE = os.getenv('PG_DATABASE', 'streampulse')
    PG_USER = os.getenv('PG_USER', 'postgres')
    PG_PASSWORD = os.getenv('PG_PASSWORD', '')
    PG_SSLMODE = os.getenv('PG_SSLMODE', 'require')
    
    # Flink Configuration
    FLINK_PARALLELISM = int(os.getenv('FLINK_PARALLELISM', '1'))
    FLINK_CHECKPOINT_INTERVAL = int(os.getenv('FLINK_CHECKPOINT_INTERVAL', '60000'))  # 60 seconds
    FLINK_CHECKPOINT_DIR = os.getenv('FLINK_CHECKPOINT_DIR', 'file:///tmp/flink-checkpoints')
    
    # Avro Schema Path
    SCHEMA_PATH = os.getenv('SCHEMA_PATH', '../schemas/event.avsc')
    
    @classmethod
    def get_kafka_properties(cls):
        """Get Kafka consumer properties as dictionary"""
        props = {
            'bootstrap.servers': cls.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': cls.KAFKA_GROUP_ID,
            'auto.offset.reset': 'latest',
            'enable.auto.commit': 'false',  # Manual commit for exactly-once
        }
        
        # Add SASL authentication if credentials provided
        if cls.KAFKA_USERNAME and cls.KAFKA_PASSWORD:
            props.update({
                'security.protocol': cls.KAFKA_SECURITY_PROTOCOL,
                'sasl.mechanism': cls.KAFKA_SASL_MECHANISM,
                'sasl.username': cls.KAFKA_USERNAME,
                'sasl.password': cls.KAFKA_PASSWORD,
            })
        
        return props
    
    @classmethod
    def get_pg_connection_string(cls):
        """Get PostgreSQL connection string"""
        return (
            f"host={cls.PG_HOST} "
            f"port={cls.PG_PORT} "
            f"dbname={cls.PG_DATABASE} "
            f"user={cls.PG_USER} "
            f"password={cls.PG_PASSWORD} "
            f"sslmode={cls.PG_SSLMODE}"
        )
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = {
            'KAFKA_BOOTSTRAP_SERVERS': cls.KAFKA_BOOTSTRAP_SERVERS,
            'PG_HOST': cls.PG_HOST,
            'PG_DATABASE': cls.PG_DATABASE,
            'PG_USER': cls.PG_USER,
            'PG_PASSWORD': cls.PG_PASSWORD,
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        print("✅ Configuration validated")
        print(f"   Kafka: {cls.KAFKA_BOOTSTRAP_SERVERS}")
        print(f"   Topic: {cls.KAFKA_TOPIC}")
        print(f"   Database: {cls.PG_HOST}/{cls.PG_DATABASE}")
        print(f"   Parallelism: {cls.FLINK_PARALLELISM}")

config = Config()