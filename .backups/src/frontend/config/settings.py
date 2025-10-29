"""
Configuración del Frontend Flet.

Maneja la configuración de la aplicación frontend usando pydantic-settings
para cargar variables de entorno.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class FrontendSettings(BaseSettings):
    """
    Configuración del frontend Flet.

    Lee variables de entorno con prefijo FRONTEND_ o usa valores por defecto.

    Example:
        settings = FrontendSettings()
        print(settings.api_url)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    api_url: str = "http://127.0.0.1:8000"
    api_timeout: int = 30

    # App Configuration
    app_title: str = "AK Group - Sistema de Gestión"
    app_width: int = 1280
    app_height: int = 800

    # UI Theme
    ui_theme: str = "light"  # light, dark, auto
    primary_color: str = "#2196F3"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/frontend.log"


# Instancia global de settings
settings = FrontendSettings()
