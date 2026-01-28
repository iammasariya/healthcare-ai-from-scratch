"""
Configuration management for the healthcare AI service.

Uses pydantic-settings for type-safe configuration with
environment variable support.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import logging


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    All settings can be overridden via environment variables.
    For production, use .env file or actual environment variables.
    """
    
    # Application settings
    app_name: str = "Healthcare AI Service"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = ""
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "json"  # json or text
    log_file: Optional[str] = None
    
    # Security settings
    cors_origins: list[str] = ["http://localhost:3000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET", "POST"]
    cors_allow_headers: list[str] = ["*"]
    
    # Request settings
    max_note_length: int = 10000
    request_timeout: int = 30
    
    # Privacy settings
    log_payload_preview_length: int = 100
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    def get_log_level(self) -> int:
        """Convert string log level to logging constant."""
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return levels.get(self.log_level.upper(), logging.INFO)


# Global settings instance
settings = Settings()
