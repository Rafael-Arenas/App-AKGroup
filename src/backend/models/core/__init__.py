"""
Core models exports.

Este módulo exporta los modelos fundamentales del sistema:
- Staff: Usuarios del sistema
- Note: Sistema polimórfico de notas
- Company, CompanyRut, Plant: Empresas y plantas
- Contact, Service: Contactos y servicios
- Address: Direcciones
- Product, ProductComponent: Sistema unificado de productos

Estado: 6/6 archivos completados (100%)
"""

from .addresses import Address, AddressType
from .companies import Company, CompanyRut, CompanyTypeEnum, Plant
from .contacts import Contact, Service
from .notes import Note, NotePriority
from .products import (
    PriceCalculationMode,
    Product,
    ProductComponent,
    ProductType,
)
from .staff import Staff

__all__ = [
    # Staff
    "Staff",
    # Notes
    "Note",
    "NotePriority",
    # Companies
    "Company",
    "CompanyRut",
    "CompanyTypeEnum",
    "Plant",
    # Contacts
    "Contact",
    "Service",
    # Addresses
    "Address",
    "AddressType",
    # Products
    "Product",
    "ProductComponent",
    "ProductType",
    "PriceCalculationMode",
]
