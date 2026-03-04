"""
Configuration management for SatyaSetu
Centralized settings with environment variable support
"""

import os
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # CORS Settings
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # External Service APIs
    OPENAI_API_KEY: Optional[str] = None
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    ELEVENLABS_API_KEY: Optional[str] = None
    
    # AWS Configuration (for Transcribe, Polly, Textract)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-south-1"  # Mumbai region - best for India
    AWS_S3_BUCKET: Optional[str] = None
    
    # AWS Service Preferences
    PREFERRED_STT: str = "openai"  # "aws" or "openai"
    PREFERRED_TTS: str = "openai"  # "aws" or "openai"
    PREFERRED_OCR: str = "aws"     # "aws" or "openai"
    
    # Database & Cache
    REDIS_URL: str = "redis://localhost:6379"
    VECTOR_DB_INDEX: str = "satyasetu-rural-cybersecurity"
    
    # AI Model Settings
    DEFAULT_LANGUAGE: str = "hi"  # Hindi
    MAX_RESPONSE_LENGTH: int = 500
    PROCESSING_TIMEOUT: int = 30
    
    # Security
    RATE_LIMIT_PER_MINUTE: int = 60
    MAX_AUDIO_SIZE_MB: int = 10
    
    # Telemetry
    MAX_TELEMETRY_EVENTS: int = 1000
    TELEMETRY_RETENTION_HOURS: int = 24
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "prod", "production", ""}:
                return False
        return value

# Global settings instance
settings = Settings()
