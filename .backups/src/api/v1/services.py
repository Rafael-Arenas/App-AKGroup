"""
Endpoints REST para Service.

Proporciona operaciones CRUD sobre servicios/departamentos.
"""

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_database, get_current_user_id
from src.services.core.service_service import ServiceService
from src.repositories.core.service_repository import ServiceRepository
from src.schemas.core.service import ServiceCreate, ServiceUpdate, ServiceResponse
from src.schemas.base import MessageResponse
from src.utils.logger import logger

router = APIRouter(prefix="/services", tags=["services"])


def get_service_service(db: Session = Depends(get_database)) -> ServiceService:
    """
    Dependency para obtener instancia de ServiceService.

    Args:
        db: Sesión de base de datos

    Returns:
        Instancia configurada de ServiceService
    """
    repository = ServiceRepository(db)
    return ServiceService(repository=repository, session=db)


@router.get("/", response_model=List[ServiceResponse])
def get_services(
    skip: int = 0,
    limit: int = 100,
    service: ServiceService = Depends(get_service_service),
):
    """
    Obtiene todos los servicios con paginación.

    Args:
        skip: Número de registros a saltar (default: 0)
        limit: Número máximo de registros (default: 100)
        service: Servicio de servicios

    Returns:
        Lista de servicios

    Example:
        GET /api/v1/services?skip=0&limit=50
    """
    logger.info(f"GET /services - skip={skip}, limit={limit}")

    services = service.get_all(skip=skip, limit=limit)

    logger.info(f"Retornando {len(services)} servicio(s)")
    return services


@router.get("/active", response_model=List[ServiceResponse])
def get_active_services(
    skip: int = 0,
    limit: int = 100,
    service: ServiceService = Depends(get_service_service),
):
    """
    Obtiene solo los servicios activos.

    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros
        service: Servicio de servicios

    Returns:
        Lista de servicios activos

    Example:
        GET /api/v1/services/active?skip=0&limit=50
    """
    logger.info(f"GET /services/active - skip={skip}, limit={limit}")

    services = service.get_active_services(skip=skip, limit=limit)

    logger.info(f"Retornando {len(services)} servicio(s) activo(s)")
    return services


@router.get("/name/{name}", response_model=ServiceResponse)
def get_service_by_name(
    name: str,
    service: ServiceService = Depends(get_service_service),
):
    """
    Obtiene un servicio por nombre.

    Args:
        name: Nombre del servicio
        service: Servicio de servicios

    Returns:
        Servicio encontrado

    Raises:
        404: Si no se encuentra el servicio

    Example:
        GET /api/v1/services/name/Ventas
    """
    logger.info(f"GET /services/name/{name}")

    svc = service.get_by_name(name)

    logger.info(f"Servicio encontrado: {svc.name}")
    return svc


@router.get("/{service_id}/contacts-count")
def get_contacts_count(
    service_id: int,
    service: ServiceService = Depends(get_service_service),
):
    """
    Cuenta cuántos contactos están asociados a un servicio.

    Args:
        service_id: ID del servicio
        service: Servicio de servicios

    Returns:
        Número de contactos

    Example:
        GET /api/v1/services/1/contacts-count
        Response:
        {
            "service_id": 1,
            "contact_count": 5
        }
    """
    logger.info(f"GET /services/{service_id}/contacts-count")

    count = service.count_contacts(service_id)

    logger.info(f"Servicio id={service_id} tiene {count} contacto(s)")

    return {
        "service_id": service_id,
        "contact_count": count
    }


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    service: ServiceService = Depends(get_service_service),
):
    """
    Obtiene un servicio por ID.

    Args:
        service_id: ID del servicio
        service: Servicio de servicios

    Returns:
        Servicio encontrado

    Raises:
        404: Si no se encuentra el servicio

    Example:
        GET /api/v1/services/123
    """
    logger.info(f"GET /services/{service_id}")

    svc = service.get_by_id(service_id)

    logger.info(f"Servicio encontrado: {svc.name}")
    return svc


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    service_data: ServiceCreate,
    service: ServiceService = Depends(get_service_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Crea un nuevo servicio.

    Args:
        service_data: Datos del servicio a crear
        service: Servicio de servicios
        user_id: ID del usuario que crea (para auditoría)

    Returns:
        Servicio creado

    Raises:
        400: Si los datos no son válidos
        409: Si el nombre ya existe

    Example:
        POST /api/v1/services
        Body:
        {
            "name": "Ventas",
            "description": "Departamento de ventas",
            "is_active": true
        }
    """
    logger.info(f"POST /services - name={service_data.name}")

    svc = service.create(service_data, user_id)

    logger.success(f"Servicio creado: id={svc.id}, name={svc.name}")
    return svc


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    service: ServiceService = Depends(get_service_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Actualiza un servicio existente.

    Args:
        service_id: ID del servicio a actualizar
        service_data: Datos a actualizar
        service: Servicio de servicios
        user_id: ID del usuario que actualiza

    Returns:
        Servicio actualizado

    Raises:
        404: Si no se encuentra el servicio
        400: Si los datos no son válidos
        409: Si el nombre ya existe en otro servicio

    Example:
        PUT /api/v1/services/123
        Body:
        {
            "description": "Nueva descripción",
            "is_active": false
        }
    """
    logger.info(f"PUT /services/{service_id}")

    svc = service.update(service_id, service_data, user_id)

    logger.success(f"Servicio actualizado: id={service_id}")
    return svc


@router.delete("/{service_id}", response_model=MessageResponse)
def delete_service(
    service_id: int,
    soft: bool = True,
    service: ServiceService = Depends(get_service_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Elimina un servicio.

    Args:
        service_id: ID del servicio a eliminar
        soft: Si True, soft delete; si False, hard delete (default: True)
        service: Servicio de servicios
        user_id: ID del usuario que elimina

    Returns:
        Mensaje de confirmación

    Raises:
        404: Si no se encuentra el servicio
        400: Si el servicio tiene contactos asociados

    Example:
        DELETE /api/v1/services/123?soft=true
    """
    logger.info(f"DELETE /services/{service_id} (soft={soft})")

    service.delete(service_id, user_id, soft=soft)

    delete_type = "marcado como eliminado" if soft else "eliminado permanentemente"
    logger.success(f"Servicio {delete_type}: id={service_id}")

    return MessageResponse(
        message=f"Servicio {delete_type} exitosamente",
        details={"service_id": service_id, "soft_delete": soft}
    )
