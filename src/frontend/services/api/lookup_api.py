"""
Servicio API para gestión de Lookups (datos de referencia).

Este módulo proporciona métodos para obtener datos de referencia del sistema
como tipos de empresa, países, unidades de medida, etc.
"""

from typing import Any
from loguru import logger

from .base_api_client import BaseAPIClient


class LookupAPIService:
    """
    Servicio para obtener datos de referencia (lookups).

    Proporciona métodos asíncronos para obtener catálogos y listas
    de referencia del sistema.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
    ) -> None:
        """
        Inicializa el servicio de Lookup API.

        Args:
            base_url: URL base del backend
            timeout: Timeout en segundos para las peticiones

        Example:
            >>> service = LookupAPIService()
        """
        self._client = BaseAPIClient(base_url=base_url, timeout=timeout)
        logger.debug("LookupAPIService inicializado | base_url={}", base_url)

    async def get_company_types(self) -> list[dict[str, Any]]:
        """
        Obtiene todos los tipos de empresa disponibles.

        Returns:
            Lista de tipos de empresa con estructura:
                - id: int
                - name: str
                - code: str (opcional)
                - description: str (opcional)

        Raises:
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> company_types = await service.get_company_types()
            >>> for ct in company_types:
            ...     print(f"{ct['id']}: {ct['name']}")
        """
        logger.info("Obteniendo tipos de empresa")

        try:
            company_types = await self._client.get("/lookups/company-types")

            logger.success("Tipos de empresa obtenidos | total={}", len(company_types))
            return company_types

        except Exception as e:
            logger.error("Error al obtener tipos de empresa | error={}", str(e))
            raise

    async def get_countries(self) -> list[dict[str, Any]]:
        """
        Obtiene todos los países disponibles.

        Returns:
            Lista de países con estructura:
                - id: int
                - name: str
                - code: str (código ISO, ej: "CO", "US")
                - phone_code: str (código telefónico, ej: "+57")

        Raises:
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> countries = await service.get_countries()
            >>> for country in countries:
            ...     print(f"{country['code']}: {country['name']} ({country['phone_code']})")
        """
        logger.info("Obteniendo países")

        try:
            countries = await self._client.get("/lookups/countries")

            logger.success("Países obtenidos | total={}", len(countries))
            return countries

        except Exception as e:
            logger.error("Error al obtener países | error={}", str(e))
            raise

    async def get_units(self) -> list[dict[str, Any]]:
        """
        Obtiene todas las unidades de medida disponibles.

        Returns:
            Lista de unidades con estructura:
                - id: int
                - name: str (nombre completo, ej: "Kilogramo")
                - symbol: str (símbolo, ej: "kg")
                - unit_type: str (tipo, ej: "MASS", "LENGTH", "VOLUME")

        Raises:
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> units = await service.get_units()
            >>> for unit in units:
            ...     print(f"{unit['symbol']}: {unit['name']} ({unit['unit_type']})")
        """
        logger.info("Obteniendo unidades de medida")

        try:
            units = await self._client.get("/lookups/units")

            logger.success("Unidades obtenidas | total={}", len(units))
            return units

        except Exception as e:
            logger.error("Error al obtener unidades | error={}", str(e))
            raise

    async def get_lookup(self, lookup_type: str) -> list[dict[str, Any]]:
        """
        Obtiene datos de lookup por tipo.

        Args:
            lookup_type: Tipo de lookup a obtener.
                Valores válidos: "countries", "company_types", "units"

        Returns:
            Lista de elementos del tipo de lookup solicitado

        Raises:
            ValueError: Si el tipo de lookup es desconocido
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> countries = await service.get_lookup("countries")
            >>> company_types = await service.get_lookup("company_types")
            >>> units = await service.get_lookup("units")
        """
        logger.info("Obteniendo lookup | lookup_type={}", lookup_type)

        if lookup_type == "countries":
            return await self.get_countries()
        elif lookup_type == "company_types":
            return await self.get_company_types()
        elif lookup_type == "units":
            return await self.get_units()
        else:
            logger.error("Tipo de lookup desconocido | lookup_type={}", lookup_type)
            raise ValueError(f"Unknown lookup type: {lookup_type}")

    async def close(self) -> None:
        """
        Cierra el cliente HTTP y libera recursos.

        Example:
            >>> await service.close()
        """
        await self._client.close()

    async def __aenter__(self) -> "LookupAPIService":
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        await self.close()
