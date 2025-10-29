"""
Schemas para entidades core.

Este paquete contiene los schemas de Pydantic para las entidades
principales del sistema (staff, companies, products, etc.).
"""

from src.schemas.core.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyRutCreate,
    CompanyRutResponse,
    BranchCreate,
    BranchUpdate,
    BranchResponse,
)
from src.schemas.core.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductComponentCreate,
    ProductComponentUpdate,
    ProductComponentResponse,
)
from src.schemas.core.address import (
    AddressCreate,
    AddressUpdate,
    AddressResponse,
)
from src.schemas.core.contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
)
from src.schemas.core.service import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
)
from src.schemas.core.staff import (
    StaffCreate,
    StaffUpdate,
    StaffResponse,
)
from src.schemas.core.note import (
    NoteCreate,
    NoteUpdate,
    NoteResponse,
)

__all__ = [
    # Company
    "CompanyCreate",
    "CompanyUpdate",
    "CompanyResponse",
    "CompanyRutCreate",
    "CompanyRutResponse",
    "BranchCreate",
    "BranchUpdate",
    "BranchResponse",
    # Product
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductComponentCreate",
    "ProductComponentUpdate",
    "ProductComponentResponse",
    # Address
    "AddressCreate",
    "AddressUpdate",
    "AddressResponse",
    # Contact
    "ContactCreate",
    "ContactUpdate",
    "ContactResponse",
    # Service
    "ServiceCreate",
    "ServiceUpdate",
    "ServiceResponse",
    # Staff
    "StaffCreate",
    "StaffUpdate",
    "StaffResponse",
    # Note
    "NoteCreate",
    "NoteUpdate",
    "NoteResponse",
]
