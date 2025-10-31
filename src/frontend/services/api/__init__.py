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
from .config import APISettings, api_settings


# Aliases para compatibilidad con los nombres usados en las vistas
CompanyAPI = CompanyAPIService
ProductAPI = ProductAPIService
LookupAPI = LookupAPIService

# Instancias singleton de servicios
# Estas instancias pueden ser importadas y reutilizadas en toda la aplicación
company_api = CompanyAPIService()
product_api = ProductAPIService()
lookup_api = LookupAPIService()


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
    # Aliases
    "CompanyAPI",
    "ProductAPI",
    "LookupAPI",
    # Instancias singleton
    "company_api",
    "product_api",
    "lookup_api",
    # Configuración
    "APISettings",
    "api_settings",
]
