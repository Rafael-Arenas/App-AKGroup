"""
Vista de listado de productos.

Muestra una tabla de productos con filtros, búsqueda y paginación.
Similar a CompanyListView pero con campos específicos de productos.
"""
from typing import Any
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import (
    SearchBar,
    FilterPanel,
    DataTable,
    LoadingSpinner,
    ErrorDisplay,
    EmptyState,
    ConfirmDialog,
)


class ProductListView(ft.Container):
    """
    Vista de listado de productos con filtros y paginación.

    Example:
        >>> product_list = ProductListView()
        >>> page.add(product_list)
    """

    def __init__(self):
        """Inicializa la vista de listado de productos."""
        super().__init__()

        self._is_loading: bool = True
        self._error_message: str = ""
        self._products: list[dict] = []
        self._total_products: int = 0
        self._current_page: int = 1
        self._page_size: int = 20

        self._search_query: str = ""
        self._status_filter: str = "all"
        self._type_filter: str = "all"

        self._search_bar: SearchBar | None = None
        self._filter_panel: FilterPanel | None = None
        self._data_table: DataTable | None = None

        logger.info("ProductListView initialized")

    def build(self) -> ft.Control:
        """Construye el componente de listado de productos."""
        header = ft.Row(
            controls=[
                ft.Text(
                    "Productos",
                    size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                    expand=True,
                ),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    text="Crear Producto",
                    on_click=self._on_create_product,
                ),
            ],
        )

        self._search_bar = SearchBar(
            placeholder="Buscar productos por código o nombre...",
            on_search=self._on_search,
        )

        self._filter_panel = FilterPanel(
            filters=[
                {
                    "key": "status",
                    "label": "products.filters.status",
                    "type": "dropdown",
                    "options": [
                        {"label": "products.filters.all", "value": "all"},
                        {"label": "products.filters.active", "value": "active"},
                        {"label": "products.filters.inactive", "value": "inactive"},
                    ],
                    "default": "all",
                },
                {
                    "key": "type",
                    "label": "products.filters.type",
                    "type": "dropdown",
                    "options": [
                        {"label": "products.filters.all", "value": "all"},
                        {"label": "products.filters.article", "value": "ARTICLE"},
                        {"label": "products.filters.nomenclature", "value": "NOMENCLATURE"},
                    ],
                    "default": "all",
                },
            ],
            on_filter_change=self._on_filter_change,
        )

        self._data_table = DataTable(
            columns=[
                {"key": "code", "label": "products.columns.code", "sortable": True},
                {"key": "name", "label": "products.columns.name", "sortable": True},
                {"key": "type", "label": "products.columns.type", "sortable": True},
                {"key": "unit", "label": "products.columns.unit", "sortable": False},
                {"key": "cost", "label": "products.columns.cost", "sortable": True},
                {"key": "status", "label": "products.columns.status", "sortable": True},
            ],
            on_row_click=self._on_row_click,
            on_edit=self._on_edit_product,
            on_delete=self._on_delete_product,
            page_size=self._page_size,
            on_page_change=self._on_page_change,
        )

        content = ft.Column(
            controls=[header, self._search_bar, self._filter_panel, self._data_table],
            spacing=LayoutConstants.SPACING_MD,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        if self._is_loading:
            return ft.Container(
                content=LoadingSpinner(message="Cargando productos..."),
                expand=True,
                alignment=ft.alignment.center,
            )
        elif self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_products,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )
        elif not self._products:
            return ft.Container(
                content=EmptyState(
                    icon=ft.Icons.INVENTORY_2_OUTLINED,
                    message="No hay productos registrados",
                    action_label="Crear Primer Producto",
                    on_action=self._on_create_product,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )
        else:
            return content

    def did_mount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.info("ProductListView mounted")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        if self.page:
            self.page.run_task(self.load_products)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_products(self) -> None:
        """Carga los productos desde la API."""
        logger.info(f"Loading products: page={self._current_page}")
        self._is_loading = True
        self._error_message = ""

        if self.page:
            self.update()

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            params: dict[str, Any] = {
                "page": self._current_page,
                "page_size": self._page_size,
            }

            if self._search_query:
                response = await product_api.search(query=self._search_query, **params)
            else:
                filters = self._get_active_filters()
                response = await product_api.get_all(**params, **filters)

            self._products = response.get("items", [])
            self._total_products = response.get("total", 0)

            if self._data_table:
                self._data_table.set_data(
                    self._format_products_for_table(self._products),
                    total=self._total_products,
                    current_page=self._current_page,
                )

            logger.success(f"Loaded {len(self._products)} products")
            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading products: {e}")
            self._error_message = f"Error al cargar productos: {str(e)}"
            self._is_loading = False

        if self.page:
            self.update()

    def _format_products_for_table(self, products: list[dict]) -> list[dict]:
        """Formatea los datos de productos para la tabla."""
        formatted = []
        for product in products:
            # Indicador de BOM
            has_bom_icon = (
                "📋 " if product.get("product_type") == "NOMENCLATURE" else ""
            )

            formatted.append({
                "id": product.get("id"),
                "code": product.get("code", ""),
                "name": has_bom_icon + product.get("name", ""),
                "type": self._format_product_type(product.get("product_type", "")),
                "unit": product.get("unit", "-"),
                "cost": f"${product.get('cost', 0):.2f}",
                "status": "Activo" if product.get("is_active") else "Inactivo",
                "_original": product,
            })
        return formatted

    def _format_product_type(self, type_code: str) -> str:
        """Formatea el tipo de producto."""
        return "Nomenclatura" if type_code == "NOMENCLATURE" else "Artículo"

    def _get_active_filters(self) -> dict[str, Any]:
        """Obtiene los filtros activos."""
        filters: dict[str, Any] = {}
        if self._status_filter != "all":
            filters["is_active"] = self._status_filter == "active"
        if self._type_filter != "all":
            filters["product_type"] = self._type_filter
        return filters

    def _on_search(self, query: str) -> None:
        """Callback cuando se realiza una búsqueda."""
        self._search_query = query
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_products)

    def _on_clear_search(self) -> None:
        """Callback cuando se limpia la búsqueda."""
        self._search_query = ""
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_products)

    def _on_filter_change(self, filters: dict[str, Any]) -> None:
        """Callback cuando cambian los filtros."""
        self._status_filter = filters.get("status", "all")
        self._type_filter = filters.get("type", "all")
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_products)

    def _on_page_change(self, page: int) -> None:
        """Callback cuando cambia la página."""
        self._current_page = page
        if self.page:
            self.page.run_task(self.load_products)

    def _on_row_click(self, row_data: dict) -> None:
        """Callback cuando se hace click en una fila."""
        product_id = row_data.get("id")
        logger.info(f"Product row clicked: ID={product_id}")
        # TODO: Navegar a detalle

    def _on_create_product(self, e: ft.ControlEvent | None = None) -> None:
        """Callback para crear nuevo producto."""
        logger.info("Create product button clicked")
        # TODO: Navegar a formulario

    def _on_edit_product(self, row_data: dict) -> None:
        """Callback para editar un producto."""
        product_id = row_data.get("id")
        logger.info(f"Edit product clicked: ID={product_id}")
        # TODO: Navegar a formulario de edición

    def _on_delete_product(self, row_data: dict) -> None:
        """Callback para eliminar un producto."""
        product_id = row_data.get("id")
        logger.info(f"Delete product clicked: ID={product_id}")
        # TODO: Mostrar diálogo de confirmación

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        if self.page:
            self.update()

    def refresh(self) -> None:
        """Refresca el listado de productos."""
        if self.page:
            self.page.run_task(self.load_products)
