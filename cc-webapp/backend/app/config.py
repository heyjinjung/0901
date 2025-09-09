"""
Casino-Club F2P - Configuration Management
=====================================
Environment variable based application configuration
"""

import os
from typing import List, Optional


class Settings:
    """Application configuration class"""
    
    def __init__(self):
        # Basic settings
        self.app_name = "Casino-Club F2P API"
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # Security settings
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret-key")
        self.algorithm = "HS256"
        self.jwt_algorithm = "HS256"
        self.jwt_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
        
        # Database settings
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
        
        # Kafka settings (optional)
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        
        # Game settings
        self.max_daily_rewards = 5
        self.initial_cyber_tokens = int(os.getenv("INITIAL_CYBER_TOKENS", "200"))


# Global settings instance
settings = Settings()


def get_settings():
    """Return settings instance"""
    return settings


def is_development():
    """Check if development environment"""
    return settings.environment == "development"
