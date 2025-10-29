"""
Repositorios para entidades core.

Este paquete contiene los repositorios de acceso a datos para
las entidades principales del sistema.
"""

from src.repositories.core.company_repository import (
    CompanyRepository,
    CompanyRutRepository,
    BranchRepository,
)
from src.repositories.core.product_repository import (
    ProductRepository,
    ProductComponentRepository,
)
from src.repositories.core.address_repository import AddressRepository
from src.repositories.core.contact_repository import ContactRepository
from src.repositories.core.service_repository import ServiceRepository
from src.repositories.core.staff_repository import StaffRepository
from src.repositories.core.note_repository import NoteRepository

__all__ = [
    # Company
    "CompanyRepository",
    "CompanyRutRepository",
    "BranchRepository",
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
