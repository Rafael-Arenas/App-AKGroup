"""
Endpoints REST para CompanyRut.

Proporciona operaciones CRUD sobre RUTs de empresas.
"""


from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from src.backend.api.dependencies import get_database, get_current_user_id
from src.backend.services.core.company_rut_service import CompanyRutService
from src.backend.repositories.core.company_rut_repository import CompanyRutRepository
from src.shared.schemas.core.company_rut import CompanyRutCreate, CompanyRutUpdate, CompanyRutResponse
from src.shared.schemas.base import MessageResponse
from src.backend.utils.logger import logger
from pydantic import ValidationError

router = APIRouter(prefix="/company-ruts", tags=["company-ruts"])


def get_company_rut_service(db: Session = Depends(get_database)) -> CompanyRutService:
    """
    Dependency para obtener instancia de CompanyRutService.

    Args:
        db: Sesión de base de datos

    Returns:
        Instancia configurada de CompanyRutService
    """
    repository = CompanyRutRepository(db)
    return CompanyRutService(repository=repository, session=db)


@router.get("/", response_model=list[CompanyRutResponse])
def get_company_ruts(
    skip: int = 0,
    limit: int = 100,
    service: CompanyRutService = Depends(get_company_rut_service),
):
    """
    Obtiene todos los RUTs con paginación.

    Args:
        skip: Número de registros a saltar (default: 0)
        limit: Número máximo de registros (default: 100)
        service: Servicio de RUTs

    Returns:
        Lista de RUTs

    Example:
        GET /api/v1/company-ruts?skip=0&limit=50
    """
    logger.info(f"GET /company-ruts - skip={skip}, limit={limit}")

    ruts = service.get_all(skip=skip, limit=limit)

    logger.info(f"Retornando {len(ruts)} RUT(s)")
    return ruts


@router.get("/company/{company_id}", response_model=list[CompanyRutResponse])
def get_ruts_by_company(
    company_id: int,
    service: CompanyRutService = Depends(get_company_rut_service),
):
    """
    Obtiene todos los RUTs de una empresa.

    Args:
        company_id: ID de la empresa
        service: Servicio de RUTs

    Returns:
        Lista de RUTs de la empresa

    Example:
        GET /api/v1/company-ruts/company/1
    """
    logger.info(f"GET /company-ruts/company/{company_id}")

    ruts = service.get_by_company(company_id)

    logger.info(f"Retornando {len(ruts)} RUT(s) de empresa id={company_id}")
    return ruts


@router.get("/company/{company_id}/main", response_model=CompanyRutResponse)
def get_main_rut(
    company_id: int,
    service: CompanyRutService = Depends(get_company_rut_service),
):
    """
    Obtiene el RUT principal de una empresa.

    Args:
        company_id: ID de la empresa
        service: Servicio de RUTs

    Returns:
        RUT principal de la empresa

    Example:
        GET /api/v1/company-ruts/company/1/main
    """
    logger.info(f"GET /company-ruts/company/{company_id}/main")

    rut = service.get_main_rut(company_id)

    logger.info(f"RUT principal encontrado: {rut.rut}")
    return rut


@router.get("/company/{company_id}/secondary", response_model=list[CompanyRutResponse])
def get_secondary_ruts(
    company_id: int,
    service: CompanyRutService = Depends(get_company_rut_service),
):
    """
    Obtiene los RUTs secundarios de una empresa.

    Args:
        company_id: ID de la empresa
        service: Servicio de RUTs

    Returns:
        Lista de RUTs secundarios

    Example:
        GET /api/v1/company-ruts/company/1/secondary
    """
    logger.info(f"GET /company-ruts/company/{company_id}/secondary")

    ruts = service.get_secondary_ruts(company_id)

    logger.info(f"Retornando {len(ruts)} RUT(s) secundario(s)")
    return ruts


@router.get("/search/{rut}", response_model=CompanyRutResponse)
def get_rut_by_value(
    rut: str,
    service: CompanyRutService = Depends(get_company_rut_service),
):
    """
    Obtiene un RUT por su valor.

    Args:
        rut: Valor del RUT a buscar
        service: Servicio de RUTs

    Returns:
        RUT encontrado

    Raises:
        404: Si no se encuentra el RUT

    Example:
        GET /api/v1/company-ruts/search/76123456-7
    """
    logger.info(f"GET /company-ruts/search/{rut}")

    rut_entity = service.get_by_rut(rut)

    logger.info(f"RUT encontrado: {rut_entity.rut}")
    return rut_entity


