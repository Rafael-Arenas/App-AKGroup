"""
Endpoints REST para Plant.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.backend.api.dependencies import get_database, get_current_user_id
from src.backend.services.core.plant_service import PlantService
from src.backend.repositories.core.plant_repository import PlantRepository
from src.shared.schemas.core.plant import PlantCreate, PlantUpdate, PlantResponse
from src.shared.schemas.base import MessageResponse
from src.backend.utils.logger import logger

router = APIRouter(prefix="/plants", tags=["plants"])


def get_plant_service(db: Session = Depends(get_database)) -> PlantService:
    """Dependency para obtener instancia de PlantService."""
    repository = PlantRepository(db)
    return PlantService(repository=repository, session=db)


@router.get("/company/{company_id}", response_model=List[PlantResponse])
def get_plants_by_company(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    service: PlantService = Depends(get_plant_service),
):
    """Obtiene todas las plantas de una empresa."""
    logger.info(f"GET /plants/company/{company_id}")
    return service.get_by_company(company_id, skip=skip, limit=limit)


@router.get("/{plant_id}", response_model=PlantResponse)
def get_plant(
    plant_id: int,
    service: PlantService = Depends(get_plant_service),
):
    """Obtiene una planta por ID."""
    logger.info(f"GET /plants/{plant_id}")
    return service.get_by_id(plant_id)


@router.post("/", response_model=PlantResponse, status_code=status.HTTP_201_CREATED)
def create_plant(
    data: PlantCreate,
    service: PlantService = Depends(get_plant_service),
    user_id: int = Depends(get_current_user_id),
):
    """Crea una nueva planta."""
    logger.info(f"POST /plants/ - name={data.name}")
    return service.create(data, user_id)


@router.put("/{plant_id}", response_model=PlantResponse)
def update_plant(
    plant_id: int,
    data: PlantUpdate,
    service: PlantService = Depends(get_plant_service),
    user_id: int = Depends(get_current_user_id),
):
    """Actualiza una planta existente."""
    logger.info(f"PUT /plants/{plant_id}")
    return service.update(plant_id, data, user_id)


@router.delete("/{plant_id}", response_model=MessageResponse)
def delete_plant(
    plant_id: int,
    service: PlantService = Depends(get_plant_service),
    user_id: int = Depends(get_current_user_id),
):
    """Elimina una planta."""
    logger.info(f"DELETE /plants/{plant_id}")
    service.delete(plant_id, user_id)
    return MessageResponse(message="Planta eliminada exitosamente")
