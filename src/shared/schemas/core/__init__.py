"""
Schemas para entidades core.

Este paquete contiene los schemas de Pydantic para las entidades
principales del sistema (staff, companies, products, etc.).
"""

from src.shared.schemas.core.company import (
    CompanyCreate,
    CompanyUpdate,
    CompanyResponse,
    CompanyRutCreate,
    CompanyRutResponse,
    BranchCreate,
    BranchUpdate,
    BranchResponse,
)
from src.shared.schemas.core.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductComponentCreate,
    ProductComponentUpdate,
    ProductComponentResponse,
)
from src.shared.schemas.core.address import (
    AddressCreate,
    AddressUpdate,
    AddressResponse,
)
from src.shared.schemas.core.contact import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
)
from src.shared.schemas.core.service import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
)
from src.shared.schemas.core.staff import (
    StaffCreate,
    StaffUpdate,
    StaffResponse,
)
from src.shared.schemas.core.note import (
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
