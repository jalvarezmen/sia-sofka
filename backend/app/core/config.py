"""Configuration settings for the application."""

import warnings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str
    database_url_sync: str

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key strength (warning only, not blocking).
        
        This validator checks if the SECRET_KEY meets minimum security
        requirements but only issues a warning if it doesn't, allowing
        the application to start. This prevents breaking existing setups
        while encouraging better security practices.
        """
        if len(v) < 32:
            warnings.warn(
                f"SECRET_KEY is too short ({len(v)} characters). "
                "Minimum 32 characters recommended for production security. "
                "This may cause security issues in production environments.",
                UserWarning,
                stacklevel=2
            )
        return v

    # Application
    app_name: str = "SIA SOFKA U"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()


