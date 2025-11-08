"""
Componente de tarjeta visual de empresa.

Muestra información resumida de una empresa en formato de tarjeta.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.color_constants import ColorConstants
from src.frontend.layout_constants import LayoutConstants


class CompanyCard(ft.Container):
    """
    Tarjeta visual de empresa con información resumida.

    Args:
        company: Diccionario con datos de la empresa
        on_click: Callback cuando se hace click en la tarjeta

    Example:
        >>> card = CompanyCard(
        ...     company={"id": 1, "name": "ABC Corp", "trigram": "ABC"},
        ...     on_click=handle_click,
        ... )
        >>> page.add(card)
    """

    def __init__(
        self,
        company: dict,
        on_click: Callable[[dict], None] | None = None,
    ):
        """Inicializa la tarjeta de empresa."""
        super().__init__()
        self.company = company
        self.on_click = on_click

        logger.debug(f"CompanyCard initialized: {company.get('name')}")

    def build(self) -> ft.Control:
        """Construye el componente de tarjeta de empresa."""
        is_dark = app_state.theme.is_dark_mode

        # Badge de tipo
        company_type = self.company.get("company_type", "")
        type_badge = self._create_type_badge(company_type)

        # Badge de estado
        is_active = self.company.get("is_active", True)
        status_badge = ft.Container(
            content=ft.Text(
                "Activa" if is_active else "Inactiva",
                size=LayoutConstants.FONT_SIZE_XS,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.Colors.WHITE,
            ),
            bgcolor=ColorConstants.SUCCESS if is_active else ColorConstants.ERROR,
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_XS,
                vertical=2,
            ),
            border_radius=LayoutConstants.RADIUS_SM,
        )

        # Contenido de la tarjeta
        card_content = ft.Container(
            content=ft.Column(
                controls=[
                    # Header con ícono
                    ft.Row(
                        controls=[
                            ft.Icon(
                                name=ft.Icons.BUSINESS,
                                color=ColorConstants.PRIMARY,
                                size=LayoutConstants.ICON_SIZE_LG,
                            ),
                            ft.Text(
                                self.company.get("trigram", ""),
                                size=LayoutConstants.FONT_SIZE_MD,
                                weight=LayoutConstants.FONT_WEIGHT_BOLD,
                                color=ColorConstants.PRIMARY,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    # Nombre
                    ft.Text(
                        self.company.get("name", ""),
                        size=LayoutConstants.FONT_SIZE_LG,
                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                        color=ColorConstants.get_color_for_theme("ON_SURFACE", is_dark),
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    # Badges
                    ft.Row(
                        controls=[type_badge, status_badge],
                        spacing=LayoutConstants.SPACING_XS,
                        wrap=True,
                    ),
                    # Información adicional
                    ft.Column(
                        controls=[
                            self._create_info_line(
                                ft.Icons.PHONE,
                                self.company.get("phone", "-"),
                            ),
                            self._create_info_line(
                                ft.Icons.EMAIL,
                                self.company.get("email", "-"),
                            ),
                        ],
                        spacing=LayoutConstants.SPACING_XS,
                    ),
                ],
                spacing=LayoutConstants.SPACING_SM,
            ),
            padding=LayoutConstants.PADDING_MD,
        )

        # Tarjeta clickeable
        card = ft.Card(
            content=card_content,
            elevation=LayoutConstants.ELEVATION_LOW,
            color=ColorConstants.get_color_for_theme("CARD_BACKGROUND", is_dark),
        )

        # Contenedor clickeable
        return ft.Container(
            content=card,
            on_click=self._on_card_click,
            ink=True,
        )

    def _create_type_badge(self, type_code: str) -> ft.Container:
        """Crea el badge de tipo de empresa."""
        type_map = {
            "CLIENT": ("Cliente", ColorConstants.INFO),
            "SUPPLIER": ("Proveedor", ColorConstants.WARNING),
            "BOTH": ("Cliente/Proveedor", ColorConstants.PRIMARY),
        }

        label, color = type_map.get(type_code, (type_code, ColorConstants.INFO))

        return ft.Container(
            content=ft.Text(
                label,
                size=LayoutConstants.FONT_SIZE_XS,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.Colors.WHITE,
            ),
            bgcolor=color,
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_XS,
                vertical=2,
            ),
            border_radius=LayoutConstants.RADIUS_SM,
        )

    def _create_info_line(self, icon: str, text: str) -> ft.Row:
        """Crea una línea de información con ícono."""
        is_dark = app_state.theme.is_dark_mode

        return ft.Row(
            controls=[
                ft.Icon(
                    name=icon,
                    size=LayoutConstants.ICON_SIZE_SM,
                    color=ColorConstants.get_color_for_theme(
                        "ON_SURFACE_VARIANT", is_dark
                    ),
                ),
                ft.Text(
                    text,
                    size=LayoutConstants.FONT_SIZE_SM,
                    color=ColorConstants.get_color_for_theme(
                        "ON_SURFACE_VARIANT", is_dark
                    ),
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
            spacing=LayoutConstants.SPACING_XS,
        )

    def _on_card_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en la tarjeta."""
        logger.debug(f"CompanyCard clicked: {self.company.get('name')}")
        if self.on_click:
            self.on_click(self.company)

    def update_company(self, company: dict) -> None:
        """
        Actualiza los datos de la empresa en la tarjeta.

        Args:
            company: Nuevos datos de la empresa

        Example:
            >>> card.update_company(new_company_data)
            >>> card.update()
        """
        self.company = company
        if self.page:
            self.update()
