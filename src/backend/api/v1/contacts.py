"""
Endpoints REST para Contact.

Proporciona operaciones CRUD sobre contactos de empresas.
"""

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.backend.api.dependencies import get_database, get_current_user_id
from src.backend.services.core.contact_service import ContactService
from src.backend.repositories.core.contact_repository import ContactRepository
from src.shared.schemas.core.contact import ContactCreate, ContactUpdate, ContactResponse
from src.shared.schemas.base import MessageResponse
from src.backend.utils.logger import logger

router = APIRouter(prefix="/contacts", tags=["contacts"])


def get_contact_service(db: Session = Depends(get_database)) -> ContactService:
    """
    Dependency para obtener instancia de ContactService.

    Args:
        db: Sesión de base de datos

    Returns:
        Instancia configurada de ContactService
    """
    repository = ContactRepository(db)
    return ContactService(repository=repository, session=db)


@router.get("/", response_model=List[ContactResponse])
def get_contacts(
    skip: int = 0,
    limit: int = 100,
    service: ContactService = Depends(get_contact_service),
):
    """
    Obtiene todos los contactos con paginación.

    Args:
        skip: Número de registros a saltar (default: 0)
        limit: Número máximo de registros (default: 100)
        service: Servicio de contactos

    Returns:
        Lista de contactos

    Example:
        GET /api/v1/contacts?skip=0&limit=50
    """
    logger.info(f"GET /contacts - skip={skip}, limit={limit}")

    contacts = service.get_all(skip=skip, limit=limit)

    logger.info(f"Retornando {len(contacts)} contacto(s)")
    return contacts


@router.get("/company/{company_id}", response_model=List[ContactResponse])
def get_contacts_by_company(
    company_id: int,
    service: ContactService = Depends(get_contact_service),
):
    """
    Obtiene todos los contactos de una empresa.

    Args:
        company_id: ID de la empresa
        service: Servicio de contactos

    Returns:
        Lista de contactos de la empresa

    Example:
        GET /api/v1/contacts/company/1
    """
    logger.info(f"GET /contacts/company/{company_id}")

    contacts = service.get_by_company(company_id)

    logger.info(f"Retornando {len(contacts)} contacto(s) de empresa id={company_id}")
    return contacts


@router.get("/search/name/{name}", response_model=List[ContactResponse])
def search_contacts_by_name(
    company_id: int,
    name: str,
    service: ContactService = Depends(get_contact_service),
):
    """
    Busca contactos por nombre (búsqueda parcial).

    Args:
        company_id: ID de la empresa
        name: Texto a buscar en el nombre
        service: Servicio de contactos

    Returns:
        Lista de contactos que coinciden

    Example:
        GET /api/v1/contacts/search/name/juan?company_id=1
    """
    logger.info(f"GET /contacts/search/name/{name} - company_id={company_id}")

    contacts = service.search_by_name(company_id, name)

    logger.info(f"Búsqueda '{name}' retornó {len(contacts)} contacto(s)")
    return contacts


@router.get("/search/email/{email}", response_model=ContactResponse)
def get_contact_by_email(
    email: str,
    service: ContactService = Depends(get_contact_service),
):
    """
    Obtiene un contacto por email.

    Args:
        email: Email del contacto
        service: Servicio de contactos

    Returns:
        Contacto encontrado

    Raises:
        404: Si no se encuentra el contacto

    Example:
        GET /api/v1/contacts/search/email/jperez@example.com
    """
    logger.info(f"GET /contacts/search/email/{email}")

    contact = service.get_by_email(email)

    logger.info(f"Contacto encontrado: {contact.full_name}")
    return contact


@router.get("/service/{service_id}", response_model=List[ContactResponse])
def get_contacts_by_service(
    service_id: int,
    service: ContactService = Depends(get_contact_service),
):
    """
    Obtiene todos los contactos de un servicio/departamento.

    Args:
        service_id: ID del servicio
        service: Servicio de contactos

    Returns:
        Lista de contactos del servicio

    Example:
        GET /api/v1/contacts/service/1
    """
    logger.info(f"GET /contacts/service/{service_id}")

    contacts = service.get_by_service(service_id)

    logger.info(f"Retornando {len(contacts)} contacto(s) del servicio id={service_id}")
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: int,
    service: ContactService = Depends(get_contact_service),
):
    """
    Obtiene un contacto por ID.

    Args:
        contact_id: ID del contacto
        service: Servicio de contactos

    Returns:
        Contacto encontrado

    Raises:
        404: Si no se encuentra el contacto

    Example:
        GET /api/v1/contacts/123
    """
    logger.info(f"GET /contacts/{contact_id}")

    contact = service.get_by_id(contact_id)

    logger.info(f"Contacto encontrado: {contact.full_name}")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact_data: ContactCreate,
    service: ContactService = Depends(get_contact_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Crea un nuevo contacto.

    Args:
        contact_data: Datos del contacto a crear
        service: Servicio de contactos
        user_id: ID del usuario que crea (para auditoría)

    Returns:
        Contacto creado

    Raises:
        400: Si los datos no son válidos
        409: Si el email ya existe

    Example:
        POST /api/v1/contacts
        Body:
        {
            "company_id": 1,
            "first_name": "Juan",
            "last_name": "Pérez",
            "email": "jperez@example.com",
            "phone": "+56912345678",
            "position": "Gerente de Ventas",
            "service_id": 1
        }
    """
    logger.info(f"POST /contacts - company_id={contact_data.company_id}")

    contact = service.create(contact_data, user_id)

    logger.success(f"Contacto creado: id={contact.id}, nombre={contact.full_name}")
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    service: ContactService = Depends(get_contact_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Actualiza un contacto existente.

    Args:
        contact_id: ID del contacto a actualizar
        contact_data: Datos a actualizar
        service: Servicio de contactos
        user_id: ID del usuario que actualiza

    Returns:
        Contacto actualizado

    Raises:
        404: Si no se encuentra el contacto
        400: Si los datos no son válidos
        409: Si el email ya existe en otro contacto

    Example:
        PUT /api/v1/contacts/123
        Body:
        {
            "phone": "+56987654321",
            "position": "Gerente General"
        }
    """
    logger.info(f"PUT /contacts/{contact_id}")

    contact = service.update(contact_id, contact_data, user_id)

    logger.success(f"Contacto actualizado: id={contact_id}")
    return contact


@router.delete("/{contact_id}", response_model=MessageResponse)
def delete_contact(
    contact_id: int,
    soft: bool = True,
    service: ContactService = Depends(get_contact_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Elimina un contacto.

    Args:
        contact_id: ID del contacto a eliminar
        soft: Si True, soft delete; si False, hard delete (default: True)
        service: Servicio de contactos
        user_id: ID del usuario que elimina

    Returns:
        Mensaje de confirmación

    Raises:
        404: Si no se encuentra el contacto

    Example:
        DELETE /api/v1/contacts/123?soft=true
    """
    logger.info(f"DELETE /contacts/{contact_id} (soft={soft})")

    service.delete(contact_id, user_id, soft=soft)

    delete_type = "marcado como eliminado" if soft else "eliminado permanentemente"
    logger.success(f"Contacto {delete_type}: id={contact_id}")

    return MessageResponse(
        message=f"Contacto {delete_type} exitosamente",
        details={"contact_id": contact_id, "soft_delete": soft}
    )
