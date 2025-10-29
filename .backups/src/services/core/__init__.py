"""
Servicios para entidades core.

Este paquete contiene los servicios de lógica de negocio para
las entidades principales del sistema.
"""

from src.services.core.company_service import CompanyService
from src.services.core.product_service import ProductService
from src.services.core.address_service import AddressService
from src.services.core.contact_service import ContactService
from src.services.core.service_service import ServiceService
from src.services.core.staff_service import StaffService
from src.services.core.note_service import NoteService

__all__ = [
    "CompanyService",
    "ProductService",
    "AddressService",
    "ContactService",
    "ServiceService",
    "StaffService",
    "NoteService",
]
