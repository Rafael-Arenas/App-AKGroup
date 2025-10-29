"""
Endpoints REST para Address.

Proporciona operaciones CRUD sobre direcciones de empresas.
"""

from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.api.dependencies import get_database, get_current_user_id
from src.services.core.address_service import AddressService
from src.repositories.core.address_repository import AddressRepository
from src.schemas.core.address import AddressCreate, AddressUpdate, AddressResponse
from src.schemas.base import MessageResponse
from src.models.core.addresses import AddressType
from src.utils.logger import logger

router = APIRouter(prefix="/addresses", tags=["addresses"])


def get_address_service(db: Session = Depends(get_database)) -> AddressService:
    """
    Dependency para obtener instancia de AddressService.

    Args:
        db: Sesión de base de datos

    Returns:
        Instancia configurada de AddressService
    """
    repository = AddressRepository(db)
    return AddressService(repository=repository, session=db)


@router.get("/", response_model=List[AddressResponse])
def get_addresses(
    skip: int = 0,
    limit: int = 100,
    service: AddressService = Depends(get_address_service),
):
    """
    Obtiene todas las direcciones con paginación.

    Args:
        skip: Número de registros a saltar (default: 0)
        limit: Número máximo de registros (default: 100)
        service: Servicio de direcciones

    Returns:
        Lista de direcciones

    Example:
        GET /api/v1/addresses?skip=0&limit=50
    """
    logger.info(f"GET /addresses - skip={skip}, limit={limit}")

    addresses = service.get_all(skip=skip, limit=limit)

    logger.info(f"Retornando {len(addresses)} dirección(es)")
    return addresses


@router.get("/company/{company_id}", response_model=List[AddressResponse])
def get_addresses_by_company(
    company_id: int,
    service: AddressService = Depends(get_address_service),
):
    """
    Obtiene todas las direcciones de una empresa.

    Args:
        company_id: ID de la empresa
        service: Servicio de direcciones

    Returns:
        Lista de direcciones de la empresa

    Example:
        GET /api/v1/addresses/company/1
    """
    logger.info(f"GET /addresses/company/{company_id}")

    addresses = service.get_by_company(company_id)

    logger.info(f"Retornando {len(addresses)} dirección(es) de empresa id={company_id}")
    return addresses


@router.get("/company/{company_id}/default", response_model=AddressResponse)
def get_default_address(
    company_id: int,
    service: AddressService = Depends(get_address_service),
):
    """
    Obtiene la dirección por defecto de una empresa.

    Args:
        company_id: ID de la empresa
        service: Servicio de direcciones

    Returns:
        Dirección por defecto

    Raises:
        404: Si no se encuentra dirección por defecto

    Example:
        GET /api/v1/addresses/company/1/default
    """
    logger.info(f"GET /addresses/company/{company_id}/default")

    address = service.get_default_address(company_id)

    logger.info(f"Dirección por defecto encontrada para empresa id={company_id}")
    return address


@router.get("/type/{address_type}", response_model=List[AddressResponse])
def get_addresses_by_type(
    company_id: int,
    address_type: AddressType,
    service: AddressService = Depends(get_address_service),
):
    """
    Obtiene direcciones de una empresa por tipo.

    Args:
        company_id: ID de la empresa
        address_type: Tipo de dirección (DELIVERY, BILLING, BOTH)
        service: Servicio de direcciones

    Returns:
        Lista de direcciones del tipo especificado

    Example:
        GET /api/v1/addresses/type/DELIVERY?company_id=1
        GET /api/v1/addresses/type/BILLING?company_id=1
    """
    logger.info(f"GET /addresses/type/{address_type} - company_id={company_id}")

    addresses = service.get_by_type(company_id, address_type)

    logger.info(
        f"Retornando {len(addresses)} dirección(es) tipo {address_type.value} "
        f"de empresa id={company_id}"
    )
    return addresses


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(
    address_id: int,
    service: AddressService = Depends(get_address_service),
):
    """
    Obtiene una dirección por ID.

    Args:
        address_id: ID de la dirección
        service: Servicio de direcciones

    Returns:
        Dirección encontrada

    Raises:
        404: Si no se encuentra la dirección

    Example:
        GET /api/v1/addresses/123
    """
    logger.info(f"GET /addresses/{address_id}")

    address = service.get_by_id(address_id)

    logger.info(f"Dirección encontrada: id={address_id}")
    return address


