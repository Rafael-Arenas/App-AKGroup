"""
Endpoints REST para Company.

Proporciona operaciones CRUD sobre empresas.
"""

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.backend.api.dependencies import get_database, get_current_user_id, validate_pagination
from src.backend.services.core.company_service import CompanyService
from src.backend.repositories.core.company_repository import CompanyRepository
from src.shared.schemas.core.company import CompanyCreate, CompanyUpdate, CompanyResponse
from src.shared.schemas.base import MessageResponse
from src.backend.utils.logger import logger

router = APIRouter(prefix="/companies", tags=["companies"])


def get_company_service(db: Session = Depends(get_database)) -> CompanyService:
    """
    Dependency para obtener instancia de CompanyService.

    Args:
        db: Sesión de base de datos

    Returns:
        Instancia configurada de CompanyService
    """
    repository = CompanyRepository(db)
    return CompanyService(repository=repository, session=db)


@router.get("/", response_model=List[CompanyResponse])
def get_companies(
    skip: int = 0,
    limit: int = 100,
    company_type_id: int | None = None,
    is_active: bool | None = None,
    service: CompanyService = Depends(get_company_service),
):
    """
    Obtiene todas las empresas con paginación y filtros opcionales.

    Args:
        skip: Número de registros a saltar (default: 0)
        limit: Número máximo de registros (default: 100, max: 1000)
        company_type_id: Filtrar por tipo de empresa (1=CLIENT, 2=SUPPLIER)
        is_active: Filtrar por estado (True=activas, False=inactivas, None=todas)
        service: Servicio de empresas

    Returns:
        Lista de empresas

    Example:
        GET /api/v1/companies?skip=0&limit=50
        GET /api/v1/companies?company_type_id=1  # Solo clientes
        GET /api/v1/companies?company_type_id=1&is_active=true  # Solo clientes activos
    """
    logger.info(
        f"GET /companies - skip={skip}, limit={limit}, "
        f"company_type_id={company_type_id}, is_active={is_active}"
    )

    # Si se especifica tipo, filtrar por tipo
    if company_type_id is not None:
        companies = service.get_by_type(
            company_type_id=company_type_id,
            skip=skip,
            limit=limit,
            is_active=is_active
        )
    else:
        # Si solo se filtra por is_active
        if is_active is not None:
            if is_active:
                companies = service.get_active_companies(skip=skip, limit=limit)
            else:
                # Necesitaríamos un método get_inactive_companies
                # Por ahora, obtener todas y filtrar
                all_companies = service.get_all(skip=0, limit=1000)
                companies = [c for c in all_companies if not c.is_active][skip:skip+limit]
        else:
            companies = service.get_all(skip=skip, limit=limit)

    logger.info(f"Retornando {len(companies)} empresa(s)")
    return companies


@router.get("/active", response_model=List[CompanyResponse])
def get_active_companies(
    skip: int = 0,
    limit: int = 100,
    service: CompanyService = Depends(get_company_service),
):
    """
    Obtiene solo las empresas activas.

    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros
        service: Servicio de empresas

    Returns:
        Lista de empresas activas

    Example:
        GET /api/v1/companies/active?skip=0&limit=50
    """
    logger.info(f"GET /companies/active - skip={skip}, limit={limit}")

    companies = service.get_active_companies(skip=skip, limit=limit)

    logger.info(f"Retornando {len(companies)} empresa(s) activa(s)")
    return companies


@router.get("/search/{name}", response_model=List[CompanyResponse])
def search_companies(
    name: str,
    service: CompanyService = Depends(get_company_service),
):
    """
    Busca empresas por nombre (búsqueda parcial).

    Args:
        name: Texto a buscar en el nombre
        service: Servicio de empresas

    Returns:
        Lista de empresas que coinciden

    Example:
        GET /api/v1/companies/search/test
    """
    logger.info(f"GET /companies/search/{name}")

    companies = service.search_by_name(name)

    logger.info(f"Búsqueda '{name}' retornó {len(companies)} empresa(s)")
    return companies


