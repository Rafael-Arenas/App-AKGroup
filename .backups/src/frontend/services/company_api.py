"""
Cliente API para operaciones con Companies.

Proporciona métodos para interactuar con los endpoints de empresas
del backend.
"""

from typing import List
from loguru import logger

from src.frontend.services.base_api_client import BaseAPIClient, APIException
from src.shared.schemas.core.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
)


class CompanyAPIClient(BaseAPIClient):
    """
    Cliente API para gestión de empresas.

    Proporciona métodos CRUD para empresas utilizando los schemas compartidos.

    Example:
        api = CompanyAPIClient()
        companies = api.get_all_companies()
        for company in companies:
            print(company.name)
    """

    def __init__(self) -> None:
        """Inicializa el cliente de API de empresas."""
        super().__init__(base_path="/api/v1")
        logger.debug("Initialized CompanyAPIClient")

    def get_all_companies(
        self,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> List[CompanyResponse]:
        """
        Obtiene todas las empresas.

        Args:
            skip: Número de registros a saltar (paginación)
            limit: Número máximo de registros a retornar
            include_inactive: Si incluir empresas inactivas

        Returns:
            Lista de empresas

        Raises:
            APIException: Si hay error en la petición

        Example:
            companies = api.get_all_companies(limit=50)
        """
        try:
            params = {
                "skip": skip,
                "limit": limit,
                "include_inactive": include_inactive,
            }
            data = self.get("/companies", params=params)
            return [CompanyResponse(**item) for item in data]
        except APIException:
            raise
        except Exception as e:
            logger.error(f"Error getting companies: {e}")
            raise APIException(f"Error obteniendo empresas: {e}") from e

    def get_company_by_id(self, company_id: int) -> CompanyResponse:
        """
        Obtiene una empresa por su ID.

        Args:
            company_id: ID de la empresa

        Returns:
            Empresa encontrada

        Raises:
            APIException: Si la empresa no existe o hay error

        Example:
            company = api.get_company_by_id(1)
            print(company.name)
        """
        try:
            data = self.get(f"/companies/{company_id}")
            return CompanyResponse(**data)
        except APIException:
            raise
        except Exception as e:
            logger.error(f"Error getting company {company_id}: {e}")
            raise APIException(f"Error obteniendo empresa: {e}") from e

    def create_company(self, company_data: CompanyCreate) -> CompanyResponse:
        """
        Crea una nueva empresa.

        Args:
            company_data: Datos de la empresa a crear

        Returns:
            Empresa creada

        Raises:
            APIException: Si hay error en la creación

        Example:
            new_company = CompanyCreate(
                name="Nueva Empresa",
                trigram="NEM",
                company_type_id=1
            )
            created = api.create_company(new_company)
        """
        try:
            data = self.post(
                "/companies",
                json=company_data.model_dump(exclude_unset=True),
            )
            return CompanyResponse(**data)
        except APIException:
            raise
        except Exception as e:
            logger.error(f"Error creating company: {e}")
            raise APIException(f"Error creando empresa: {e}") from e

    def update_company(
        self,
        company_id: int,
        company_data: CompanyUpdate,
    ) -> CompanyResponse:
        """
        Actualiza una empresa existente.

        Args:
            company_id: ID de la empresa a actualizar
            company_data: Datos a actualizar

        Returns:
            Empresa actualizada

        Raises:
            APIException: Si la empresa no existe o hay error

        Example:
            update_data = CompanyUpdate(name="Nombre Actualizado")
            updated = api.update_company(1, update_data)
        """
        try:
            data = self.put(
                f"/companies/{company_id}",
                json=company_data.model_dump(exclude_unset=True),
            )
            return CompanyResponse(**data)
        except APIException:
            raise
        except Exception as e:
            logger.error(f"Error updating company {company_id}: {e}")
            raise APIException(f"Error actualizando empresa: {e}") from e

    def delete_company(self, company_id: int) -> dict:
        """
        Elimina una empresa (soft delete).

        Args:
            company_id: ID de la empresa a eliminar

        Returns:
            Diccionario con mensaje de confirmación

        Raises:
            APIException: Si la empresa no existe o hay error

        Example:
            result = api.delete_company(1)
            print(result["message"])
        """
        try:
            return self.delete(f"/companies/{company_id}")
        except APIException:
            raise
        except Exception as e:
            logger.error(f"Error deleting company {company_id}: {e}")
            raise APIException(f"Error eliminando empresa: {e}") from e

    def search_companies(
        self,
        search_term: str,
        limit: int = 50,
    ) -> List[CompanyResponse]:
        """
        Busca empresas por nombre o trigram.

        Args:
            search_term: Término de búsqueda
            limit: Número máximo de resultados

        Returns:
            Lista de empresas que coinciden con la búsqueda

        Raises:
            APIException: Si hay error en la búsqueda

        Example:
            results = api.search_companies("AK")
        """
        try:
            params = {"q": search_term, "limit": limit}
            data = self.get("/companies/search", params=params)
            return [CompanyResponse(**item) for item in data]
        except APIException:
            raise
        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            raise APIException(f"Error buscando empresas: {e}") from e
