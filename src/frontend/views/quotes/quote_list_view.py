"""
Vista de listado de cotizaciones.

Muestra todas las cotizaciones del sistema con filtros, búsqueda y paginación.
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


class QuoteListView(ft.Container):
    """
    Vista de listado de cotizaciones con filtros y paginación.

    Muestra tabla de cotizaciones con:
    - Búsqueda por asunto
    - Filtros por estado y personal
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
        Inicializa la vista de listado de cotizaciones.

        Args:
            on_view_detail: Callback para ver detalle (quote_id, company_id, company_type)
            on_create: Callback para crear nueva cotización
            on_edit: Callback para editar cotización (quote_id, company_id, company_type)
        """
        super().__init__()

        # Callbacks de navegación
        self._on_view_detail_callback = on_view_detail
        self._on_create_callback = on_create
        self._on_edit_callback = on_edit

        # Estado
        self._is_loading: bool = True
        self._error_message: str = ""
        self._quotes: list[dict] = []
        self._total_quotes: int = 0
        self._current_page: int = 1
        self._page_size: int = 20

        # Filtros
        self._search_query: str = ""
        self._status_filter: str = "all"
        self._staff_filter: str = "all"

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

        logger.info("QuoteListView initialized")

    def build(self) -> ft.Control:
        """
        Construye el componente de listado de cotizaciones.

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
                    on_retry=self.load_quotes,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )

        if not self._quotes and not self._search_query and self._status_filter == "all":
            return ft.Container(
                content=EmptyState(
                    icon=ft.Icons.DESCRIPTION_OUTLINED,
                    title=t("quotes.title"),
                    message=t("quotes.no_quotes"),
                    action_text=t("quotes.create_first"),
                    on_action=self._on_create_quote,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )

        # Contenido principal con datos
        # SearchBar
        self._search_bar = SearchBar(
            placeholder=t("quotes.search_placeholder"),
            on_search=self._on_search,
        )

        # FilterPanel con filtros
        filters_config = [
            {
                "key": "status",
                "label": "quotes.fields.status",
                "type": "dropdown",
                "options": [
                    {"label": "common.all", "value": "all"},
                    {"label": "quotes.status.draft", "value": "1"},
                    {"label": "quotes.status.sent", "value": "2"},
                    {"label": "quotes.status.accepted", "value": "3"},
                    {"label": "quotes.status.rejected", "value": "4"},
                ],
                "default": "all",
            },
        ]

        self._filter_panel = FilterPanel(
            filters=filters_config,
            on_filter_change=self._on_filter_change,
        )

        # DataTable con columnas de cotizaciones
        self._data_table = DataTable(
            columns=[
                {"key": "quote_number", "label": "quotes.columns.quote_number", "sortable": True},
                {"key": "subject", "label": "quotes.columns.subject", "sortable": True},
                {"key": "company_name", "label": "quotes.columns.company", "sortable": True},
                {"key": "quote_date", "label": "quotes.columns.quote_date", "sortable": True},
                {"key": "total", "label": "quotes.columns.total_amount", "sortable": True, "numeric": True},
                {"key": "status", "label": "quotes.columns.status", "sortable": True},
            ],
            on_row_click=self._on_row_click,
            on_edit=self._on_edit_quote,
            on_delete=self._on_delete_quote,
            page_size=self._page_size,
            on_page_change=self._on_page_change,
        )

        # Asignar datos al DataTable
        formatted_data = self._format_quotes_for_table(self._quotes)
        self._data_table.set_data(
            formatted_data,
            total=self._total_quotes,
            current_page=self._current_page,
        )

        # Header con título y botón crear (opcional desde aquí)
        header = ft.Row(
            controls=[
                ft.Text(
                    t("quotes.title"),
                    size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                    expand=True,
                ),
                # Generalmente las cotizaciones se crean desde una empresa, 
                # pero podemos permitirlo si el callback está asignado
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    on_click=self._on_create_quote,
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
        logger.info("QuoteListView mounted, loading data")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        if self.page:
            self.page.run_task(self.load_quotes)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_quotes(self) -> None:
        """Carga las cotizaciones desde la API."""
        logger.info(f"Loading quotes: page={self._current_page}, search='{self._search_query}'")
        self._is_loading = True
        self._error_message = ""
        
        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import quote_api
            
            params = {
                "page": self._current_page,
                "page_size": self._page_size,
            }

            if self._search_query:
                response = await quote_api.search(query=self._search_query, **params)
            else:
                filters = {}
                if self._status_filter != "all":
                    filters["status_id"] = int(self._status_filter)
                response = await quote_api.get_all(**params, **filters)

            self._quotes = response.get("items", [])
            self._total_quotes = response.get("total", 0)
            self._is_loading = False

            logger.success(f"Loaded {len(self._quotes)} quotes")

        except Exception as e:
            logger.exception(f"Error loading quotes: {e}")
            self._error_message = t("quotes.messages.error_loading", {"error": str(e)})
            self._is_loading = False

        self.content = self.build()
        if self.page:
            self.update()

    def _format_quotes_for_table(self, quotes: list[dict]) -> list[dict]:
        """Formatea los datos para la tabla."""
        formatted = []
        for q in quotes:
            status_id = q.get("status_id")
            status_text = t(f"quotes.status.{self._get_status_key(status_id)}")
            
            formatted.append({
                "id": q.get("id"),
                "quote_number": q.get("quote_number", "-"),
                "subject": q.get("subject", "-"),
                "company_name": q.get("company_name", "-"),
                "quote_date": q.get("quote_date", "-"),
                "total": f"${float(q.get('total', 0)):,.2f}",
                "status": status_text,
                "_original": q,
            })
        return formatted

    def _get_status_key(self, status_id: int) -> str:
        """Mapea ID de estado a clave i18n."""
        mapping = {1: "draft", 2: "sent", 3: "accepted", 4: "rejected"}
        return mapping.get(status_id, "draft")

    def _on_search(self, query: str) -> None:
        """Callback de búsqueda."""
        self._search_query = query
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_quotes)

    def _on_filter_change(self, filters: dict[str, Any]) -> None:
        """Callback de cambio de filtros."""
        self._status_filter = filters.get("status", "all")
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_quotes)

    def _on_page_change(self, page: int) -> None:
        """Callback de cambio de página."""
        self._current_page = page
        if self.page:
            self.page.run_task(self.load_quotes)

    def _on_row_click(self, row_data: dict) -> None:
        """Callback de click en fila."""
        quote = row_data.get("_original")
        if self._on_view_detail_callback and quote:
            self._on_view_detail_callback(
                quote.get("id"), 
                quote.get("company_id"),
                "CLIENT" # Defaulting to client for now
            )

    def _on_create_quote(self, e=None) -> None:
        """Callback crear."""
        if self._on_create_callback:
            self._on_create_callback()

    def _on_edit_quote(self, row_data: dict) -> None:
        """Callback editar."""
        quote = row_data.get("_original")
        if self._on_edit_callback and quote:
            self._on_edit_callback(
                quote.get("id"),
                quote.get("company_id"),
                "CLIENT"
            )

    def _on_delete_quote(self, row_data: dict) -> None:
        """Callback eliminar."""
        quote_id = row_data.get("id")
        number = row_data.get("quote_number")
        
        self._confirm_dialog = ConfirmDialog(
            title=t("common.confirm_delete"),
            message=t("quotes.messages.delete_confirm", {"number": number}),
            on_confirm=lambda: self._confirm_delete(quote_id),
        )

        if self.page:
            self.page.dialog = self._confirm_dialog
            self._confirm_dialog.open = True
            self.page.update()

    async def _confirm_delete(self, quote_id: int) -> None:
        """Ejecuta la eliminación."""
        try:
            from src.frontend.services.api import quote_api
            await quote_api.delete(quote_id)
            logger.success(f"Quote {quote_id} deleted")
            await self.load_quotes()
        except Exception as e:
            logger.error(f"Error deleting quote: {e}")

    def _on_state_changed(self) -> None:
        """Actualiza la interfaz al cambiar tema/idioma."""
        self.content = self.build()
        if self.page:
            self.update()
