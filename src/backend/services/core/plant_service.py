"""
Servicio para Plant.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from src.backend.models.core.companies import Plant
from src.backend.repositories.core.plant_repository import PlantRepository
from src.backend.services.base import BaseService
from src.shared.schemas.core.plant import PlantCreate, PlantUpdate, PlantResponse


class PlantService(BaseService[Plant, PlantCreate, PlantUpdate, PlantResponse]):
    """
    Servicio de negocio para Plants.
    """

    def __init__(self, repository: PlantRepository, session: Session):
        super().__init__(repository, session, Plant, PlantResponse)
        self.repository = repository

    def get_by_company(self, company_id: int, skip: int = 0, limit: int = 100) -> List[Plant]:
        """
        Obtiene plantas de una empresa.
        """
        return self.repository.get_by_company(company_id, skip, limit)
