"""
Endpoints REST para Staff.

Proporciona operaciones CRUD sobre usuarios del sistema.
"""

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.backend.api.dependencies import get_database, get_current_user_id
from src.backend.services.core.staff_service import StaffService
from src.backend.repositories.core.staff_repository import StaffRepository
from src.shared.schemas.core.staff import StaffCreate, StaffUpdate, StaffResponse
from src.shared.schemas.base import MessageResponse
from src.backend.utils.logger import logger

router = APIRouter(prefix="/staff", tags=["staff"])


def get_staff_service(db: Session = Depends(get_database)) -> StaffService:
    """
    Dependency para obtener instancia de StaffService.

    Args:
        db: Sesión de base de datos

    Returns:
        Instancia configurada de StaffService
    """
    repository = StaffRepository(db)
    return StaffService(repository=repository, session=db)


@router.get("/", response_model=List[StaffResponse])
def get_staff(
    skip: int = 0,
    limit: int = 100,
    service: StaffService = Depends(get_staff_service),
):
    """
    Obtiene todos los usuarios con paginación.

    Args:
        skip: Número de registros a saltar (default: 0)
        limit: Número máximo de registros (default: 100)
        service: Servicio de staff

    Returns:
        Lista de usuarios

    Example:
        GET /api/v1/staff?skip=0&limit=50
    """
    logger.info(f"GET /staff - skip={skip}, limit={limit}")

    staff = service.get_all(skip=skip, limit=limit)

    logger.info(f"Retornando {len(staff)} usuario(s)")
    return staff


@router.get("/active", response_model=List[StaffResponse])
def get_active_staff(
    skip: int = 0,
    limit: int = 100,
    service: StaffService = Depends(get_staff_service),
):
    """
    Obtiene solo los usuarios activos.

    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros
        service: Servicio de staff

    Returns:
        Lista de usuarios activos

    Example:
        GET /api/v1/staff/active?skip=0&limit=50
    """
    logger.info(f"GET /staff/active - skip={skip}, limit={limit}")

    staff = service.get_active_staff(skip=skip, limit=limit)

    logger.info(f"Retornando {len(staff)} usuario(s) activo(s)")
    return staff


@router.get("/admins", response_model=List[StaffResponse])
def get_admins(
    skip: int = 0,
    limit: int = 100,
    service: StaffService = Depends(get_staff_service),
):
    """
    Obtiene solo los administradores.

    Args:
        skip: Número de registros a saltar
        limit: Número máximo de registros
        service: Servicio de staff

    Returns:
        Lista de administradores

    Example:
        GET /api/v1/staff/admins?skip=0&limit=50
    """
    logger.info(f"GET /staff/admins - skip={skip}, limit={limit}")

    admins = service.get_admins(skip=skip, limit=limit)

    logger.info(f"Retornando {len(admins)} administrador(es)")
    return admins


@router.get("/search/{query}", response_model=List[StaffResponse])
def search_staff(
    query: str,
    service: StaffService = Depends(get_staff_service),
):
    """
    Busca usuarios por nombre (búsqueda parcial).

    Args:
        query: Texto a buscar
        service: Servicio de staff

    Returns:
        Lista de usuarios que coinciden

    Example:
        GET /api/v1/staff/search/john
    """
    logger.info(f"GET /staff/search/{query}")

    staff = service.search_by_name(query)

    logger.info(f"Búsqueda '{query}' retornó {len(staff)} usuario(s)")
    return staff


@router.get("/username/{username}", response_model=StaffResponse)
def get_staff_by_username(
    username: str,
    service: StaffService = Depends(get_staff_service),
):
    """
    Obtiene un usuario por username.

    Args:
        username: Username a buscar
        service: Servicio de staff

    Returns:
        Usuario encontrado

    Raises:
        404: Si no se encuentra el usuario

    Example:
        GET /api/v1/staff/username/jdoe
    """
    logger.info(f"GET /staff/username/{username}")

    staff_member = service.get_by_username(username)

    logger.info(f"Usuario encontrado: {staff_member.full_name}")
    return staff_member


@router.get("/email/{email}", response_model=StaffResponse)
def get_staff_by_email(
    email: str,
    service: StaffService = Depends(get_staff_service),
):
    """
    Obtiene un usuario por email.

    Args:
        email: Email a buscar
        service: Servicio de staff

    Returns:
        Usuario encontrado

    Raises:
        404: Si no se encuentra el usuario

    Example:
        GET /api/v1/staff/email/john.doe@akgroup.com
    """
    logger.info(f"GET /staff/email/{email}")

    staff_member = service.get_by_email(email)

    logger.info(f"Usuario encontrado: {staff_member.full_name}")
    return staff_member


@router.get("/trigram/{trigram}", response_model=StaffResponse)
def get_staff_by_trigram(
    trigram: str,
    service: StaffService = Depends(get_staff_service),
):
    """
    Obtiene un usuario por trigram.

    Args:
        trigram: Trigram a buscar (3 letras)
        service: Servicio de staff

    Returns:
        Usuario encontrado

    Raises:
        404: Si no se encuentra el usuario

    Example:
        GET /api/v1/staff/trigram/JDO
    """
    logger.info(f"GET /staff/trigram/{trigram}")

    staff_member = service.get_by_trigram(trigram)

    logger.info(f"Usuario encontrado: {staff_member.full_name}")
    return staff_member


