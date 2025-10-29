"""
Cliente HTTP base para comunicación con el backend.

Proporciona funcionalidad común para todos los clientes API,
incluyendo manejo de errores, timeouts, y logging.
"""

from typing import Any

import httpx
from loguru import logger

from src.frontend.config.settings import frontend_settings


class BaseAPIClient:
    """
    Cliente HTTP base para comunicación con el backend API.

    Proporciona métodos genéricos para realizar requests HTTP
    con manejo consistente de errores y configuración.

    Attributes:
        base_url: URL base de la API
        timeout: Timeout para requests HTTP
    """

    def __init__(self, base_url: str | None = None, timeout: int | None = None):
        """
        Inicializa el cliente API.

        Args:
            base_url: URL base de la API (usa config si no se especifica)
            timeout: Timeout para requests (usa config si no se especifica)
        """
        self.base_url = base_url or frontend_settings.api_url
        self.timeout = timeout or frontend_settings.api_timeout

    def _get_headers(self) -> dict[str, str]:
        """
        Obtiene los headers HTTP por defecto.

        Returns:
            Diccionario con headers HTTP
        """
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def get(self, endpoint: str, params: dict[str, Any] | None = None) -> Any:
        """
        Realiza un GET request.

        Args:
            endpoint: Endpoint de la API (ej: /companies)
            params: Parámetros query string

        Returns:
            Respuesta JSON deserializada

        Raises:
            httpx.HTTPError: Si ocurre un error HTTP
        """
        url = f"{self.base_url}{endpoint}"

        try:
            logger.debug(f"GET {url} params={params}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                data = response.json()

                logger.debug(f"GET {url} -> {response.status_code}")
                return data

        except httpx.HTTPError as e:
            logger.error(f"GET {url} failed: {e}")
            raise

    async def post(
        self, endpoint: str, data: dict[str, Any] | None = None
    ) -> Any:
        """
        Realiza un POST request.

        Args:
            endpoint: Endpoint de la API
            data: Datos a enviar en el body

        Returns:
            Respuesta JSON deserializada

        Raises:
            httpx.HTTPError: Si ocurre un error HTTP
        """
        url = f"{self.base_url}{endpoint}"

        try:
            logger.debug(f"POST {url}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=data,
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                result = response.json()

                logger.debug(f"POST {url} -> {response.status_code}")
                return result

        except httpx.HTTPError as e:
            logger.error(f"POST {url} failed: {e}")
            raise

    async def put(
        self, endpoint: str, data: dict[str, Any] | None = None
    ) -> Any:
        """
        Realiza un PUT request.

        Args:
            endpoint: Endpoint de la API
            data: Datos a enviar en el body

        Returns:
            Respuesta JSON deserializada

        Raises:
            httpx.HTTPError: Si ocurre un error HTTP
        """
        url = f"{self.base_url}{endpoint}"

        try:
            logger.debug(f"PUT {url}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.put(
                    url,
                    json=data,
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                result = response.json()

                logger.debug(f"PUT {url} -> {response.status_code}")
                return result

        except httpx.HTTPError as e:
            logger.error(f"PUT {url} failed: {e}")
            raise

    async def delete(self, endpoint: str) -> Any:
        """
        Realiza un DELETE request.

        Args:
            endpoint: Endpoint de la API

        Returns:
            Respuesta JSON deserializada

        Raises:
            httpx.HTTPError: Si ocurre un error HTTP
        """
        url = f"{self.base_url}{endpoint}"

        try:
            logger.debug(f"DELETE {url}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.delete(
                    url,
                    headers=self._get_headers(),
                )
                response.raise_for_status()
                result = response.json()

                logger.debug(f"DELETE {url} -> {response.status_code}")
                return result

        except httpx.HTTPError as e:
            logger.error(f"DELETE {url} failed: {e}")
            raise
