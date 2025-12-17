"""
Servicio API para gestión de Plants (Plantas/Sucursales).

Este módulo proporciona métodos para interactuar con los endpoints de plantas
del backend FastAPI.
"""

from typing import Any
from loguru import logger

from .base_api_client import BaseAPIClient


class PlantAPIService:
    """
    Servicio para operaciones CRUD de Plants.

    Proporciona métodos asíncronos para listar, crear, actualizar, eliminar
    y buscar plantas en el backend.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
    ) -> None:
        """
        Inicializa el servicio de Plant API.

        Args:
            base_url: URL base del backend
            timeout: Timeout en segundos para las peticiones
        """
        self._client = BaseAPIClient(base_url=base_url, timeout=timeout)
        logger.debug("PlantAPIService inicializado | base_url={}", base_url)

    async def get_by_company(self, company_id: int) -> list[dict[str, Any]]:
        """
        Obtiene todas las plantas de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de plantas
        """
        logger.info(f"Obteniendo plantas para empresa ID={company_id}")

        try:
            plants = await self._client.get(f"/plants/company/{company_id}")
            logger.success(f"Plantas obtenidas: {len(plants)}")
            return plants
        except Exception as e:
            logger.error(f"Error al obtener plantas: {e}")
            raise

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Crea una nueva planta.

        Args:
            data: Datos de la planta

        Returns:
            Planta creada
        """
        logger.info(f"Creando nueva planta: {data.get('name')}")

        try:
            plant = await self._client.post("/plants/", json=data)
            logger.success(f"Planta creada ID={plant.get('id')}")
            return plant
        except Exception as e:
            logger.error(f"Error al crear planta: {e}")
            raise

    async def update(self, plant_id: int, data: dict[str, Any]) -> dict[str, Any]:
        """
        Actualiza una planta existente.

        Args:
            plant_id: ID de la planta
            data: Datos a actualizar

        Returns:
            Planta actualizada
        """
        logger.info(f"Actualizando planta ID={plant_id}")

        try:
            plant = await self._client.put(f"/plants/{plant_id}", json=data)
            logger.success(f"Planta actualizada ID={plant.get('id')}")
            return plant
        except Exception as e:
            logger.error(f"Error al actualizar planta: {e}")
            raise

    async def delete(self, plant_id: int) -> bool:
        """
        Elimina una planta.

        Args:
            plant_id: ID de la planta

        Returns:
            True si fue exitoso
        """
        logger.info(f"Eliminando planta ID={plant_id}")

        try:
            await self._client.delete(f"/plants/{plant_id}")
            logger.success(f"Planta eliminada ID={plant_id}")
            return True
        except Exception as e:
            logger.error(f"Error al eliminar planta: {e}")
            raise

    async def close(self) -> None:
        """Cierra el cliente HTTP."""
        await self._client.close()

    async def __aenter__(self) -> "PlantAPIService":
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        await self.close()
