"""
Módulo de navegación especializada.

Proporciona navegadores especializados para cada tipo de entidad de la aplicación.
"""
from src.frontend.navigation.base_navigator import BaseNavigator
from src.frontend.navigation.company_navigator import CompanyNavigator
from src.frontend.navigation.article_navigator import ArticleNavigator
from src.frontend.navigation.nomenclature_navigator import NomenclatureNavigator
from src.frontend.navigation.quote_navigator import QuoteNavigator
from src.frontend.navigation.order_navigator import OrderNavigator
from src.frontend.navigation.invoice_navigator import InvoiceNavigator
from src.frontend.navigation.staff_navigator import StaffNavigator

__all__ = [
    "BaseNavigator",
    "CompanyNavigator",
    "ArticleNavigator",
    "NomenclatureNavigator",
    "QuoteNavigator",
    "OrderNavigator",
    "InvoiceNavigator",
    "StaffNavigator",
]

