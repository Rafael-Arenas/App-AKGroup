"""
Application settings using Pydantic Settings.

Settings are loaded from environment variables with defaults.
Create a .env file in the project root to override defaults.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    All settings can be overridden via environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "AK Group API"
    app_version: str = "1.0.0"
    environment: Literal["development", "production"] = "development"
    debug: bool = False

    # Database
    database_type: Literal["sqlite", "mysql"] = "sqlite"
    database_echo: bool = False

    # SQLite settings
    sqlite_path: str = "app_akgroup.db"

    # MySQL settings
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "akgroup_user"
    mysql_password: str = "password"
    mysql_database: str = "akgroup_db"
    mysql_pool_size: int = 5
    mysql_max_overflow: int = 10
    mysql_pool_recycle: int = 3600
    mysql_connect_timeout: int = 10

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/akgroup.log"
    log_rotation: str = "500 MB"
    log_retention: str = "10 days"

    # Business defaults
    default_currency: str = "CLP"
    default_tax_rate: float = 19.0
    default_pagination_limit: int = 100
    max_pagination_limit: int = 1000

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    api_prefix: str = "/api/v1"
    api_title: str = "AK Group API"
    api_description: str = "Business management system API"

    # CORS settings
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # JWT settings
    jwt_secret_key: str = "change-this-secret-key-in-production-min-32-characters"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 8

    @property
    def database_url(self) -> str:
        """
        Get database URL based on database type.

        Returns:
            str: SQLAlchemy database URL
        """
        if self.database_type == "sqlite":
            return f"sqlite:///{self.sqlite_path}"
        elif self.database_type == "mysql":
            return (
                f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
                f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
            )
        else:
            raise ValueError(f"Unsupported database type: {self.database_type}")


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings

    Note:
        Settings are cached to avoid reading .env file multiple times.
    """
    return Settings()


# Global settings instance
settings = get_settings()
