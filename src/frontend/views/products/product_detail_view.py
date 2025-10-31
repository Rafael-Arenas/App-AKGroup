"""
Vista de detalle de producto.

Muestra información completa de un producto.
Si es nomenclatura, muestra el árbol de componentes (BOM).
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.color_constants import ColorConstants
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import BaseCard, LoadingSpinner, ErrorDisplay, ConfirmDialog


class ProductDetailView(ft.Container):
    """
    Vista de detalle de producto con BOM si es nomenclatura.

    Args:
        product_id: ID del producto a mostrar
        on_edit: Callback cuando se edita el producto
        on_delete: Callback cuando se elimina el producto
        on_back: Callback para volver atrás

    Example:
        >>> detail = ProductDetailView(product_id=123, on_edit=handle_edit)
        >>> page.add(detail)
    """

    def __init__(
        self,
        product_id: int,
        on_edit: Callable[[int], None] | None = None,
        on_delete: Callable[[int], None] | None = None,
        on_back: Callable[[], None] | None = None,
    ):
        """Inicializa la vista de detalle de producto."""
        super().__init__()
        self.product_id = product_id
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_back = on_back

        self._is_loading: bool = True
        self._error_message: str = ""
        self._product: dict | None = None
        self._bom_components: list[dict] = []

        logger.info(f"ProductDetailView initialized: product_id={product_id}")

    def build(self) -> ft.Control:
        """Construye el componente de detalle de producto."""
        is_dark = app_state.theme.is_dark_mode

        if self._is_loading:
            return ft.Container(
                content=LoadingSpinner(message="Cargando producto..."),
                expand=True,
                alignment=ft.alignment.center,
            )
        elif self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_product,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )

        # Badge de tipo
        is_nomenclature = self._product.get("product_type") == "NOMENCLATURE"
        type_badge = ft.Container(
            content=ft.Text(
                "Nomenclatura" if is_nomenclature else "Artículo",
                size=LayoutConstants.FONT_SIZE_SM,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.colors.WHITE,
            ),
            bgcolor=ColorConstants.PRIMARY if is_nomenclature else ColorConstants.INFO,
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_SM,
                vertical=LayoutConstants.PADDING_XS,
            ),
            border_radius=LayoutConstants.RADIUS_SM,
        )

        status_badge = ft.Container(
            content=ft.Text(
                "Activo" if self._product.get("is_active") else "Inactivo",
                size=LayoutConstants.FONT_SIZE_SM,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.colors.WHITE,
            ),
            bgcolor=(
                ColorConstants.SUCCESS
                if self._product.get("is_active")
                else ColorConstants.ERROR
            ),
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_SM,
                vertical=LayoutConstants.PADDING_XS,
            ),
            border_radius=LayoutConstants.RADIUS_SM,
        )

        # Header
        header = ft.Row(
            controls=[
                ft.Icon(
                    name=ft.Icons.INVENTORY_2,
                    color=ColorConstants.PRIMARY,
                    size=LayoutConstants.ICON_SIZE_XL,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            self._product.get("name", ""),
                            size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                            weight=LayoutConstants.FONT_WEIGHT_BOLD,
                            color=ColorConstants.get_color_for_theme("ON_SURFACE", is_dark),
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f"Código: {self._product.get('code', '')}",
                                    size=LayoutConstants.FONT_SIZE_MD,
                                    color=ColorConstants.get_color_for_theme(
                                        "ON_SURFACE_VARIANT", is_dark
                                    ),
                                ),
                                type_badge,
                                status_badge,
                            ],
                            spacing=LayoutConstants.SPACING_SM,
                        ),
                    ],
                    expand=True,
                    spacing=LayoutConstants.SPACING_XS,
                ),
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            tooltip="Editar",
                            on_click=self._on_edit_click,
                            bgcolor=ColorConstants.PRIMARY,
                            icon_color=ft.colors.WHITE,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Eliminar",
                            on_click=self._on_delete_click,
                            bgcolor=ColorConstants.ERROR,
                            icon_color=ft.colors.WHITE,
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_SM,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Información del producto
        info_content = ft.Column(
            controls=[
                self._create_info_row("Descripción", self._product.get("description", "-")),
                ft.Divider(),
                self._create_info_row("Unidad", self._product.get("unit", "-")),
                self._create_info_row(
                    "Costo", f"${self._product.get('cost', 0):.2f}"
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        info_card = BaseCard(
            title="Información del Producto",
            icon=ft.Icons.INFO_OUTLINED,
            content=info_content,
        )

        # Sección BOM (solo si es nomenclatura)
        bom_section = None
        if is_nomenclature:
            bom_content = self._create_bom_tree()
            total_cost = self._calculate_total_cost()

            bom_section = BaseCard(
                title="Lista de Materiales (BOM)",
                icon=ft.Icons.LIST_ALT,
                content=ft.Column(
                    controls=[
                        bom_content,
                        ft.Divider(),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    "Costo Total:",
                                    size=LayoutConstants.FONT_SIZE_LG,
                                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                                ),
                                ft.Text(
                                    f"${total_cost:.2f}",
                                    size=LayoutConstants.FONT_SIZE_LG,
                                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                                    color=ColorConstants.PRIMARY,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_MD,
                ),
            )

        # Botón volver
        back_button = ft.TextButton(
            text="Volver",
            icon=ft.Icons.ARROW_BACK,
            on_click=self._on_back_click,
        )

        # Contenido
        controls = [back_button, header, info_card]
        if bom_section:
            controls.append(bom_section)

        content = ft.Column(
            controls=controls,
            spacing=LayoutConstants.SPACING_LG,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        return content

    def _create_info_row(self, label: str, value: str) -> ft.Row:
        """Crea una fila de información."""
        is_dark = app_state.theme.is_dark_mode

        return ft.Row(
            controls=[
                ft.Text(
                    f"{label}:",
                    size=LayoutConstants.FONT_SIZE_MD,
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    color=ColorConstants.get_color_for_theme("ON_SURFACE", is_dark),
                    width=150,
                ),
                ft.Text(
                    value,
                    size=LayoutConstants.FONT_SIZE_MD,
                    color=ColorConstants.get_color_for_theme(
                        "ON_SURFACE_VARIANT", is_dark
                    ),
                    expand=True,
                ),
            ],
        )

    def _create_bom_tree(self) -> ft.Control:
        """Crea el árbol de componentes BOM."""
        if not self._bom_components:
            return ft.Text("No hay componentes en el BOM")

        # Crear tabla de componentes
        rows = []
        for comp in self._bom_components:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(comp.get("component_code", ""))),
                        ft.DataCell(ft.Text(comp.get("component_name", ""))),
                        ft.DataCell(ft.Text(str(comp.get("quantity", 0)))),
                        ft.DataCell(
                            ft.Text(f"${comp.get('unit_cost', 0):.2f}")
                        ),
                        ft.DataCell(
                            ft.Text(
                                f"${comp.get('quantity', 0) * comp.get('unit_cost', 0):.2f}"
                            )
                        ),
                    ],
                )
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Cantidad")),
                ft.DataColumn(ft.Text("Costo Unit.")),
                ft.DataColumn(ft.Text("Costo Total")),
            ],
            rows=rows,
        )

        return ft.Container(
            content=table,
            border=ft.border.all(1, ColorConstants.BORDER_LIGHT),
            border_radius=LayoutConstants.RADIUS_SM,
            padding=LayoutConstants.PADDING_SM,
        )

    def _calculate_total_cost(self) -> float:
        """Calcula el costo total del BOM."""
        total = 0.0
        for comp in self._bom_components:
            total += comp.get("quantity", 0) * comp.get("unit_cost", 0)
        return total

    def did_mount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.info("ProductDetailView mounted")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        if self.page:
            self.page.run_task(self.load_product)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_product(self) -> None:
        """Carga los datos del producto desde la API."""
        logger.info(f"Loading product ID={self.product_id}")
        self._is_loading = True
        self._error_message = ""

        if self.page:
            self.update()

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            self._product = await product_api.get_by_id(self.product_id)

            # Si es nomenclatura, cargar componentes BOM
            if self._product.get("product_type") == "NOMENCLATURE":
                self._bom_components = await product_api.get_bom_components(
                    self.product_id
                )

            logger.success(f"Product loaded: {self._product.get('name')}")
            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading product: {e}")
            self._error_message = f"Error al cargar producto: {str(e)}"
            self._is_loading = False

        if self.page:
            self.update()

    def _on_edit_click(self, e: ft.ControlEvent) -> None:
        """Callback para editar el producto."""
        if self.on_edit:
            self.on_edit(self.product_id)

    def _on_delete_click(self, e: ft.ControlEvent) -> None:
        """Callback para eliminar el producto."""
        # TODO: Mostrar diálogo de confirmación
        if self.on_delete:
            self.on_delete(self.product_id)

    def _on_back_click(self, e: ft.ControlEvent) -> None:
        """Callback para volver atrás."""
        if self.on_back:
            self.on_back()

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        if self.page:
            self.update()
