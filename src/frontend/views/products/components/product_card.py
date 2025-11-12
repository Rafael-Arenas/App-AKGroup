"""
Componente de tarjeta visual de producto.

Muestra información resumida de un producto en formato de tarjeta.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants


class ProductCard(ft.Container):
    """
    Tarjeta visual de producto con información resumida.

    Args:
        product: Diccionario con datos del producto
        on_click: Callback cuando se hace click en la tarjeta

    Example:
        >>> card = ProductCard(
        ...     product={"id": 1, "name": "Producto A", "code": "PA001"},
        ...     on_click=handle_click,
        ... )
        >>> page.add(card)
    """

    def __init__(
        self,
        product: dict,
        on_click: Callable[[dict], None] | None = None,
    ):
        """Inicializa la tarjeta de producto."""
        super().__init__()
        self.product = product
        self.on_click = on_click

        logger.debug(f"ProductCard initialized: {product.get('name')}")

    def build(self) -> ft.Control:
        """Construye el componente de tarjeta de producto."""
        # Badge de tipo
        product_type = self.product.get("product_type", "")
        is_nomenclature = product_type == "NOMENCLATURE"

        type_badge = ft.Container(
            content=ft.Text(
                "Nomenclatura" if is_nomenclature else "Artículo",
                size=LayoutConstants.FONT_SIZE_XS,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.Colors.WHITE,
            ),
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_XS,
                vertical=2,
            ),
            border_radius=LayoutConstants.RADIUS_SM,
        )

        # Indicador de BOM
        bom_indicator = None
        if is_nomenclature:
            bom_indicator = ft.Container(
                content=ft.Icon(
                    name=ft.Icons.LIST_ALT,
                    size=LayoutConstants.ICON_SIZE_SM,
                ),
                tooltip="Tiene lista de materiales",
            )

        # Costo
        cost = self.product.get("cost", 0)
        cost_text = ft.Text(
            f"${cost:.2f}",
            size=LayoutConstants.FONT_SIZE_LG,
            weight=LayoutConstants.FONT_WEIGHT_BOLD,
        )

        # Contenido de la tarjeta
        card_content = ft.Container(
            content=ft.Column(
                controls=[
                    # Header con ícono y código
                    ft.Row(
                        controls=[
                            ft.Icon(
                                name=ft.Icons.INVENTORY_2,
                                size=LayoutConstants.ICON_SIZE_LG,
                            ),
                            ft.Text(
                                self.product.get("code", ""),
                                size=LayoutConstants.FONT_SIZE_MD,
                                weight=LayoutConstants.FONT_WEIGHT_BOLD,
                            ),
                            bom_indicator if bom_indicator else ft.Container(),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    # Nombre
                    ft.Text(
                        self.product.get("name", ""),
                        size=LayoutConstants.FONT_SIZE_LG,
                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    # Badge de tipo
                    type_badge,
                    # Información adicional
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Unidad:",
                                        size=LayoutConstants.FONT_SIZE_SM,
                                    ),
                                    ft.Text(
                                        self.product.get("unit", "-"),
                                        size=LayoutConstants.FONT_SIZE_MD,
                                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(
                                        "Costo:",
                                        size=LayoutConstants.FONT_SIZE_SM,
                                    ),
                                    cost_text,
                                ],
                                spacing=2,
                                horizontal_alignment=ft.CrossAxisAlignment.END,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
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
        )

        # Contenedor clickeable
        return ft.Container(
            content=card,
            on_click=self._on_card_click,
            ink=True,
        )

    def _on_card_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en la tarjeta."""
        logger.debug(f"ProductCard clicked: {self.product.get('name')}")
        if self.on_click:
            self.on_click(self.product)

    def update_product(self, product: dict) -> None:
        """
        Actualiza los datos del producto en la tarjeta.

        Args:
            product: Nuevos datos del producto

        Example:
            >>> card.update_product(new_product_data)
            >>> card.update()
        """
        self.product = product
        if self.page:
            self.update()
