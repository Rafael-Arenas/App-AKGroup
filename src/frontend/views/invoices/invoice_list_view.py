"""
Vista de listado de facturas por orden.

Muestra las facturas (SII y Export) de una orden específica con filtros y búsqueda.
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


class InvoiceListView(ft.Container):
    """
    Vista de listado de facturas por orden.

    Muestra tabla de facturas con:
    - Búsqueda por número de factura
    - Filtros por tipo de factura
    - Información de la orden asociada
    - Acciones de ver detalle/editar/eliminar
    """

    def __init__(
        self,
        order_id: int,
        order_number: str,
        on_view_detail: Callable[[int, str], None] | None = None,
        on_create: Callable[[int], None] | None = None,
        on_back: Callable[[], None] | None = None,
    ):
        """
        Inicializa la vista de listado de facturas.

        Args:
            order_id: ID de la orden
            order_number: Número de la orden (para mostrar)
            on_view_detail: Callback para ver detalle (invoice_id, invoice_type_class)
            on_create: Callback para crear nueva factura (order_id)
            on_back: Callback para volver a la lista de órdenes
        """
        super().__init__()

        # Datos de la orden
        self._order_id = order_id
        self._order_number = order_number

        # Callbacks de navegación
        self._on_view_detail_callback = on_view_detail
        self._on_create_callback = on_create
        self._on_back_callback = on_back

        # Estado
        self._is_loading: bool = True
        self._error_message: str = ""
        self._invoices: list[dict] = []
        self._total_invoices: int = 0
        self._current_page: int = 1
        self._page_size: int = 20

        # Filtros
        self._search_query: str = ""
        self._type_filter: str = "all"  # all, SII, EXPORT

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

        logger.info(f"InvoiceListView initialized for order_id={order_id}")

    def build(self) -> ft.Control:
        """
        Construye el componente de listado de facturas.

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
                    on_retry=self.load_invoices,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )

        if not self._invoices and not self._search_query and self._type_filter == "all":
            return ft.Container(
                content=EmptyState(
                    icon=ft.Icons.RECEIPT_LONG_OUTLINED,
                    title=t("invoices.title"),
                    message=t("invoices.no_invoices"),
                    action_text=t("invoices.create_first"),
                    on_action=self._on_create_invoice,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )

        # Contenido principal con datos
        # SearchBar
        self._search_bar = SearchBar(
            placeholder=t("invoices.search_placeholder"),
            on_search=self._on_search,
        )

        # FilterPanel con filtros
        filters_config = [
            {
                "key": "type",
                "label": "invoices.fields.type",
                "type": "dropdown",
                "options": [
                    {"label": "common.all", "value": "all"},
                    {"label": "invoices.type.sii", "value": "SII"},
                    {"label": "invoices.type.export", "value": "EXPORT"},
                ],
                "default": "all",
            },
        ]

        self._filter_panel = FilterPanel(
            filters=filters_config,
            on_filter_change=self._on_filter_change,
        )

        # DataTable con columnas de facturas
        self._data_table = DataTable(
            columns=[
                {"key": "revision", "label": "invoices.columns.revision", "sortable": True},
                {"key": "invoice_number", "label": "invoices.columns.invoice_number", "sortable": True},
                {"key": "invoice_type", "label": "invoices.columns.invoice_type", "sortable": True},
                {"key": "invoice_type_class", "label": "invoices.columns.class", "sortable": True},
                {"key": "order_number", "label": "invoices.columns.order", "sortable": False},
                {"key": "total", "label": "invoices.columns.total", "sortable": True, "numeric": True},
            ],
            on_row_click=self._on_row_click,
            on_edit=self._on_edit_invoice,
            on_delete=self._on_delete_invoice,
            page_size=self._page_size,
            on_page_change=self._on_page_change,
        )

        # Asignar datos al DataTable
        formatted_data = self._format_invoices_for_table(self._invoices)
        self._data_table.set_data(
            formatted_data,
            total=self._total_invoices,
            current_page=self._current_page,
        )

        # Header con título y botones
        header = ft.Row(
            controls=[
                # Botón volver
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    on_click=self._on_back_click,
                    tooltip=t("common.back"),
                    visible=self._on_back_callback is not None,
                ),
                ft.Text(
                    f"{t('invoices.title')} - {t('orders.order')} {self._order_number}",
                    size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                    expand=True,
                ),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    on_click=self._on_create_invoice,
                    visible=self._on_create_callback is not None,
                    tooltip=t("invoices.create"),
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
        logger.info("InvoiceListView mounted, loading data")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        if self.page:
            self.page.run_task(self.load_invoices)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_invoices(self) -> None:
        """Carga las facturas desde la API."""
        logger.info(f"Loading invoices for order {self._order_id}: page={self._current_page}")
        self._is_loading = True
        self._error_message = ""
        
        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import invoice_api
            
            params = {
                "page": self._current_page,
                "page_size": self._page_size,
            }

            # Get all invoices for this order
            response = await invoice_api.get_all_by_order(self._order_id, **params)
            
            all_invoices = response.get("items", [])
            
            # Apply filters
            if self._search_query:
                all_invoices = [
                    inv for inv in all_invoices 
                    if self._search_query.lower() in inv.get("invoice_number", "").lower()
                ]
            
            if self._type_filter != "all":
                all_invoices = [
                    inv for inv in all_invoices 
                    if inv.get("invoice_type_class") == self._type_filter
                ]

            self._invoices = all_invoices
            self._total_invoices = len(all_invoices)
            self._is_loading = False

            logger.success(f"Loaded {len(self._invoices)} invoices")

        except Exception as e:
            logger.exception(f"Error loading invoices: {e}")
            self._error_message = t("invoices.messages.error_loading", {"error": str(e)})
            self._is_loading = False

        self.content = self.build()
        if self.page:
            self.update()

    def _format_invoices_for_table(self, invoices: list[dict]) -> list[dict]:
        """Formatea los datos para la tabla."""
        formatted = []
        for inv in invoices:
            invoice_type_class = inv.get("invoice_type_class", "SII")
            invoice_type = inv.get("invoice_type", "-")
            
            # Map invoice type codes to readable names
            type_mapping = {
                "33": "Factura Electrónica",
                "34": "Factura Exenta",
                "56": "Nota de Débito",
                "61": "Nota de Crédito",
                "110": "Factura Export",
                "111": "Nota de Débito Export",
                "112": "Nota de Crédito Export",
            }
            type_text = type_mapping.get(invoice_type, invoice_type)
            
            formatted.append({
                "id": inv.get("id"),
                "revision": inv.get("revision", "A"),
                "invoice_number": inv.get("invoice_number", "-"),
                "invoice_type": type_text,
                "invoice_type_class": invoice_type_class,
                "order_number": self._order_number,
                "total": f"${float(inv.get('total', 0)):,.2f}",
                "_original": inv,
            })
        return formatted

    def _on_search(self, query: str) -> None:
        """Callback de búsqueda."""
        self._search_query = query
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_invoices)

    def _on_filter_change(self, filters: dict[str, Any]) -> None:
        """Callback de cambio de filtros."""
        self._type_filter = filters.get("type", "all")
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_invoices)

    def _on_page_change(self, page: int) -> None:
        """Callback de cambio de página."""
        self._current_page = page
        if self.page:
            self.page.run_task(self.load_invoices)

    def _on_row_click(self, row_data: dict) -> None:
        """Callback de click en fila."""
        invoice = row_data.get("_original")
        if self._on_view_detail_callback and invoice:
            self._on_view_detail_callback(
                invoice.get("id"), 
                invoice.get("invoice_type_class", "SII")
            )

    def _on_create_invoice(self, e=None) -> None:
        """Callback crear."""
        if self._on_create_callback:
            self._on_create_callback(self._order_id)

    def _on_edit_invoice(self, row_data: dict) -> None:
        """Callback editar."""
        # TODO: Implement edit functionality
        logger.info(f"Edit invoice: {row_data}")

    def _on_delete_invoice(self, row_data: dict) -> None:
        """Callback eliminar."""
        invoice_id = row_data.get("id")
        number = row_data.get("invoice_number")
        invoice_type_class = row_data.get("invoice_type_class", "SII")
        
        self._confirm_dialog = ConfirmDialog(
            title=t("common.confirm_delete"),
            message=t("invoices.messages.delete_confirm", {"number": number}),
            on_confirm=lambda: self._confirm_delete(invoice_id, invoice_type_class),
        )

        if self.page:
            self.page.dialog = self._confirm_dialog
            self._confirm_dialog.open = True
            self.page.update()

    async def _confirm_delete(self, invoice_id: int, invoice_type_class: str) -> None:
        """Ejecuta la eliminación."""
        try:
            from src.frontend.services.api import invoice_api
            if invoice_type_class == "SII":
                await invoice_api.delete_sii(invoice_id, user_id=1)  # TODO: Get real user_id
            else:
                await invoice_api.delete_export(invoice_id, user_id=1)
            logger.success(f"Invoice {invoice_id} deleted")
            await self.load_invoices()
        except Exception as e:
            logger.error(f"Error deleting invoice: {e}")

    def _on_back_click(self, e: ft.ControlEvent = None) -> None:
        """Callback para volver."""
        if self._on_back_callback:
            self._on_back_callback()

    def _on_state_changed(self) -> None:
        """Actualiza la interfaz al cambiar tema/idioma."""
        self.content = self.build()
        if self.page:
            self.update()
