"""
API services para comunicación con el backend FastAPI.

Este módulo proporciona instancias singleton de los servicios API
para facilitar el acceso desde la aplicación frontend.
"""

from .base_api_client import (
    BaseAPIClient,
    APIException,
    NetworkException,
    ValidationException,
    NotFoundException,
    UnauthorizedException,
)
from .company_api import CompanyAPIService
from .product_api import ProductAPIService
from .lookup_api import LookupAPIService
from .plant_api import PlantAPIService
from .quote_api import QuoteAPIService
from .contact_api import ContactAPIService
from .company_rut_api import CompanyRutAPIService
from .staff_api import StaffAPIService
from .config import APISettings, api_settings


# Aliases para compatibilidad con los nombres usados en las vistas
CompanyAPI = CompanyAPIService
ProductAPI = ProductAPIService
LookupAPI = LookupAPIService
PlantAPI = PlantAPIService
QuoteAPI = QuoteAPIService
ContactAPI = ContactAPIService
CompanyRutAPI = CompanyRutAPIService
StaffAPI = StaffAPIService

# Instancias singleton de servicios
# Estas instancias pueden ser importadas y reutilizadas en toda la aplicación
company_api = CompanyAPIService()
product_api = ProductAPIService()
lookup_api = LookupAPIService()
plant_api = PlantAPIService()
quote_api = QuoteAPIService()
contact_api = ContactAPIService()
company_rut_api = CompanyRutAPIService()
staff_api = StaffAPIService()


__all__ = [
    # Cliente base
    "BaseAPIClient",
    # Excepciones
    "APIException",
    "NetworkException",
    "ValidationException",
    "NotFoundException",
    "UnauthorizedException",
    # Servicios
    "CompanyAPIService",
    "ProductAPIService",
    "LookupAPIService",
    "PlantAPIService",
    "QuoteAPIService",
    "ContactAPIService",
    "CompanyRutAPIService",
    "StaffAPIService",
    # Aliases
    "CompanyAPI",
    "ProductAPI",
    "LookupAPI",
    "PlantAPI",
    "QuoteAPI",
    "ContactAPI",
    "CompanyRutAPI",
    "StaffAPI",
    # Instancias singleton
    "company_api",
    "product_api",
    "lookup_api",
    "plant_api",
    "quote_api",
    "contact_api",
    "company_rut_api",
    "staff_api",
    # Configuración
    "APISettings",
    "api_settings",
]
