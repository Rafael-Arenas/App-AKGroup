"""
Cliente API para gestión de empresas.

Proporciona métodos para interactuar con el endpoint de companies del backend.
"""

from typing import Any

from src.frontend.services.base_api import BaseAPIClient
from src.shared.schemas.core.company import CompanyResponse, CompanyCreate, CompanyUpdate


class CompaniesAPIClient(BaseAPIClient):
    """
    Cliente API para gestión de empresas.

    Proporciona métodos específicos para CRUD de companies.
    """

    async def get_companies(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Obtiene lista de empresas.

        Args:
            skip: Número de registros a saltar (paginación)
            limit: Límite de registros a retornar
            search: Término de búsqueda opcional

        Returns:
            Lista de empresas

        Raises:
            httpx.HTTPError: Si ocurre un error HTTP
        """
        params: dict[str, Any] = {"skip": skip, "limit": limit}
        if search:
            params["search"] = search

        return await self.get("/companies", params=params)

    async def get_company(self, company_id: int) -> dict[str, Any]:
        """
        Obtiene una empresa por ID.

        Args:
            company_id: ID de la empresa

        Returns:
            Datos de la empresa

        Raises:
            httpx.HTTPError: Si ocurre un error HTTP
        """
        return await self.get(f"/companies/{company_id}")

    async def create_company(self, company_data: dict[str, Any]) -> dict[str, Any]:
        """
        Crea una nueva empresa.

        Args:
            company_data: Datos de la empresa a crear

        Returns:
            Datos de la empresa creada

        Raises:
            httpx.HTTPError: Si ocurre un error HTTP
        """
        return await self.post("/companies", data=company_data)

    async def update_company(
        self, company_id: int, company_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Actualiza una empresa existente.

        Args:
            company_id: ID de la empresa
            company_data: Datos actualizados

        Returns:
            Datos de la empresa actualizada

        Raises:
            httpx.HTTPError: Si ocurre un error HTTP
        """
        return await self.put(f"/companies/{company_id}", data=company_data)

    async def delete_company(self, company_id: int) -> dict[str, Any]:
        """
        Elimina una empresa (soft delete).

        Args:
            company_id: ID de la empresa

        Returns:
            Confirmación de eliminación

        Raises:
            httpx.HTTPError: Si ocurre un error HTTP
        """
        return await self.delete(f"/companies/{company_id}")

    async def search_companies(
        self, query: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        """
        Busca empresas por nombre o RUT.

        Args:
            query: Término de búsqueda
            limit: Límite de resultados

        Returns:
            Lista de empresas que coinciden

        Raises:
            httpx.HTTPError: Si ocurre un error HTTP
        """
        params = {"search": query, "limit": limit}
        return await self.get("/companies/search", params=params)
