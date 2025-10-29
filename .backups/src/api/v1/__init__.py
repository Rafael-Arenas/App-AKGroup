"""
API v1 - Endpoints REST.

Este paquete contiene todos los endpoints de la versión 1 de la API.
"""

from src.api.v1.companies import router as companies_router
from src.api.v1.products import router as products_router
from src.api.v1.addresses import router as addresses_router
from src.api.v1.contacts import router as contacts_router
from src.api.v1.services import router as services_router
from src.api.v1.staff import router as staff_router
from src.api.v1.notes import router as notes_router
from src.api.v1.quotes import router as quotes_router
from src.api.v1.orders import router as orders_router
from src.api.v1.deliveries import deliveries_router
from src.api.v1.invoices import invoices_router
from src.api.v1.lookups import lookups_router

__all__ = [
    "companies_router",
    "products_router",
    "addresses_router",
    "contacts_router",
    "services_router",
    "staff_router",
    "notes_router",
    "quotes_router",
    "orders_router",
    "deliveries_router",
    "invoices_router",
    "lookups_router",
]
