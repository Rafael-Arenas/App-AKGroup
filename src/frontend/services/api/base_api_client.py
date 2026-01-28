"""
Cliente HTTP base para comunicación con el backend FastAPI.

Este módulo proporciona un cliente HTTP asíncrono base con manejo de errores,
logging, reintentos automáticos y excepciones personalizadas.
"""

from typing import Any, Optional
import httpx
from loguru import logger
import asyncio


# Excepciones personalizadas
class APIException(Exception):
    """Excepción base para errores de API."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Inicializa la excepción de API.

        Args:
            message: Mensaje de error descriptivo
            status_code: Código de estado HTTP (si aplica)
            details: Detalles adicionales del error

        Example:
            >>> raise APIException("Error de conexión", status_code=500)
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Representación en string de la excepción."""
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class NetworkException(APIException):
    """Excepción para errores de red/conexión."""

    def __init__(self, message: str = "Error de red o conexión", **kwargs: Any) -> None:
        """
        Inicializa la excepción de red.

        Args:
            message: Mensaje de error
            **kwargs: Argumentos adicionales para APIException
        """
        super().__init__(message, **kwargs)


class ValidationException(APIException):
    """Excepción para errores de validación (422)."""

    def __init__(
        self,
        message: str = "Error de validación",
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Inicializa la excepción de validación.

        Args:
            message: Mensaje de error
            details: Detalles de validación del servidor
        """
        super().__init__(message, status_code=422, details=details or {})


class NotFoundException(APIException):
    """Excepción para recursos no encontrados (404)."""

    def __init__(self, message: str = "Recurso no encontrado") -> None:
        """
        Inicializa la excepción de recurso no encontrado.

        Args:
            message: Mensaje de error
        """
        super().__init__(message, status_code=404)


class UnauthorizedException(APIException):
    """Excepción para errores de autorización (401)."""

    def __init__(self, message: str = "No autorizado") -> None:
        """
        Inicializa la excepción de no autorizado.

        Args:
            message: Mensaje de error
        """
        super().__init__(message, status_code=401)


class BaseAPIClient:
    """
    Cliente HTTP base para interactuar con el backend FastAPI.

    Proporciona métodos para realizar peticiones HTTP con manejo de errores,
    logging automático, reintentos y timeout configurable.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        """
        Inicializa el cliente API base.

        Args:
            base_url: URL base del backend
            timeout: Timeout en segundos para las peticiones (default: 30s)
            max_retries: Número máximo de reintentos para errores de red (default: 3)

        Example:
            >>> client = BaseAPIClient(base_url="http://localhost:8000/api/v1")
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Optional[httpx.AsyncClient] = None

        logger.info(
            "Cliente API inicializado | base_url={} timeout={}s max_retries={}",
            self.base_url,
            self.timeout,
            self.max_retries,
        )

    async def _get_client(self) -> httpx.AsyncClient:
        """
        Obtiene o crea el cliente HTTP asíncrono.

        Returns:
            Cliente HTTP asíncrono configurado

        Example:
            >>> client = await self._get_client()
        """
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout),
                headers={"Content-Type": "application/json"},
            )
        return self._client

    async def close(self) -> None:
        """
        Cierra el cliente HTTP y libera recursos.

        Example:
            >>> await client.close()
        """
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            logger.debug("Cliente HTTP cerrado")

    async def _handle_response(self, response: httpx.Response) -> Any:
        """
        Procesa la respuesta HTTP y maneja errores.

        Args:
            response: Respuesta HTTP del servidor

        Returns:
            Datos JSON de la respuesta

        Raises:
            UnauthorizedException: Si el código de estado es 401
            NotFoundException: Si el código de estado es 404
            ValidationException: Si el código de estado es 422
            APIException: Para otros códigos de error

        Example:
            >>> data = await self._handle_response(response)
        """
        try:
            # Log de la respuesta
            logger.debug(
                "Respuesta recibida | status={} url={}",
                response.status_code,
                response.url,
            )

            # Verificar errores HTTP
            if response.status_code >= 400:
                error_data = {}
                try:
                    error_data = response.json()
                    # Debug: Log raw response for 422 and 500 errors
                    if response.status_code in [422, 500]:
                        logger.debug(
                            "Raw {} response data: {}",
                            response.status_code,
                            error_data
                        )
                except Exception:
                    error_data = {"error": "unknown", "message": response.text}

                # FastAPI validation errors come in "detail" field
                if "detail" in error_data:
                    if isinstance(error_data["detail"], list):
                        # Parse FastAPI validation errors list
                        error_messages = []
                        for item in error_data["detail"]:
                            if isinstance(item, dict) and "msg" in item:
                                loc = " -> ".join(str(x) for x in item.get("loc", []))
                                error_messages.append(f"{loc}: {item['msg']}" if loc else item['msg'])
                        error_message = "\n".join(error_messages) if error_messages else "Error de validación"
                        error_details = {"validation_errors": error_data["detail"]}
                    else:
                        # Single detail message
                        error_message = str(error_data["detail"])
                        error_details = error_data
                else:
                    error_message = error_data.get("message", "Error desconocido")
                    error_details = error_data.get("details", {})

                # Mapear códigos de estado a excepciones
                if response.status_code == 401:
                    raise UnauthorizedException(error_message)
                elif response.status_code == 404:
                    raise NotFoundException(error_message)
                elif response.status_code == 422:
                    raise ValidationException(error_message, details=error_details)
                else:
                    raise APIException(
                        error_message,
                        status_code=response.status_code,
                        details=error_details,
                    )

            # Retornar datos JSON
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(
                "Error HTTP | status={} url={}", e.response.status_code, e.request.url
            )
            raise APIException(
                f"Error HTTP {e.response.status_code}",
                status_code=e.response.status_code,
            )

    async def _request_with_retry(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> Any:
        """
        Realiza una petición HTTP con lógica de reintentos.

        Args:
            method: Método HTTP (GET, POST, PUT, PATCH, DELETE)
            endpoint: Endpoint de la API (sin base_url)
            **kwargs: Argumentos adicionales para httpx.request

        Returns:
            Datos JSON de la respuesta

        Raises:
            NetworkException: Si se agotan los reintentos
            APIException: Para otros errores de API

        Example:
            >>> data = await self._request_with_retry("GET", "/companies")
        """
        client = await self._get_client()
        url = f"{endpoint}" if endpoint.startswith("/") else f"/{endpoint}"

        last_exception: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(
                    "Petición HTTP | method={} url={} attempt={}/{}",
                    method,
                    url,
                    attempt,
                    self.max_retries,
                )

                response = await client.request(method, url, **kwargs)
                return await self._handle_response(response)

            except (
                httpx.ConnectError,
                httpx.TimeoutException,
                httpx.NetworkError,
            ) as e:
                last_exception = e
                logger.warning(
                    "Error de red | method={} url={} attempt={}/{} error={}",
                    method,
                    url,
                    attempt,
                    self.max_retries,
                    str(e),
                )

                # Si no es el último intento, esperar antes de reintentar
                if attempt < self.max_retries:
                    wait_time = 2**attempt  # Backoff exponencial: 2s, 4s, 8s
                    logger.debug("Reintentando en {} segundos...", wait_time)
                    await asyncio.sleep(wait_time)
                    continue

                # Último intento fallido
                raise NetworkException(
                    f"Error de red después de {self.max_retries} intentos: {str(e)}"
                )

            except (
                UnauthorizedException,
                NotFoundException,
                ValidationException,
                APIException,
            ):
                # No reintentar errores de API conocidos
                raise

            except Exception as e:
                logger.exception(
                    "Error inesperado en petición HTTP | method={} url={}", method, url
                )
                raise APIException(f"Error inesperado: {str(e)}")

        # No debería llegar aquí, pero por seguridad
        if last_exception:
            raise NetworkException(
                f"Error de red después de {self.max_retries} intentos: {str(last_exception)}"
            )
        raise APIException("Error desconocido en petición HTTP")

    async def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Realiza una petición GET.

        Args:
            endpoint: Endpoint de la API
            params: Parámetros de query string

        Returns:
            Datos JSON de la respuesta

        Raises:
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> companies = await client.get("/companies", params={"skip": 0, "limit": 10})
        """
        logger.info("GET request | endpoint={} params={}", endpoint, params)
        return await self._request_with_retry("GET", endpoint, params=params)

    async def post(
        self,
        endpoint: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Realiza una petición POST.

        Args:
            endpoint: Endpoint de la API
            json: Datos JSON a enviar en el body

        Returns:
            Datos JSON de la respuesta

        Raises:
            NetworkException: Error de red/conexión
            ValidationException: Error de validación (422)
            APIException: Error de API

        Example:
            >>> company = await client.post("/companies", json={"name": "AK Group"})
        """
        logger.info("POST request | endpoint={} json={}", endpoint, json)
        return await self._request_with_retry("POST", endpoint, json=json)

    async def put(
        self,
        endpoint: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Realiza una petición PUT.

        Args:
            endpoint: Endpoint de la API
            json: Datos JSON a enviar en el body

        Returns:
            Datos JSON de la respuesta

        Raises:
            NetworkException: Error de red/conexión
            ValidationException: Error de validación (422)
            NotFoundException: Recurso no encontrado (404)
            APIException: Error de API

        Example:
            >>> company = await client.put("/companies/1", json={"name": "Updated Name"})
        """
        logger.info("PUT request | endpoint={} json={}", endpoint, json)
        return await self._request_with_retry("PUT", endpoint, json=json)

    async def patch(
        self,
        endpoint: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Any:
        """
        Realiza una petición PATCH.

        Args:
            endpoint: Endpoint de la API
            json: Datos JSON a enviar en el body

        Returns:
            Datos JSON de la respuesta

        Raises:
            NetworkException: Error de red/conexión
            ValidationException: Error de validación (422)
            NotFoundException: Recurso no encontrado (404)
            APIException: Error de API

        Example:
            >>> company = await client.patch("/companies/1", json={"is_active": False})
        """
        logger.info("PATCH request | endpoint={} json={}", endpoint, json)
        return await self._request_with_retry("PATCH", endpoint, json=json)

    async def delete(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
    ) -> bool:
        """
        Realiza una petición DELETE.

        Args:
            endpoint: Endpoint de la API
            params: Parámetros de query string (opcional)

        Returns:
            True si la eliminación fue exitosa

        Raises:
            NetworkException: Error de red/conexión
            NotFoundException: Recurso no encontrado (404)
            APIException: Error de API

        Example:
            >>> success = await client.delete("/companies/1")
        """
        logger.info("DELETE request | endpoint={} params={}", endpoint, params)
        await self._request_with_retry("DELETE", endpoint, params=params)
        return True

    async def __aenter__(self) -> "BaseAPIClient":
        """Context manager entry."""
        await self._get_client()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        await self.close()
