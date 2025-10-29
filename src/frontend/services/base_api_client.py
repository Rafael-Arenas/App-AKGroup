"""
Cliente HTTP base para comunicación con la API Backend.

Proporciona funcionalidad común para todos los clientes API usando httpx.
"""

from typing import Any, TypeVar, Generic
from loguru import logger
import httpx

from src.frontend.config.settings import settings


T = TypeVar("T")


class APIException(Exception):
    """Excepción base para errores de API."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Inicializa excepción de API.

        Args:
            message: Mensaje de error
            status_code: Código HTTP de error
            details: Detalles adicionales del error
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class BaseAPIClient:
    """
    Cliente HTTP base para comunicación con el backend.

    Proporciona métodos comunes para hacer requests HTTP con manejo
    de errores, timeouts, y logging.

    Example:
        class CompanyAPI(BaseAPIClient):
            def __init__(self):
                super().__init__(base_path="/api/v1")

            def get_all(self) -> list[CompanyResponse]:
                response = self.get("/companies")
                return [CompanyResponse(**item) for item in response]
    """

    def __init__(self, base_path: str = "/api/v1") -> None:
        """
        Inicializa el cliente API.

        Args:
            base_path: Path base para todos los endpoints (ej: /api/v1)
        """
        self.base_url = settings.api_url
        self.base_path = base_path
        self.timeout = settings.api_timeout

        # Crear cliente httpx con configuración común
        self.client = httpx.Client(
            base_url=f"{self.base_url}{self.base_path}",
            timeout=self.timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        logger.debug(
            f"Initialized API client for {self.base_url}{self.base_path}"
        )

    def _handle_response(self, response: httpx.Response) -> Any:
        """
        Maneja la respuesta HTTP y convierte errores a excepciones.

        Args:
            response: Respuesta HTTP de httpx

        Returns:
            JSON deserializado de la respuesta

        Raises:
            APIException: Si la respuesta indica error
        """
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Intentar obtener detalles del error del response
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = {"detail": e.response.text}

            logger.error(
                f"API error {e.response.status_code}: {error_detail}"
            )

            raise APIException(
                message=error_detail.get("message", str(e)),
                status_code=e.response.status_code,
                details=error_detail,
            ) from e

        except httpx.TimeoutException as e:
            logger.error(f"API timeout: {e}")
            raise APIException(
                message="Request timeout - el servidor no respondió a tiempo",
                details={"timeout": self.timeout},
            ) from e

        except httpx.RequestError as e:
            logger.error(f"API request error: {e}")
            raise APIException(
                message="Error de conexión con el servidor",
                details={"error": str(e)},
            ) from e

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """
        Realiza una petición GET.

        Args:
            path: Path del endpoint (ej: /companies)
            params: Query parameters opcionales

        Returns:
            JSON deserializado de la respuesta

        Raises:
            APIException: Si hay error en la petición

        Example:
            data = client.get("/companies", params={"limit": 10})
        """
        logger.debug(f"GET {path} with params {params}")
        response = self.client.get(path, params=params)
        return self._handle_response(response)

    def post(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        """
        Realiza una petición POST.

        Args:
            path: Path del endpoint
            data: Form data (form-encoded)
            json: JSON data (JSON-encoded)

        Returns:
            JSON deserializado de la respuesta

        Raises:
            APIException: Si hay error en la petición

        Example:
            result = client.post("/companies", json={"name": "Test"})
        """
        logger.debug(f"POST {path}")
        response = self.client.post(path, data=data, json=json)
        return self._handle_response(response)

    def put(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        """
        Realiza una petición PUT.

        Args:
            path: Path del endpoint
            data: Form data
            json: JSON data

        Returns:
            JSON deserializado de la respuesta

        Raises:
            APIException: Si hay error en la petición

        Example:
            result = client.put("/companies/1", json={"name": "Updated"})
        """
        logger.debug(f"PUT {path}")
        response = self.client.put(path, data=data, json=json)
        return self._handle_response(response)

    def patch(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        """
        Realiza una petición PATCH.

        Args:
            path: Path del endpoint
            data: Form data
            json: JSON data

        Returns:
            JSON deserializado de la respuesta

        Raises:
            APIException: Si hay error en la petición

        Example:
            result = client.patch("/companies/1", json={"phone": "+123"})
        """
        logger.debug(f"PATCH {path}")
        response = self.client.patch(path, data=data, json=json)
        return self._handle_response(response)

    def delete(self, path: str) -> Any:
        """
        Realiza una petición DELETE.

        Args:
            path: Path del endpoint

        Returns:
            JSON deserializado de la respuesta

        Raises:
            APIException: Si hay error en la petición

        Example:
            client.delete("/companies/1")
        """
        logger.debug(f"DELETE {path}")
        response = self.client.delete(path)
        return self._handle_response(response)

    def close(self) -> None:
        """
        Cierra el cliente HTTP.

        Debe llamarse al finalizar para liberar recursos.

        Example:
            client.close()
        """
        self.client.close()
        logger.debug("API client closed")

    def __enter__(self) -> "BaseAPIClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit - cierra el cliente."""
        self.close()
