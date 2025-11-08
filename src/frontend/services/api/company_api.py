"""
Servicio API para gestión de Companies (Empresas).

Este módulo proporciona métodos para interactuar con los endpoints de empresas
del backend FastAPI.
"""

from typing import Any
from loguru import logger

from .base_api_client import BaseAPIClient


class CompanyAPIService:
    """
    Servicio para operaciones CRUD de Companies.

    Proporciona métodos asíncronos para listar, crear, actualizar, eliminar
    y buscar empresas en el backend.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
    ) -> None:
        """
        Inicializa el servicio de Company API.

        Args:
            base_url: URL base del backend
            timeout: Timeout en segundos para las peticiones

        Example:
            >>> service = CompanyAPIService()
        """
        self._client = BaseAPIClient(base_url=base_url, timeout=timeout)
        logger.debug("CompanyAPIService inicializado | base_url={}", base_url)

    async def get_all(
        self,
        skip: int | None = None,
        limit: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        **filters: Any,
    ) -> dict[str, Any]:
        """
        Obtiene todas las empresas con paginación.

        Args:
            skip: Número de registros a omitir
            limit: Número máximo de registros a retornar
            page: Número de página (1-indexed, alternativa a skip)
            page_size: Tamaño de página (alternativa a limit)
            **filters: Filtros adicionales (is_active, company_type, etc.)

        Returns:
            Diccionario con 'items' (lista de empresas) y 'total' (total de registros)

        Raises:
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> result = await service.get_all(page=1, page_size=20)
            >>> print(f"Total empresas: {result['total']}")
        """
        # Convertir page/page_size a skip/limit si se proporcionan
        if page is not None and page_size is not None:
            skip = (page - 1) * page_size
            limit = page_size
        elif skip is None:
            skip = 0
        if limit is None:
            limit = 100

        logger.info("Obteniendo todas las empresas | skip={} limit={} filters={}", skip, limit, filters)

        try:
            # Preparar parámetros de consulta
            params = {"skip": skip, "limit": limit}
            params.update(filters)

            companies = await self._client.get("/companies/", params=params)

            # Retornar en formato esperado por las vistas
            result = {
                "items": companies if isinstance(companies, list) else [],
                "total": len(companies) if isinstance(companies, list) else 0,
            }

            logger.success("Empresas obtenidas exitosamente | total={}", result["total"])
            return result

        except Exception as e:
            logger.error("Error al obtener empresas | error={}", str(e))
            raise

    async def get_by_id(self, company_id: int) -> dict[str, Any]:
        """
        Obtiene una empresa por su ID.

        Args:
            company_id: ID de la empresa

        Returns:
            Datos de la empresa en formato diccionario

        Raises:
            NotFoundException: Si la empresa no existe
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> company = await service.get_by_id(1)
            >>> print(f"Empresa: {company['name']}")
        """
        logger.info("Obteniendo empresa por ID | company_id={}", company_id)

        try:
            company = await self._client.get(f"/companies/{company_id}")

            logger.success(
                "Empresa obtenida exitosamente | id={} name={}",
                company_id,
                company.get("name"),
            )
            return company

        except Exception as e:
            logger.error(
                "Error al obtener empresa | company_id={} error={}", company_id, str(e)
            )
            raise

    async def search(
        self,
        query: str,
        page: int | None = None,
        page_size: int | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """
        Busca empresas por nombre o trigrama (búsqueda parcial).

        Args:
            query: Texto de búsqueda (nombre o trigrama)
            page: Número de página (1-indexed)
            page_size: Tamaño de página
            **params: Parámetros adicionales

        Returns:
            Diccionario con 'items' (lista de empresas) y 'total' (total de registros)

        Raises:
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> result = await service.search("AK", page=1, page_size=20)
            >>> for company in result['items']:
            ...     print(company["name"])
        """
        # Convertir page/page_size a skip/limit
        skip = 0
        limit = 100
        if page is not None and page_size is not None:
            skip = (page - 1) * page_size
            limit = page_size

        logger.info("Buscando empresas | query={} skip={} limit={}", query, skip, limit)

        try:
            # Preparar parámetros
            search_params = {"skip": skip, "limit": limit}
            search_params.update(params)

            companies = await self._client.get(
                f"/companies/search/{query}",
                params=search_params,
            )

            # Retornar en formato esperado
            result = {
                "items": companies if isinstance(companies, list) else [],
                "total": len(companies) if isinstance(companies, list) else 0,
            }

            logger.success(
                "Búsqueda completada | query={} results={}", query, result["total"]
            )
            return result

        except Exception as e:
            logger.error("Error al buscar empresas | query={} error={}", query, str(e))
            raise

    async def get_active(self) -> list[dict[str, Any]]:
        """
        Obtiene todas las empresas activas.

        Returns:
            Lista de empresas activas

        Raises:
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> active_companies = await service.get_active()
            >>> print(f"Empresas activas: {len(active_companies)}")
        """
        logger.info("Obteniendo empresas activas")

        try:
            companies = await self._client.get("/companies/active")

            logger.success("Empresas activas obtenidas | total={}", len(companies))
            return companies

        except Exception as e:
            logger.error("Error al obtener empresas activas | error={}", str(e))
            raise

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Crea una nueva empresa.

        Args:
            data: Datos de la empresa a crear. Debe incluir:
                - name: str (requerido)
                - company_type_id: int (requerido)
                - country_id: int (requerido)
                - nit: str (opcional)
                - email: str (opcional)
                - phone: str (opcional)
                - address: str (opcional)
                - is_active: bool (opcional, default: True)

        Returns:
            Datos de la empresa creada con su ID asignado

        Raises:
            ValidationException: Si los datos son inválidos (422)
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> new_company = await service.create({
            ...     "name": "AK Group",
            ...     "company_type_id": 1,
            ...     "country_id": 1,
            ...     "nit": "900123456-7",
            ...     "email": "info@akgroup.com",
            ...     "phone": "+57 300 1234567",
            ...     "address": "Calle 123 #45-67",
            ...     "is_active": True
            ... })
            >>> print(f"Empresa creada con ID: {new_company['id']}")
        """
        logger.info("Creando nueva empresa | name={}", data.get("name"))

        try:
            company = await self._client.post("/companies/", json=data)

            logger.success(
                "Empresa creada exitosamente | id={} name={}",
                company.get("id"),
                company.get("name"),
            )
            return company

        except Exception as e:
            logger.error("Error al crear empresa | data={} error={}", data, str(e))
            raise

    async def update(
        self,
        company_id: int,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Actualiza una empresa existente.

        Args:
            company_id: ID de la empresa a actualizar
            data: Datos a actualizar (campos opcionales):
                - name: str
                - company_type_id: int
                - country_id: int
                - nit: str
                - email: str
                - phone: str
                - address: str
                - is_active: bool

        Returns:
            Datos de la empresa actualizada

        Raises:
            NotFoundException: Si la empresa no existe
            ValidationException: Si los datos son inválidos (422)
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> updated_company = await service.update(1, {
            ...     "name": "AK Group Internacional",
            ...     "phone": "+57 300 9876543"
            ... })
            >>> print(f"Empresa actualizada: {updated_company['name']}")
        """
        logger.info("Actualizando empresa | company_id={} data={}", company_id, data)

        try:
            company = await self._client.put(f"/companies/{company_id}", json=data)

            logger.success(
                "Empresa actualizada exitosamente | id={} name={}",
                company_id,
                company.get("name"),
            )
            return company

        except Exception as e:
            logger.error(
                "Error al actualizar empresa | company_id={} data={} error={}",
                company_id,
                data,
                str(e),
            )
            raise

    async def delete(self, company_id: int) -> bool:
        """
        Elimina una empresa.

        Args:
            company_id: ID de la empresa a eliminar

        Returns:
            True si la eliminación fue exitosa

        Raises:
            NotFoundException: Si la empresa no existe
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> success = await service.delete(1)
            >>> if success:
            ...     print("Empresa eliminada exitosamente")
        """
        logger.info("Eliminando empresa | company_id={}", company_id)

        try:
            result = await self._client.delete(f"/companies/{company_id}")

            logger.success("Empresa eliminada exitosamente | company_id={}", company_id)
            return result

        except Exception as e:
            logger.error(
                "Error al eliminar empresa | company_id={} error={}", company_id, str(e)
            )
            raise

    async def close(self) -> None:
        """
        Cierra el cliente HTTP y libera recursos.

        Example:
            >>> await service.close()
        """
        await self._client.close()

    async def __aenter__(self) -> "CompanyAPIService":
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        await self.close()
