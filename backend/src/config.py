"""
Configuration management for Backend API
Loads settings from environment variables
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # PostgreSQL Configuration
    PG_HOST = os.getenv('PG_HOST', 'localhost')
    PG_PORT = int(os.getenv('PG_PORT', '5432'))
    PG_DATABASE = os.getenv('PG_DATABASE', 'streampulse')
    PG_USER = os.getenv('PG_USER', 'postgres')
    PG_PASSWORD = os.getenv('PG_PASSWORD', '')
    PG_SSLMODE = os.getenv('PG_SSLMODE', 'require')
    
    # API Configuration
    API_TITLE = os.getenv('API_TITLE', 'StreamPulse API')
    API_VERSION = os.getenv('API_VERSION', '1.0.0')
    API_PREFIX = os.getenv('API_PREFIX', '/api')
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 
        'http://localhost:3000,https://streampulse.vercel.app').split(',')
    
    # Cache Configuration
    CACHE_TTL = int(os.getenv('CACHE_TTL', '2'))  # seconds
    
    @classmethod
    def get_database_url(cls):
        """Get PostgreSQL connection string"""
        return (
            f"postgresql://{cls.PG_USER}:{cls.PG_PASSWORD}@"
            f"{cls.PG_HOST}:{cls.PG_PORT}/{cls.PG_DATABASE}"
            f"?sslmode={cls.PG_SSLMODE}"
        )
    
    @classmethod
    def get_connection_params(cls):
        """Get PostgreSQL connection parameters as dict"""
        return {
            'host': cls.PG_HOST,
            'port': cls.PG_PORT,
            'database': cls.PG_DATABASE,
            'user': cls.PG_USER,
            'password': cls.PG_PASSWORD,
            'sslmode': cls.PG_SSLMODE
        }
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = {
            'PG_HOST': cls.PG_HOST,
            'PG_DATABASE': cls.PG_DATABASE,
            'PG_USER': cls.PG_USER,
            'PG_PASSWORD': cls.PG_PASSWORD,
        }
        
        missing = [key for key, value in required.items() if not value]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        print("✅ Backend configuration validated")
        print(f"   Database: {cls.PG_HOST}/{cls.PG_DATABASE}")
        print(f"   API Version: {cls.API_VERSION}")
        print(f"   CORS Origins: {cls.ALLOWED_ORIGINS}")

config = Config()