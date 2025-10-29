"""
Configuración del frontend Flet.

Configuración centralizada para el cliente frontend,
incluyendo URLs de API, timeouts, y configuraciones de UI.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class FrontendSettings(BaseSettings):
    """
    Configuración del frontend Flet.

    Atributos:
        api_base_url: URL base del backend API
        api_version: Versión de la API
        api_timeout: Timeout para requests HTTP (segundos)
        app_title: Título de la aplicación
        app_window_width: Ancho de la ventana
        app_window_height: Alto de la ventana
        app_theme_mode: Modo de tema (light/dark/system)
    """

    # API Configuration
    api_base_url: str = "http://localhost:8000"
    api_version: str = "v1"
    api_timeout: int = 30

    # Application Configuration
    app_title: str = "AK Group - Sistema de Gestion"
    app_window_width: int = 1280
    app_window_height: int = 800
    app_theme_mode: str = "light"

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # UI Configuration
    primary_color: str = "blue"
    accent_color: str = "amber"

    model_config = SettingsConfigDict(
        env_prefix="FRONTEND_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def api_url(self) -> str:
        """URL completa de la API."""
        return f"{self.api_base_url}/api/{self.api_version}"


# Instancia global de configuración
frontend_settings = FrontendSettings()
