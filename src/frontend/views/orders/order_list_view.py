"""
Vista de listado de órdenes.

Muestra todas las órdenes del sistema con filtros, búsqueda y paginación.
"""
from typing import Any, Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t
from src.frontend.components.common import (
    SearchBar,
    FilterPanel,
    DataTable,
    LoadingSpinner,
    ErrorDisplay,
    EmptyState,
    ConfirmDialog,
)


class OrderListView(ft.Container):
    """
    Vista de listado de órdenes con filtros y paginación.

    Muestra tabla de órdenes con:
    - Búsqueda por número de orden
    - Filtros por estado
    - Paginación
    - Acciones de ver detalle/editar/eliminar
    """

    def __init__(
        self,
        on_view_detail: Callable[[int, int, str], None] | None = None,
        on_create: Callable[[], None] | None = None,
        on_edit: Callable[[int, int, str], None] | None = None,
    ):
        """
        Inicializa la vista de listado de órdenes.

        Args:
            on_view_detail: Callback para ver detalle (order_id, company_id, company_type)
            on_create: Callback para crear nueva orden
            on_edit: Callback para editar orden (order_id, company_id, company_type)
        """
        super().__init__()

        # Callbacks de navegación
        self._on_view_detail_callback = on_view_detail
        self._on_create_callback = on_create
        self._on_edit_callback = on_edit

        # Estado
        self._is_loading: bool = True
        self._error_message: str = ""
        self._orders: list[dict] = []
        self._total_orders: int = 0
        self._current_page: int = 1
        self._page_size: int = 20

        # Filtros
        self._search_query: str = ""
        self._status_filter: str = "all"

        # Componentes
        self._search_bar: SearchBar | None = None
        self._filter_panel: FilterPanel | None = None
        self._data_table: DataTable | None = None
        self._confirm_dialog: ConfirmDialog | None = None

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = 0

        # Construir contenido inicial
        self.content = self.build()

        logger.info("OrderListView initialized")

    def build(self) -> ft.Control:
        """
        Construye el componente de listado de órdenes.

        Returns:
            Control de Flet con la vista completa
        """
        # Estados de carga/error/vacío
        if self._is_loading:
            return ft.Container(
                content=LoadingSpinner(message=t("common.loading")),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )

        if self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_orders,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )

        if not self._orders and not self._search_query and self._status_filter == "all":
            return ft.Container(
                content=EmptyState(
                    icon=ft.Icons.SHOPPING_CART_OUTLINED,
                    title=t("orders.title"),
                    message=t("orders.no_orders"),
                    action_text=t("orders.create_first"),
                    on_action=self._on_create_order,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )

        # Contenido principal con datos
        # SearchBar
        self._search_bar = SearchBar(
            placeholder=t("orders.search_placeholder"),
            on_search=self._on_search,
        )

        # FilterPanel con filtros
        filters_config = [
            {
                "key": "status",
                "label": "orders.fields.status",
                "type": "dropdown",
                "options": [
                    {"label": "common.all", "value": "all"},
                    {"label": "orders.status.draft", "value": "1"},
                    {"label": "orders.status.confirmed", "value": "2"},
                    {"label": "orders.status.in_progress", "value": "3"},
                    {"label": "orders.status.completed", "value": "4"},
                    {"label": "orders.status.cancelled", "value": "5"},
                ],
                "default": "all",
            },
        ]

        self._filter_panel = FilterPanel(
            filters=filters_config,
            on_filter_change=self._on_filter_change,
        )

        # DataTable con columnas de órdenes
        self._data_table = DataTable(
            columns=[
                {"key": "order_number", "label": "orders.columns.order_number", "sortable": True},
                {"key": "company_name", "label": "orders.columns.company", "sortable": True},
                {"key": "order_date", "label": "orders.columns.order_date", "sortable": True},
                {"key": "total", "label": "orders.columns.total_amount", "sortable": True, "numeric": True},
                {"key": "status", "label": "orders.columns.status", "sortable": True},
            ],
            on_row_click=self._on_row_click,
            on_edit=self._on_edit_order,
            on_delete=self._on_delete_order,
            page_size=self._page_size,
            on_page_change=self._on_page_change,
        )

        # Asignar datos al DataTable
        formatted_data = self._format_orders_for_table(self._orders)
        self._data_table.set_data(
            formatted_data,
            total=self._total_orders,
            current_page=self._current_page,
        )

        # Header con título y botón crear (opcional desde aquí)
        header = ft.Row(
            controls=[
                ft.Text(
                    t("orders.title"),
                    size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                    expand=True,
                ),
                # Generalmente las órdenes se crean desde una empresa o una cotización,
                # pero podemos permitirlo si el callback está asignado
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    on_click=self._on_create_order,
                    visible=self._on_create_callback is not None,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Contenido principal
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=header,
                        padding=ft.padding.only(
                            left=LayoutConstants.PADDING_LG,
                            right=LayoutConstants.PADDING_LG,
                            top=LayoutConstants.PADDING_LG,
                        ),
                    ),
                    ft.Container(
                        content=self._search_bar,
                        padding=ft.padding.symmetric(horizontal=LayoutConstants.PADDING_LG),
                    ),
                    ft.Container(
                        content=self._filter_panel,
                        padding=ft.padding.symmetric(horizontal=LayoutConstants.PADDING_LG),
                    ),
                    ft.Container(
                        content=self._data_table,
                        padding=ft.padding.only(
                            left=LayoutConstants.PADDING_LG,
                            right=LayoutConstants.PADDING_LG,
                            bottom=LayoutConstants.PADDING_LG,
                        ),
                        expand=True,
                    ),
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
            expand=True,
            padding=0,
        )

    def did_mount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.info("OrderListView mounted, loading data")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        if self.page:
            self.page.run_task(self.load_orders)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_orders(self) -> None:
        """Carga las órdenes desde la API."""
        logger.info(f"Loading orders: page={self._current_page}, search='{self._search_query}'")
        self._is_loading = True
        self._error_message = ""
        
        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import order_api
            
            params = {
                "page": self._current_page,
                "page_size": self._page_size,
            }

            if self._search_query:
                response = await order_api.search(query=self._search_query, **params)
            else:
                filters = {}
                if self._status_filter != "all":
                    filters["status_id"] = int(self._status_filter)
                response = await order_api.get_all(**params, **filters)

            self._orders = response.get("items", [])
            self._total_orders = response.get("total", 0)
            self._is_loading = False

            logger.success(f"Loaded {len(self._orders)} orders")

        except Exception as e:
            logger.exception(f"Error loading orders: {e}")
            self._error_message = t("orders.messages.error_loading", {"error": str(e)})
            self._is_loading = False

        self.content = self.build()
        if self.page:
            self.update()

    def _format_orders_for_table(self, orders: list[dict]) -> list[dict]:
        """Formatea los datos para la tabla."""
        formatted = []
        for o in orders:
            status_id = o.get("status_id")
            status_text = t(f"orders.status.{self._get_status_key(status_id)}")
            
            formatted.append({
                "id": o.get("id"),
                "order_number": o.get("order_number", "-"),
                "company_name": o.get("company_name", "-"),
                "order_date": o.get("order_date", "-"),
                "total": f"${float(o.get('total', 0)):,.2f}",
                "status": status_text,
                "_original": o,
            })
        return formatted

    def _get_status_key(self, status_id: int) -> str:
        """Mapea ID de estado a clave i18n."""
        mapping = {
            1: "draft",
            2: "confirmed",
            3: "in_progress",
            4: "completed",
            5: "cancelled"
        }
        return mapping.get(status_id, "draft")

    def _on_search(self, query: str) -> None:
        """Callback de búsqueda."""
        self._search_query = query
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_orders)

    def _on_filter_change(self, filters: dict[str, Any]) -> None:
        """Callback de cambio de filtros."""
        self._status_filter = filters.get("status", "all")
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_orders)

    def _on_page_change(self, page: int) -> None:
        """Callback de cambio de página."""
        self._current_page = page
        if self.page:
            self.page.run_task(self.load_orders)

    def _on_row_click(self, row_data: dict) -> None:
        """Callback de click en fila."""
        order = row_data.get("_original")
        if self._on_view_detail_callback and order:
            self._on_view_detail_callback(
                order.get("id"), 
                order.get("company_id"),
                order.get("company_type", "CLIENT")
            )

    def _on_create_order(self, e=None) -> None:
        """Callback crear."""
        if self._on_create_callback:
            self._on_create_callback()

    def _on_edit_order(self, row_data: dict) -> None:
        """Callback editar."""
        order = row_data.get("_original")
        if self._on_edit_callback and order:
            self._on_edit_callback(
                order.get("id"),
                order.get("company_id"),
                order.get("company_type", "CLIENT")
            )

    def _on_delete_order(self, row_data: dict) -> None:
        """Callback eliminar."""
        order_id = row_data.get("id")
        number = row_data.get("order_number")
        
        self._confirm_dialog = ConfirmDialog(
            title=t("common.confirm_delete"),
            message=t("orders.messages.delete_confirm", {"number": number}),
            on_confirm=lambda: self._confirm_delete(order_id),
        )

        if self.page:
            self.page.dialog = self._confirm_dialog
            self._confirm_dialog.open = True
            self.page.update()

    async def _confirm_delete(self, order_id: int) -> None:
        """Ejecuta la eliminación."""
        try:
            from src.frontend.services.api import order_api
            await order_api.delete(order_id)
            logger.success(f"Order {order_id} deleted")
            await self.load_orders()
        except Exception as e:
            logger.error(f"Error deleting order: {e}")

    def _on_state_changed(self) -> None:
        """Actualiza la interfaz al cambiar tema/idioma."""
        self.content = self.build()
        if self.page:
            self.update()
