"""
Configuration management for the healthcare AI service.

Uses pydantic-settings for type-safe configuration with
environment variable support.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
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
    app_version: str = "0.7.0"
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
    
    # LLM settings (Post 2)
    anthropic_api_key: Optional[str] = None
    llm_enabled: bool = False  # Feature flag for LLM functionality
    llm_model: str = "claude-3-5-sonnet-20241022"
    llm_max_tokens: int = 1024
    llm_temperature: float = 0.3
    llm_timeout: float = 30.0
    llm_max_retries: int = 2

    # Shadow mode settings (Post 6)
    shadow_mode_enabled: bool = False
    shadow_write_results: bool = True
    shadow_results_dir: str = "shadow_results"
    shadow_similarity_threshold: float = 0.35
    shadow_alert_similarity_threshold: float = 0.25
    shadow_promotion_min_requests: int = 5
    shadow_promotion_min_avg_similarity: float = 0.55
    shadow_promotion_max_divergence_rate: float = 0.20
    shadow_candidate_model: str = "claude-3-5-sonnet-20241022"
    shadow_candidate_temperature: float = 0.2
    shadow_candidate_prompt_version: Optional[str] = None
    shadow_promote_full_threshold: float = 0.90
    shadow_promote_broad_threshold: float = 0.80
    shadow_promote_limited_threshold: float = 0.70

    # HAPI FHIR settings for clinical examples (Post 6)
    hapi_fhir_base_url: Optional[str] = None
    hapi_fhir_timeout_seconds: int = 10

    # Monitoring settings (Post 7)
    monitoring_enabled: bool = True
    monitoring_window_size: int = 20
    monitoring_min_runs_for_actions: int = 5
    monitoring_max_divergence_rate: float = 0.30
    monitoring_max_critical_alert_rate: float = 0.10
    monitoring_max_avg_shadow_latency_ms: float = 3000.0
    monitoring_max_avg_shadow_cost_usd: float = 0.02
    monitoring_action_ttl_minutes: int = 30
    monitoring_state_file: str = "monitoring_state.json"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug_value(cls, value):
        """Accept common deployment strings for debug mode."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production"}:
                return False
            if normalized in {"dev", "development"}:
                return True
        return value
    
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