@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(
    address_data: AddressCreate,
    service: AddressService = Depends(get_address_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Crea una nueva dirección.

    Args:
        address_data: Datos de la dirección a crear
        service: Servicio de direcciones
        user_id: ID del usuario que crea (para auditoría)

    Returns:
        Dirección creada

    Raises:
        400: Si los datos no son válidos

    Example:
        POST /api/v1/addresses
        Body:
        {
            "company_id": 1,
            "address_type": "DELIVERY",
            "street": "Av. Principal 123",
            "city": "Santiago",
            "country": "Chile",
            "is_default": true
        }
    """
    logger.info(f"POST /addresses - company_id={address_data.company_id}")

    address = service.create(address_data, user_id)

    logger.success(f"Dirección creada: id={address.id}, company_id={address.company_id}")
    return address


@router.post("/{address_id}/set-default", response_model=AddressResponse)
def set_default_address(
    address_id: int,
    company_id: int,
    service: AddressService = Depends(get_address_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Establece una dirección como por defecto.

    Args:
        address_id: ID de la dirección
        company_id: ID de la empresa
        service: Servicio de direcciones
        user_id: ID del usuario que realiza la operación

    Returns:
        Dirección actualizada

    Raises:
        404: Si la dirección no existe
        400: Si la dirección no pertenece a la empresa

    Example:
        POST /api/v1/addresses/5/set-default?company_id=1
    """
    logger.info(f"POST /addresses/{address_id}/set-default - company_id={company_id}")

    address = service.set_default_address(address_id, company_id, user_id)

    logger.success(f"Dirección id={address_id} establecida como default")
    return address


@router.put("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    address_data: AddressUpdate,
    service: AddressService = Depends(get_address_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Actualiza una dirección existente.

    Args:
        address_id: ID de la dirección a actualizar
        address_data: Datos a actualizar
        service: Servicio de direcciones
        user_id: ID del usuario que actualiza

    Returns:
        Dirección actualizada

    Raises:
        404: Si no se encuentra la dirección
        400: Si los datos no son válidos

    Example:
        PUT /api/v1/addresses/123
        Body:
        {
            "street": "Nueva Dirección 456",
            "city": "Valparaíso"
        }
    """
    logger.info(f"PUT /addresses/{address_id}")

    address = service.update(address_id, address_data, user_id)

    logger.success(f"Dirección actualizada: id={address_id}")
    return address


@router.delete("/{address_id}", response_model=MessageResponse)
def delete_address(
    address_id: int,
    soft: bool = True,
    service: AddressService = Depends(get_address_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Elimina una dirección.

    Args:
        address_id: ID de la dirección a eliminar
        soft: Si True, soft delete; si False, hard delete (default: True)
        service: Servicio de direcciones
        user_id: ID del usuario que elimina

    Returns:
        Mensaje de confirmación

    Raises:
        404: Si no se encuentra la dirección

    Example:
        DELETE /api/v1/addresses/123?soft=true
    """
    logger.info(f"DELETE /addresses/{address_id} (soft={soft})")

    service.delete(address_id, user_id, soft=soft)

    delete_type = "marcada como eliminada" if soft else "eliminada permanentemente"
    logger.success(f"Dirección {delete_type}: id={address_id}")

    return MessageResponse(
        message=f"Dirección {delete_type} exitosamente",
        details={"address_id": address_id, "soft_delete": soft}
    )