@router.get("/trigram/{trigram}", response_model=CompanyResponse)
def get_company_by_trigram(
    trigram: str,
    service: CompanyService = Depends(get_company_service),
):
    """
    Obtiene una empresa por su trigram.

    Args:
        trigram: Trigram de 3 letras (ej: "AKG")
        service: Servicio de empresas

    Returns:
        Empresa encontrada

    Raises:
        404: Si no se encuentra la empresa

    Example:
        GET /api/v1/companies/trigram/AKG
    """
    logger.info(f"GET /companies/trigram/{trigram}")

    company = service.get_by_trigram(trigram)

    logger.info(f"Empresa encontrada: {company.name}")
    return company


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    service: CompanyService = Depends(get_company_service),
):
    """
    Obtiene una empresa por ID.

    Args:
        company_id: ID de la empresa
        service: Servicio de empresas

    Returns:
        Empresa encontrada

    Raises:
        404: Si no se encuentra la empresa

    Example:
        GET /api/v1/companies/123
    """
    logger.info(f"GET /companies/{company_id}")

    company = service.get_by_id(company_id)

    logger.info(f"Empresa encontrada: {company.name}")
    return company


@router.get("/{company_id}/with-plants", response_model=CompanyResponse)
def get_company_with_plants(
    company_id: int,
    service: CompanyService = Depends(get_company_service),
):
    """
    Obtiene una empresa con sus plantas cargadas.

    Args:
        company_id: ID de la empresa
        service: Servicio de empresas

    Returns:
        Empresa con plantas

    Raises:
        404: Si no se encuentra la empresa

    Example:
        GET /api/v1/companies/123/with-plants
    """
    logger.info(f"GET /companies/{company_id}/with-plants")

    company = service.get_with_plants(company_id)

    logger.info(f"Empresa encontrada con {len(company.plants)} planta(s)")
    return company


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    company_data: CompanyCreate,
    service: CompanyService = Depends(get_company_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Crea una nueva empresa.

    Args:
        company_data: Datos de la empresa a crear
        service: Servicio de empresas
        user_id: ID del usuario que crea (para auditoría)

    Returns:
        Empresa creada

    Raises:
        400: Si los datos no son válidos
        409: Si el trigram ya existe

    Example:
        POST /api/v1/companies
        Body:
        {
            "name": "AK Group",
            "trigram": "AKG",
            "company_type_id": 1
        }
    """
    logger.info(f"POST /companies - trigram={company_data.trigram}")

    company = service.create(company_data, user_id)

    logger.success(f"Empresa creada: id={company.id}, trigram={company.trigram}")
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    service: CompanyService = Depends(get_company_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Actualiza una empresa existente.

    Args:
        company_id: ID de la empresa a actualizar
        company_data: Datos a actualizar
        service: Servicio de empresas
        user_id: ID del usuario que actualiza

    Returns:
        Empresa actualizada

    Raises:
        404: Si no se encuentra la empresa
        400: Si los datos no son válidos
        409: Si el trigram ya existe en otra empresa

    Example:
        PUT /api/v1/companies/123
        Body:
        {
            "name": "Nuevo Nombre",
            "phone": "+56912345678"
        }
    """
    logger.info(f"PUT /companies/{company_id}")

    company = service.update(company_id, company_data, user_id)

    logger.success(f"Empresa actualizada: id={company_id}")
    return company


@router.delete("/{company_id}", response_model=MessageResponse)
def delete_company(
    company_id: int,
    soft: bool = True,
    service: CompanyService = Depends(get_company_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Elimina una empresa.

    Args:
        company_id: ID de la empresa a eliminar
        soft: Si True, soft delete; si False, hard delete (default: True)
        service: Servicio de empresas
        user_id: ID del usuario que elimina

    Returns:
        Mensaje de confirmación

    Raises:
        404: Si no se encuentra la empresa

    Example:
        DELETE /api/v1/companies/123?soft=true
    """
    logger.info(f"DELETE /companies/{company_id} (soft={soft})")

    service.delete(company_id, user_id, soft=soft)

    delete_type = "marcada como eliminada" if soft else "eliminada permanentemente"
    logger.success(f"Empresa {delete_type}: id={company_id}")

    return MessageResponse(
        message=f"Empresa {delete_type} exitosamente",
        details={"company_id": company_id, "soft_delete": soft}
    )
