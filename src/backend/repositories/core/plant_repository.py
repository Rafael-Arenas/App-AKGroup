"""
Repositorio para Plant.
"""

from typing import List, Optional

from sqlalchemy import select, or_
from sqlalchemy.orm import Session, joinedload

from src.backend.models.core.companies import Plant
from src.backend.repositories.base import BaseRepository
from src.shared.schemas.core.plant import PlantCreate, PlantUpdate


class PlantRepository(BaseRepository[Plant]):
    """
    Repositorio para gestionar operaciones de base de datos de Plant.
    """

    def __init__(self, db: Session):
        super().__init__(db, Plant)

    def get_by_company(self, company_id: int, skip: int = 0, limit: int = 100) -> List[Plant]:
        """
        Obtiene plantas de una empresa.
        """
        stmt = (
            select(self.model)
            .options(joinedload(Plant.city))
            .where(self.model.company_id == company_id)
            .offset(skip)
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()

    def get_with_relations(self, plant_id: int) -> Optional[Plant]:
        """
        Obtiene una planta con sus relaciones cargadas.
        """
        stmt = (
            select(self.model)
            .options(joinedload(Plant.city))
            .where(self.model.id == plant_id)
        )
        return self.session.execute(stmt).scalar_one_or_none()
