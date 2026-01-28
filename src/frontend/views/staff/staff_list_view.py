"""
Vista de listado de personal (Staff).

Muestra una tabla de usuarios del sistema con filtros, búsqueda y paginación.
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


class StaffListView(ft.Container):
    """
    Vista de listado de personal con filtros y paginación.

    Muestra tabla de usuarios del sistema con:
    - Búsqueda por nombre/username/email
    - Filtros por estado y rol
    - Paginación
    - Acciones de editar/eliminar
    - Botón para crear nuevo personal

    Example:
        >>> staff_list = StaffListView()
        >>> page.add(staff_list)
    """

    def __init__(
        self,
        on_view_detail: Callable[[int], None] | None = None,
        on_create: Callable[[], None] | None = None,
        on_edit: Callable[[int], None] | None = None,
    ):
        """
        Inicializa la vista de listado de personal.

        Args:
            on_view_detail: Callback para ver detalle (staff_id)
            on_create: Callback para crear nuevo personal
            on_edit: Callback para editar personal (staff_id)
        """
        super().__init__()

        # Callbacks de navegación
        self._on_view_detail_callback = on_view_detail
        self._on_create_callback = on_create
        self._on_edit_callback = on_edit

        # Estado
        self._is_loading: bool = True
        self._error_message: str = ""
        self._staff_list: list[dict] = []
        self._total_staff: int = 0
        self._current_page: int = 1
        self._page_size: int = 20

        # Filtros
        self._search_query: str = ""
        self._status_filter: str = "all"
        self._role_filter: str = "all"

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

        logger.info("StaffListView initialized")

    def build(self) -> ft.Control:
        """
        Construye el componente de listado de personal.

        Returns:
            Control de Flet con la vista completa
        """
        # Estados de carga/error/vacío
        if self._is_loading:
            loading_message = t("staff.messages.loading")
            return ft.Container(
                content=LoadingSpinner(message=loading_message),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )

        if self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_staff,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )

        if not self._staff_list:
            return ft.Container(
                content=EmptyState(
                    icon=ft.Icons.BADGE_OUTLINED,
                    title=t("staff.title"),
                    message=t("staff.no_staff"),
                    action_text=t("staff.create_first"),
                    on_action=self._on_create_staff,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )

        # Contenido principal con datos
        # SearchBar
        self._search_bar = SearchBar(
            placeholder=t("staff.search_placeholder"),
            on_search=self._on_search,
        )

        # FilterPanel con filtros
        filters_config = [
            {
                "key": "status",
                "label": "staff.filters.status",
                "type": "dropdown",
                "options": [
                    {"label": "staff.filters.all", "value": "all"},
                    {"label": "staff.filters.active", "value": "active"},
                    {"label": "staff.filters.inactive", "value": "inactive"},
                ],
                "default": "all",
            },
            {
                "key": "role",
                "label": "staff.filters.role",
                "type": "dropdown",
                "options": [
                    {"label": "staff.filters.all", "value": "all"},
                    {"label": "staff.filters.admin", "value": "admin"},
                    {"label": "staff.filters.user", "value": "user"},
                ],
                "default": "all",
            },
        ]

        self._filter_panel = FilterPanel(
            filters=filters_config,
            on_filter_change=self._on_filter_change,
        )

        # DataTable con columnas de personal
        self._data_table = DataTable(
            columns=[
                {"key": "full_name", "label": "staff.columns.full_name", "sortable": True},
                {"key": "username", "label": "staff.columns.username", "sortable": True},
                {"key": "email", "label": "staff.columns.email", "sortable": True},
                {"key": "trigram", "label": "staff.columns.trigram", "sortable": True},
                {"key": "position", "label": "staff.columns.position", "sortable": False},
                {"key": "role", "label": "staff.columns.role", "sortable": True},
                {"key": "status", "label": "staff.columns.status", "sortable": True},
            ],
            on_row_click=self._on_row_click,
            on_edit=self._on_edit_staff,
            on_delete=self._on_delete_staff,
            page_size=self._page_size,
            on_page_change=self._on_page_change,
        )

        # Asignar datos al DataTable si hay personal cargado
        if self._staff_list:
            formatted_data = self._format_staff_for_table(self._staff_list)
            self._data_table.set_data(
                formatted_data,
                total=self._total_staff,
                current_page=self._current_page,
            )

        # Header con título y botón crear
        header = ft.Row(
            controls=[
                ft.Text(
                    t("staff.list_title"),
                    size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                    expand=True,
                ),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    on_click=self._on_create_staff,
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
        """
        Lifecycle: Se ejecuta cuando el componente se monta.

        Carga el personal.
        """
        logger.info("StaffListView mounted, loading data")

        # Suscribirse a cambios de estado
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)

        # Cargar datos
        if self.page:
            self.page.run_task(self.load_staff)

    def will_unmount(self) -> None:
        """
        Lifecycle: Se ejecuta cuando el componente se desmonta.

        Limpia los observers.
        """
        logger.info("StaffListView unmounting")
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_staff(self) -> None:
        """
        Carga el personal desde la API.

        Aplica los filtros y búsqueda actuales.
        """
        logger.info(
            f"Loading staff: page={self._current_page}, "
            f"search='{self._search_query}', filters={self._get_active_filters()}"
        )

        self._is_loading = True
        self._error_message = ""

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import StaffAPI

            staff_api = StaffAPI()

            # Por ahora usamos get_all ya que la API no tiene paginación ni búsqueda avanzada
            # TODO: Implementar paginación y búsqueda en el backend si es necesario
            filters = self._get_active_filters()
            
            if filters.get("is_active") is True:
                staff_result = await staff_api.get_active()
            elif filters.get("is_admin") is True:
                staff_result = await staff_api.get_admins()
            else:
                staff_result = await staff_api.get_all()

            # Filtrar localmente si hay búsqueda
            if self._search_query:
                query = self._search_query.lower()
                staff_result = [
                    s for s in staff_result
                    if query in s.get("username", "").lower()
                    or query in s.get("email", "").lower()
                    or query in s.get("first_name", "").lower()
                    or query in s.get("last_name", "").lower()
                    or query in (s.get("trigram") or "").lower()
                ]

            # Aplicar filtros locales
            if self._status_filter == "active":
                staff_result = [s for s in staff_result if s.get("is_active")]
            elif self._status_filter == "inactive":
                staff_result = [s for s in staff_result if not s.get("is_active")]
            
            if self._role_filter == "admin":
                staff_result = [s for s in staff_result if s.get("is_admin")]
            elif self._role_filter == "user":
                staff_result = [s for s in staff_result if not s.get("is_admin")]

            # Actualizar datos
            self._staff_list = staff_result
            self._total_staff = len(staff_result)

            logger.success(f"Loaded {len(self._staff_list)} staff members")

            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading staff: {e}")
            self._error_message = f"Error al cargar personal: {str(e)}"
            self._is_loading = False

        # Reconstruir contenido con los datos cargados o error
        self.content = self.build()
        if self.page:
            self.update()

    def _format_staff_for_table(self, staff_list: list[dict]) -> list[dict]:
        """
        Formatea los datos de personal para la tabla.

        Args:
            staff_list: Lista de personal desde la API

        Returns:
            Lista formateada para DataTable
        """
        formatted = []
        for staff in staff_list:
            formatted.append({
                "id": staff.get("id"),
                "full_name": f"{staff.get('first_name', '')} {staff.get('last_name', '')}".strip(),
                "username": staff.get("username", ""),
                "email": staff.get("email", ""),
                "trigram": staff.get("trigram") or "-",
                "position": staff.get("position") or "-",
                "role": t("staff.role.admin") if staff.get("is_admin") else t("staff.role.user"),
                "status": t("common.active") if staff.get("is_active") else t("common.inactive"),
                "_original": staff,
            })
        return formatted

    def _get_active_filters(self) -> dict[str, Any]:
        """
        Obtiene los filtros activos (que no sean "all").

        Returns:
            Diccionario con filtros activos
        """
        filters: dict[str, Any] = {}

        if self._status_filter == "active":
            filters["is_active"] = True
        elif self._status_filter == "inactive":
            filters["is_active"] = False

        if self._role_filter == "admin":
            filters["is_admin"] = True
        elif self._role_filter == "user":
            filters["is_admin"] = False

        return filters

    def _on_search(self, query: str) -> None:
        """
        Callback cuando se realiza una búsqueda.

        Args:
            query: Texto de búsqueda
        """
        logger.info(f"Search triggered: '{query}'")
        self._search_query = query
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_staff)

    def _on_filter_change(self, filters: dict[str, Any]) -> None:
        """
        Callback cuando cambian los filtros.

        Args:
            filters: Diccionario con valores de filtros
        """
        logger.info(f"Filters changed: {filters}")
        self._status_filter = filters.get("status", "all")
        self._role_filter = filters.get("role", "all")
        self._current_page = 1

        if self.page:
            self.page.run_task(self.load_staff)

    def _on_page_change(self, page: int) -> None:
        """
        Callback cuando cambia la página.

        Args:
            page: Número de página
        """
        logger.info(f"Page changed to: {page}")
        self._current_page = page
        if self.page:
            self.page.run_task(self.load_staff)

    def _on_row_click(self, row_data: dict) -> None:
        """
        Callback cuando se hace click en una fila.

        Args:
            row_data: Datos de la fila clickeada
        """
        staff_id = row_data.get("id")
        logger.info(f"Staff row clicked: ID={staff_id}")

        if self._on_view_detail_callback:
            self._on_view_detail_callback(staff_id)

    def _on_create_staff(self, e: ft.ControlEvent | None = None) -> None:
        """Callback para crear nuevo personal."""
        logger.info("Create staff button clicked")

        if self._on_create_callback:
            self._on_create_callback()

    def _on_edit_staff(self, row_data: dict) -> None:
        """
        Callback para editar un personal.

        Args:
            row_data: Datos de la fila a editar
        """
        staff_id = row_data.get("id")
        logger.info(f"Edit staff clicked: ID={staff_id}")

        if self._on_edit_callback:
            self._on_edit_callback(staff_id)

    def _on_delete_staff(self, row_data: dict) -> None:
        """
        Callback para eliminar un personal.

        Args:
            row_data: Datos de la fila a eliminar
        """
        staff_id = row_data.get("id")
        staff_name = row_data.get("full_name")
        logger.info(f"Delete staff clicked: ID={staff_id}")

        # Mostrar diálogo de confirmación
        self._confirm_dialog = ConfirmDialog(
            title=t("staff.delete"),
            message=t("staff.messages.delete_confirm").replace("{name}", staff_name),
            on_confirm=lambda: self._confirm_delete_staff(staff_id),
        )

        if self.page:
            self.page.dialog = self._confirm_dialog
            self._confirm_dialog.open = True
            self.page.update()

    async def _confirm_delete_staff(self, staff_id: int) -> None:
        """
        Confirma y ejecuta la eliminación de un personal.

        Args:
            staff_id: ID del personal a eliminar
        """
        logger.info(f"Confirming deletion of staff ID={staff_id}")

        try:
            from src.frontend.services.api import StaffAPI

            staff_api = StaffAPI()
            await staff_api.delete(staff_id)

            logger.success(f"Staff {staff_id} deleted successfully")

            # Recargar lista
            await self.load_staff()

        except Exception as e:
            logger.exception(f"Error deleting staff: {e}")

    def _on_state_changed(self) -> None:
        """
        Observer: Se ejecuta cuando cambia el estado de tema o idioma.

        Actualiza la interfaz.
        """
        logger.debug("StaffListView state changed, rebuilding content")
        self.content = self.build()
        if self.page:
            self.update()

    def refresh(self) -> None:
        """
        Refresca el listado de personal.

        Example:
            >>> staff_list.refresh()
        """
        logger.info("Refreshing staff list")
        if self.page:
            self.page.run_task(self.load_staff)
