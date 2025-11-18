"""
Vista de detalle de producto.

Muestra información completa de un producto.
Si es nomenclatura, muestra el árbol de componentes (BOM).
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
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

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = LayoutConstants.PADDING_LG

        # Construir contenido inicial (loading)
        self.content = self.build()

        logger.info(f"ProductDetailView initialized: product_id={product_id}")

    def build(self) -> ft.Control:
        """Construye el componente de detalle de producto."""
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
        is_nomenclature = self._product.get("product_type") == "nomenclature"
        type_badge = ft.Container(
            content=ft.Text(
                "Nomenclatura" if is_nomenclature else "Artículo",
                size=LayoutConstants.FONT_SIZE_SM,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.Colors.WHITE,
            ),
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
                color=ft.Colors.WHITE,
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
                    size=LayoutConstants.ICON_SIZE_XL,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            self._product.get("designation_es", ""),
                            size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                            weight=LayoutConstants.FONT_WEIGHT_BOLD,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f"Código: {self._product.get('reference', '')}",
                                    size=LayoutConstants.FONT_SIZE_MD,
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
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Eliminar",
                            on_click=self._on_delete_click,
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_SM,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Información general del producto
        general_info = ft.Column(
            controls=[
                self._create_info_row("Descripción", self._product.get("short_designation", "-") or "-"),
                self._create_info_row("Revisión", self._product.get("revision", "-") or "-"),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        general_card = BaseCard(
            title="Información General",
            icon=ft.Icons.INFO_OUTLINED,
            content=general_info,
        )

        # Información de precios
        pricing_info = ft.Column(
            controls=[
                self._create_info_row(
                    "Precio Compra", f"${float(self._product.get('purchase_price', 0) or 0):.2f}"
                ),
                self._create_info_row(
                    "Precio Costo", f"${float(self._product.get('cost_price', 0) or 0):.2f}"
                ),
                self._create_info_row(
                    "Precio Venta", f"${float(self._product.get('sale_price', 0) or 0):.2f}"
                ),
                self._create_info_row(
                    "Precio Venta EUR", f"€{float(self._product.get('sale_price_eur', 0) or 0):.2f}"
                ),
                self._create_info_row(
                    "Margen %", f"{float(self._product.get('margin_percentage', 0) or 0):.1f}%"
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        pricing_card = BaseCard(
            title="Precios",
            icon=ft.Icons.ATTACH_MONEY,
            content=pricing_info,
        )

        # Información de stock
        stock_info = ft.Column(
            controls=[
                self._create_info_row(
                    "Cantidad en Stock", f"{float(self._product.get('stock_quantity', 0) or 0):.3f}"
                ),
                self._create_info_row(
                    "Stock Mínimo", f"{float(self._product.get('minimum_stock', 0) or 0):.3f}"
                ),
                self._create_info_row(
                    "Ubicación", self._product.get("stock_location", "-") or "-"
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        stock_card = BaseCard(
            title="Inventario",
            icon=ft.Icons.INVENTORY,
            content=stock_info,
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
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_MD,
                ),
            )

        # Contenido
        controls = [header, general_card, pricing_card, stock_card]
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
        return ft.Row(
            controls=[
                ft.Text(
                    f"{label}:",
                    size=LayoutConstants.FONT_SIZE_MD,
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    width=150,
                ),
                ft.Text(
                    value,
                    size=LayoutConstants.FONT_SIZE_MD,
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

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            self._product = await product_api.get_by_id(self.product_id)

            # Si es nomenclatura, cargar componentes BOM
            if self._product.get("product_type") == "nomenclature":
                self._bom_components = await product_api.get_bom_components(
                    self.product_id
                )

            logger.success(f"Product loaded: {self._product.get('designation_es')}")
            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading product: {e}")
            self._error_message = f"Error al cargar producto: {str(e)}"
            self._is_loading = False

        # Reconstruir contenido con los datos cargados
        self.content = self.build()
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
