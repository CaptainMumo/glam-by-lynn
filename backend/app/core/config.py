"""
Application configuration using Pydantic Settings
"""
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Any
import secrets


class Settings(BaseSettings):
    """Application settings with validation"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Application
    APP_NAME: str = "Glam by Lynn API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"  # Default to SQLite for testing
    DATABASE_URL_ASYNC: str = "sqlite+aiosqlite:///./app.db"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/api/auth/callback/google"

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = ""

    # Email
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@glambylynn.com"

    # Admin
    ADMIN_EMAILS: List[str] = []

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Validate SECRET_KEY is secure in production."""
        # Get ENVIRONMENT from values (it's already been set)
        environment = info.data.get("ENVIRONMENT", "development")

        if environment == "production":
            # In production, SECRET_KEY must be at least 32 characters
            if len(v) < 32:
                raise ValueError(
                    "SECRET_KEY must be at least 32 characters in production"
                )
            # Must not be the default development key
            if v == "dev-secret-key-change-in-production":
                raise ValueError(
                    "SECRET_KEY must be changed from default value in production"
                )
        return v

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str, info) -> str:
        """Validate DATABASE_URL is set properly."""
        environment = info.data.get("ENVIRONMENT", "development")

        if environment == "production" and "sqlite" in v.lower():
            raise ValueError(
                "SQLite database should not be used in production. "
                "Use PostgreSQL or another production database."
            )
        return v

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def validate_allowed_origins(cls, v: List[str]) -> List[str]:
        """Ensure ALLOWED_ORIGINS is properly configured."""
        if not v:
            raise ValueError("ALLOWED_ORIGINS must contain at least one origin")
        # Validate format
        for origin in v:
            if not origin.startswith(("http://", "https://")):
                raise ValueError(
                    f"Invalid origin format: {origin}. Must start with http:// or https://"
                )
        return v

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        """Validate all production-critical settings."""
        if self.ENVIRONMENT == "production":
            # Ensure Google OAuth is configured
            if not self.GOOGLE_CLIENT_ID or not self.GOOGLE_CLIENT_SECRET:
                raise ValueError(
                    "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in production"
                )

            # Ensure database is configured
            if not self.DATABASE_URL or self.DATABASE_URL == "sqlite:///./app.db":
                raise ValueError(
                    "DATABASE_URL must be properly configured in production"
                )

            # Debug mode should be off in production
            if self.DEBUG:
                raise ValueError(
                    "DEBUG should be set to False in production for security"
                )

        return self

    def get_safe_config(self) -> dict:
        """
        Get configuration dict with sensitive values masked.

        Useful for logging or displaying config without exposing secrets.
        """
        config = self.model_dump()

        # Sensitive keys to mask
        sensitive_keys = [
            "SECRET_KEY",
            "DATABASE_URL",
            "DATABASE_URL_ASYNC",
            "GOOGLE_CLIENT_SECRET",
            "AWS_SECRET_ACCESS_KEY",
            "RESEND_API_KEY",
        ]

        # Mask sensitive values
        for key in sensitive_keys:
            if key in config and config[key]:
                # Show first 4 chars and mask the rest
                value = str(config[key])
                if len(value) > 4:
                    config[key] = value[:4] + "*" * (len(value) - 4)
                else:
                    config[key] = "*" * len(value)

        return config


settings = Settings()
