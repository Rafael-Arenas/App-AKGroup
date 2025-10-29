"""
Servicios para entidades core.

Este paquete contiene los servicios de lógica de negocio para
las entidades principales del sistema.
"""

from src.backend.services.core.company_service import CompanyService
from src.backend.services.core.product_service import ProductService
from src.backend.services.core.address_service import AddressService
from src.backend.services.core.contact_service import ContactService
from src.backend.services.core.service_service import ServiceService
from src.backend.services.core.staff_service import StaffService
from src.backend.services.core.note_service import NoteService

__all__ = [
    "CompanyService",
    "ProductService",
    "AddressService",
    "ContactService",
    "ServiceService",
    "StaffService",
    "NoteService",
]