@router.get("/{rut_id}", response_model=CompanyRutResponse)
def get_rut(
    rut_id: int,
    service: CompanyRutService = Depends(get_company_rut_service),
):
    """
    Obtiene un RUT por ID.

    Args:
        rut_id: ID del RUT
        service: Servicio de RUTs

    Returns:
        RUT encontrado

    Raises:
        404: Si no se encuentra el RUT

    Example:
        GET /api/v1/company-ruts/123
    """
    logger.info(f"GET /company-ruts/{rut_id}")

    rut = service.get_by_id(rut_id)

    logger.info(f"RUT encontrado: {rut.rut}")
    return rut


@router.post("/", response_model=CompanyRutResponse, status_code=status.HTTP_201_CREATED)
def create_rut(
    rut_data: CompanyRutCreate,
    service: CompanyRutService = Depends(get_company_rut_service),
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Crea un nuevo RUT.

    Args:
        rut_data: Datos del RUT a crear
        service: Servicio de RUTs
        db: Sesión de base de datos
        user_id: ID del usuario que crea (para auditoría)

    Returns:
        RUT creado

    Raises:
        400: Si los datos no son válidos
        409: Si el RUT ya existe

    Example:
        POST /api/v1/company-ruts
        Body:
        {
            "rut": "76.123.456-7",
            "is_main": true,
            "company_id": 1
        }
    """
    logger.info(f"POST /company-ruts - company_id={rut_data.company_id}")

    try:
        rut = service.create(rut_data, user_id)
        
        # Commit the transaction to save to database
        db.commit()

        logger.success(f"RUT creado: id={rut.id}, rut={rut.rut}")
        return rut
    except ValidationError as e:
        logger.error(f"Error de validación al crear RUT: {e.errors()}")
        raise HTTPException(
            status_code=422,
            detail=f"Error de validación: {e.errors()}"
        )
    except Exception as e:
        logger.error(f"Error al crear RUT: {str(e)}")
        raise


@router.put("/{rut_id}", response_model=CompanyRutResponse)
def update_rut(
    rut_id: int,
    rut_data: CompanyRutUpdate,
    service: CompanyRutService = Depends(get_company_rut_service),
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Actualiza un RUT existente.

    Args:
        rut_id: ID del RUT a actualizar
        rut_data: Datos a actualizar
        service: Servicio de RUTs
        user_id: ID del usuario que actualiza

    Returns:
        RUT actualizado

    Raises:
        404: Si no se encuentra el RUT
        400: Si los datos no son válidos
        409: Si el RUT ya existe en otra empresa

    Example:
        PUT /api/v1/company-ruts/123
        Body:
        {
            "is_main": false
        }
    """
    logger.info(f"PUT /company-ruts/{rut_id}")

    rut = service.update(rut_id, rut_data, user_id)
    
    # Commit the transaction to save to database
    db.commit()

    logger.success(f"RUT actualizado: id={rut_id}")
    return rut


@router.put("/{rut_id}/set-main", response_model=CompanyRutResponse)
def set_rut_as_main(
    rut_id: int,
    service: CompanyRutService = Depends(get_company_rut_service),
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Establece un RUT como principal.

    Args:
        rut_id: ID del RUT a establecer como principal
        service: Servicio de RUTs
        user_id: ID del usuario que realiza la acción

    Returns:
        RUT actualizado

    Raises:
        404: Si no se encuentra el RUT

    Example:
        PUT /api/v1/company-ruts/123/set-main
    """
    logger.info(f"PUT /company-ruts/{rut_id}/set-main")

    rut = service.set_as_main(rut_id, user_id)
    
    # Commit the transaction to save to database
    db.commit()

    logger.success(f"RUT {rut.rut} establecido como principal")
    return rut


@router.delete("/{rut_id}", response_model=MessageResponse)
def delete_rut(
    rut_id: int,
    soft: bool = True,
    service: CompanyRutService = Depends(get_company_rut_service),
    db: Session = Depends(get_database),
    user_id: int = Depends(get_current_user_id),
):
    """
    Elimina un RUT.

    Args:
        rut_id: ID del RUT a eliminar
        soft: Si True, soft delete; si False, hard delete (default: True)
        service: Servicio de RUTs
        user_id: ID del usuario que elimina

    Returns:
        Mensaje de confirmación

    Raises:
        404: Si no se encuentra el RUT

    Example:
        DELETE /api/v1/company-ruts/123?soft=true
    """
    logger.info(f"DELETE /company-ruts/{rut_id} (soft={soft})")

    service.delete(rut_id, user_id, soft=soft)
    
    # Commit the transaction to save to database
    db.commit()

    delete_type = "marcado como eliminado" if soft else "eliminado permanentemente"
    logger.success(f"RUT {delete_type}: id={rut_id}")

    return MessageResponse(
        message=f"RUT {delete_type} exitosamente",
        details={"rut_id": rut_id, "soft_delete": soft}
    )
