"""
Navigation configuration for the application.

Defines the structure and hierarchy of navigation items.
"""
from enum import Enum
import flet as ft


class SectionGroup(Enum):
    """Grupos de secciones en la navegación."""

    DASHBOARD = "dashboard"
    GESTION = "gestion"
    CONFIGURACION = "configuracion"


# Estructura de navegación declarativa
NAVIGATION_STRUCTURE = [
    {
        "group": SectionGroup.DASHBOARD,
        "group_label": None,  # Sin label de grupo
        "items": [
            {
                "index": 0,
                "icon": ft.Icons.DASHBOARD_OUTLINED,
                "icon_selected": ft.Icons.DASHBOARD,
                "label": "dashboard.title",  # i18n key
                "route": "/",
                "description": "dashboard.description",
                "badge": None,
            }
        ],
    },
    {
        "group": SectionGroup.GESTION,
        "group_label": "navigation.management",  # i18n key
        "items": [
            {
                "index": 1,
                "icon": ft.Icons.PEOPLE_OUTLINED,
                "icon_selected": ft.Icons.PEOPLE,
                "label": "clients.title",
                "route": "/companies/clients",
                "description": "clients.description",
                "badge": None,
            },
            {
                "index": 2,
                "icon": ft.Icons.FACTORY_OUTLINED,
                "icon_selected": ft.Icons.FACTORY,
                "label": "suppliers.title",
                "route": "/companies/suppliers",
                "description": "suppliers.description",
                "badge": None,
            },
            {
                "index": 3,
                "icon": ft.Icons.INVENTORY_2_OUTLINED,
                "icon_selected": ft.Icons.INVENTORY_2,
                "label": "articles.title",
                "route": "/articles",
                "description": "articles.description",
                "badge": None,
            },
            {
                "index": 4,
                "icon": ft.Icons.CATEGORY_OUTLINED,
                "icon_selected": ft.Icons.CATEGORY,
                "label": "nomenclatures.title",
                "route": "/nomenclatures",
                "description": "nomenclatures.description",
                "badge": None,
            },
            {
                "index": 5,
                "icon": ft.Icons.DESCRIPTION_OUTLINED,
                "icon_selected": ft.Icons.DESCRIPTION,
                "label": "quotes.title",
                "route": "/quotes",
                "description": "quotes.description",
                "badge": None,
            },
            {
                "index": 6,
                "icon": ft.Icons.SHOPPING_CART_OUTLINED,
                "icon_selected": ft.Icons.SHOPPING_CART,
                "label": "orders.title",
                "route": "/orders",
                "description": "orders.description",
                "badge": None,
            },
            {
                "index": 7,
                "icon": ft.Icons.RECEIPT_LONG_OUTLINED,
                "icon_selected": ft.Icons.RECEIPT_LONG,
                "label": "invoices.title",
                "route": "/invoices",
                "description": "invoices.description",
                "badge": None,
            },
        ],
    },
    {
        "group": SectionGroup.CONFIGURACION,
        "group_label": "navigation.settings",  # i18n key
        "items": [
            {
                "index": 8,
                "icon": ft.Icons.BADGE_OUTLINED,
                "icon_selected": ft.Icons.BADGE,
                "label": "staff.title",
                "route": "/staff",
                "description": "staff.description",
                "badge": None,
            },
            {
                "index": 9,
                "icon": ft.Icons.SETTINGS_OUTLINED,
                "icon_selected": ft.Icons.SETTINGS,
                "label": "settings.title",
                "route": "/settings",
                "description": "settings.description",
                "badge": None,
            },
        ],
    },
]


def get_navigation_item_by_index(index: int) -> dict | None:
    """
    Obtiene un item de navegación por su índice.

    Args:
        index: Índice del item de navegación

    Returns:
        Diccionario con datos del item o None si no existe

    Example:
        >>> item = get_navigation_item_by_index(1)
        >>> item["label"]
        "companies.title"
    """
    for group in NAVIGATION_STRUCTURE:
        for item in group["items"]:
            if item["index"] == index:
                return item
    return None


def get_navigation_item_by_route(route: str) -> dict | None:
    """
    Obtiene un item de navegación por su ruta.

    Args:
        route: Ruta del item (ej: "/companies")

    Returns:
        Diccionario con datos del item o None si no existe

    Example:
        >>> item = get_navigation_item_by_route("/companies")
        >>> item["index"]
        1
    """
    for group in NAVIGATION_STRUCTURE:
        for item in group["items"]:
            if item["route"] == route:
                return item
    return None


def get_all_navigation_items() -> list[dict]:
    """
    Obtiene todos los items de navegación en una lista plana.

    Returns:
        Lista de diccionarios con todos los items

    Example:
        >>> items = get_all_navigation_items()
        >>> len(items)
        10
    """
    items = []
    for group in NAVIGATION_STRUCTURE:
        items.extend(group["items"])
    return items


def get_navigation_groups() -> list[dict]:
    """
    Obtiene todos los grupos de navegación.

    Returns:
        Lista de grupos con sus items

    Example:
        >>> groups = get_navigation_groups()
        >>> groups[1]["group"]
        SectionGroup.GESTION
    """
    return NAVIGATION_STRUCTURE
