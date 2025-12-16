"""
Repositorios para entidades core.

Este paquete contiene los repositorios de acceso a datos para
las entidades principales del sistema.
"""

from src.backend.repositories.core.company_repository import (
    CompanyRepository,
    CompanyRutRepository,
    PlantRepository,
)
from src.backend.repositories.core.product_repository import (
    ProductRepository,
    ProductComponentRepository,
)
from src.backend.repositories.core.address_repository import AddressRepository
from src.backend.repositories.core.contact_repository import ContactRepository
from src.backend.repositories.core.service_repository import ServiceRepository
from src.backend.repositories.core.staff_repository import StaffRepository
from src.backend.repositories.core.note_repository import NoteRepository

__all__ = [
    # Company
    "CompanyRepository",
    "CompanyRutRepository",
    "PlantRepository",
    # Product
    "ProductRepository",
    "ProductComponentRepository",
    # Address
    "AddressRepository",
    # Contact
    "ContactRepository",
    # Service
    "ServiceRepository",
    # Staff
    "StaffRepository",
    # Note
    "NoteRepository",
]
