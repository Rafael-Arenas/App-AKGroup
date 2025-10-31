"""
Configuración para servicios API del frontend.

Este módulo centraliza la configuración de los servicios API
para facilitar cambios de entorno (desarrollo, producción, etc.).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """
    Configuración de servicios API.

    Atributos:
        backend_base_url: URL base del backend FastAPI
        api_timeout: Timeout en segundos para peticiones HTTP
        api_max_retries: Número máximo de reintentos para errores de red
        api_version: Versión de la API
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="API_",
        case_sensitive=False,
    )

    backend_base_url: str = "http://localhost:8000"
    api_timeout: float = 30.0
    api_max_retries: int = 3
    api_version: str = "v1"

    @property
    def full_api_url(self) -> str:
        """
        Retorna la URL completa de la API.

        Returns:
            URL completa incluyendo versión (ej: http://localhost:8000/api/v1)

        Example:
            >>> settings = APISettings()
            >>> print(settings.full_api_url)
            http://localhost:8000/api/v1
        """
        return f"{self.backend_base_url.rstrip('/')}/api/{self.api_version}"


# Instancia global de configuración
api_settings = APISettings()


# Para facilitar imports
__all__ = ["APISettings", "api_settings"]
