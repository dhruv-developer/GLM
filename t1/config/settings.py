"""
Configuration Settings for ZIEL-MAS
"""

import os
import json
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "ZIEL-MAS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"

    # CORS - Made optional with default and custom parsing
    ALLOWED_ORIGINS: str = '["http://localhost:3000", "http://localhost:8000"]'

    # Database
    MONGODB_URI: str = "mongodb://localhost:27017"
    REDIS_URI: str = "redis://localhost:6379/0"

    # Security
    JWT_SECRET: str = "your-super-secret-jwt-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 86400  # 24 hours
    ENCRYPTION_KEY: str = "your-32-byte-encryption-key-here"

    # GLM API
    GLM_API_KEY: str = ""
    GLM_API_URL: str = "https://api.glm.ai/v1"

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # WhatsApp (Twilio)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""

    # Execution
    MAX_EXECUTION_TIME: int = 3600  # 1 hour
    MAX_RETRIES: int = 3
    RETRY_BACKOFF: int = 2

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/ziel_mas.log"

    # Monitoring
    ENABLE_AUDIT_LOGS: bool = True
    METRICS_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env file

    def get_allowed_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from JSON string"""
        try:
            if isinstance(self.ALLOWED_ORIGINS, list):
                return self.ALLOWED_ORIGINS
            return json.loads(self.ALLOWED_ORIGINS)
        except (json.JSONDecodeError, TypeError):
            return ["http://localhost:3000", "http://localhost:8000"]


# Global settings instance
settings = Settings()