@router.get("/{staff_id}", response_model=StaffResponse)
def get_staff_by_id(
    staff_id: int,
    service: StaffService = Depends(get_staff_service),
):
    """
    Obtiene un usuario por ID.

    Args:
        staff_id: ID del usuario
        service: Servicio de staff

    Returns:
        Usuario encontrado

    Raises:
        404: Si no se encuentra el usuario

    Example:
        GET /api/v1/staff/123
    """
    logger.info(f"GET /staff/{staff_id}")

    staff_member = service.get_by_id(staff_id)

    logger.info(f"Usuario encontrado: {staff_member.full_name}")
    return staff_member


@router.post("/", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
def create_staff(
    staff_data: StaffCreate,
    service: StaffService = Depends(get_staff_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Crea un nuevo usuario.

    Args:
        staff_data: Datos del usuario a crear
        service: Servicio de staff
        user_id: ID del usuario que crea (para auditoría)

    Returns:
        Usuario creado

    Raises:
        400: Si los datos no son válidos
        409: Si el username, email o trigram ya existen

    Example:
        POST /api/v1/staff
        Body:
        {
            "username": "jdoe",
            "email": "john.doe@akgroup.com",
            "first_name": "John",
            "last_name": "Doe",
            "trigram": "JDO",
            "position": "Desarrollador",
            "is_admin": false,
            "is_active": true
        }
    """
    logger.info(f"POST /staff - username={staff_data.username}")

    staff_member = service.create(staff_data, user_id)

    logger.success(f"Usuario creado: id={staff_member.id}, username={staff_member.username}")
    return staff_member


@router.post("/{staff_id}/activate", response_model=StaffResponse)
def activate_staff(
    staff_id: int,
    service: StaffService = Depends(get_staff_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Activa un usuario desactivado.

    Args:
        staff_id: ID del usuario
        service: Servicio de staff
        user_id: ID del usuario que realiza la operación

    Returns:
        Usuario actualizado

    Raises:
        404: Si no se encuentra el usuario

    Example:
        POST /api/v1/staff/123/activate
    """
    logger.info(f"POST /staff/{staff_id}/activate")

    from src.shared.schemas.core.staff import StaffUpdate
    staff_update = StaffUpdate(is_active=True)
    staff_member = service.update(staff_id, staff_update, user_id)

    logger.success(f"Usuario activado: id={staff_id}")
    return staff_member


@router.post("/{staff_id}/deactivate", response_model=StaffResponse)
def deactivate_staff(
    staff_id: int,
    service: StaffService = Depends(get_staff_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Desactiva un usuario activo.

    Args:
        staff_id: ID del usuario
        service: Servicio de staff
        user_id: ID del usuario que realiza la operación

    Returns:
        Usuario actualizado

    Raises:
        404: Si no se encuentra el usuario

    Example:
        POST /api/v1/staff/123/deactivate
    """
    logger.info(f"POST /staff/{staff_id}/deactivate")

    from src.shared.schemas.core.staff import StaffUpdate
    staff_update = StaffUpdate(is_active=False)
    staff_member = service.update(staff_id, staff_update, user_id)

    logger.success(f"Usuario desactivado: id={staff_id}")
    return staff_member


@router.put("/{staff_id}", response_model=StaffResponse)
def update_staff(
    staff_id: int,
    staff_data: StaffUpdate,
    service: StaffService = Depends(get_staff_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Actualiza un usuario existente.

    Args:
        staff_id: ID del usuario a actualizar
        staff_data: Datos a actualizar
        service: Servicio de staff
        user_id: ID del usuario que actualiza

    Returns:
        Usuario actualizado

    Raises:
        404: Si no se encuentra el usuario
        400: Si los datos no son válidos
        409: Si el username, email o trigram ya existen en otro usuario

    Example:
        PUT /api/v1/staff/123
        Body:
        {
            "position": "Senior Developer",
            "phone": "+56987654321"
        }
    """
    logger.info(f"PUT /staff/{staff_id}")

    staff_member = service.update(staff_id, staff_data, user_id)

    logger.success(f"Usuario actualizado: id={staff_id}")
    return staff_member


@router.delete("/{staff_id}", response_model=MessageResponse)
def delete_staff(
    staff_id: int,
    soft: bool = True,
    service: StaffService = Depends(get_staff_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Elimina un usuario.

    Args:
        staff_id: ID del usuario a eliminar
        soft: Si True, soft delete; si False, hard delete (default: True)
        service: Servicio de staff
        user_id: ID del usuario que elimina

    Returns:
        Mensaje de confirmación

    Raises:
        404: Si no se encuentra el usuario

    Example:
        DELETE /api/v1/staff/123?soft=true
    """
    logger.info(f"DELETE /staff/{staff_id} (soft={soft})")

    service.delete(staff_id, user_id, soft=soft)

    delete_type = "marcado como eliminado" if soft else "eliminado permanentemente"
    logger.success(f"Usuario {delete_type}: id={staff_id}")

    return MessageResponse(
        message=f"Usuario {delete_type} exitosamente",
        details={"staff_id": staff_id, "soft_delete": soft}
    )
