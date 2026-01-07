"""
Vista de listado de empresas.

Muestra una tabla de empresas con filtros, búsqueda y paginación.
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


class CompanyListView(ft.Container):
    """
    Vista de listado de empresas con filtros y paginación.

    Muestra tabla de empresas con:
    - Búsqueda por nombre/trigrama
    - Filtros por estado, tipo y país
    - Paginación
    - Acciones de editar/eliminar
    - Botón para crear nueva empresa

    Example:
        >>> company_list = CompanyListView()
        >>> page.add(company_list)
    """

    def __init__(
        self,
        default_type_filter: str = "all",
        on_view_detail: Callable[[int, str], None] | None = None,
        on_create: Callable[[str], None] | None = None,
        on_edit: Callable[[int, str], None] | None = None,
    ):
        """
        Inicializa la vista de listado de empresas.

        Args:
            default_type_filter: Filtro inicial de tipo ("all", "CLIENT", "SUPPLIER")
                                Si es diferente de "all", el filtro de tipo se bloquea
            on_view_detail: Callback para ver detalle (company_id, company_type)
            on_create: Callback para crear nueva empresa (company_type)
            on_edit: Callback para editar empresa (company_id, company_type)
        """
        super().__init__()

        # Callbacks de navegación
        self._on_view_detail_callback = on_view_detail
        self._on_create_callback = on_create
        self._on_edit_callback = on_edit

        # Estado
        self._is_loading: bool = True
        self._error_message: str = ""
        self._companies: list[dict] = []
        self._total_companies: int = 0
        self._current_page: int = 1
        self._page_size: int = 20

        # Filtros
        self._search_query: str = ""
        self._status_filter: str = "all"
        self._type_filter: str = default_type_filter
        self._country_filter: str = "all"
        self._is_type_locked: bool = default_type_filter != "all"

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

        logger.info(f"CompanyListView initialized with type_filter={self._type_filter}")

    def _get_i18n_key_prefix(self) -> str:
        """
        Obtiene el prefijo de clave i18n según el tipo de filtro.

        Returns:
            "clients", "suppliers" o "companies"
        """
        if self._type_filter == "CLIENT":
            return "clients"
        elif self._type_filter == "SUPPLIER":
            return "suppliers"
        else:
            return "companies"

    def build(self) -> ft.Control:
        """
        Construye el componente de listado de empresas.

        Returns:
            Control de Flet con la vista completa
        """
        i18n_prefix = self._get_i18n_key_prefix()

        # Estados de carga/error/vacío
        if self._is_loading:
            loading_message = "Cargando " + t(f"{i18n_prefix}.title").lower() + "..."
            return ft.Container(
                content=LoadingSpinner(message=loading_message),
                expand=True,
                alignment=ft.Alignment(0, 0),  # center
            )

        if self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_companies,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),  # center
            )

        if not self._companies:
            # Icono y mensajes según el tipo
            if self._type_filter == "CLIENT":
                icon = ft.Icons.PEOPLE_OUTLINED
                empty_title = t("clients.title")
                empty_message = t("clients.no_clients")
                action_label = t("clients.create_first")
            elif self._type_filter == "SUPPLIER":
                icon = ft.Icons.FACTORY_OUTLINED
                empty_title = t("suppliers.title")
                empty_message = t("suppliers.no_suppliers")
                action_label = t("suppliers.create_first")
            else:
                icon = ft.Icons.BUSINESS_OUTLINED
                empty_title = t("companies.title")
                empty_message = t("companies.no_companies")
                action_label = t("companies.create_first")

            return ft.Container(
                content=EmptyState(
                    icon=icon,
                    title=empty_title,
                    message=empty_message,
                    action_text=action_label,
                    on_action=self._on_create_company,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),  # center
            )

        # Contenido principal con datos
        # SearchBar
        self._search_bar = SearchBar(
            placeholder=t(f"{i18n_prefix}.search_placeholder"),
            on_search=self._on_search,
        )

        # FilterPanel con filtros
        filters_config = [
            {
                "key": "status",
                "label": "companies.filters.status",
                "type": "dropdown",
                "options": [
                    {"label": "companies.filters.all", "value": "all"},
                    {"label": "companies.filters.active", "value": "active"},
                    {"label": "companies.filters.inactive", "value": "inactive"},
                ],
                "default": "all",
            },
        ]

        # Solo agregar filtro de tipo si no está bloqueado
        if not self._is_type_locked:
            filters_config.append({
                "key": "type",
                "label": "companies.filters.type",
                "type": "dropdown",
                "options": [
                    {"label": "companies.filters.all", "value": "all"},
                    {"label": "companies.filters.customer", "value": "CLIENT"},
                    {"label": "companies.filters.supplier", "value": "SUPPLIER"},
                    {"label": "companies.filters.both", "value": "BOTH"},
                ],
                "default": "all",
            })

        filters_config.append({
            "key": "country",
            "label": "companies.filters.country",
            "type": "dropdown",
            "options": [],  # Se cargarán dinámicamente
            "default": "all",
        })

        self._filter_panel = FilterPanel(
            filters=filters_config,
            on_filter_change=self._on_filter_change,
        )

        # DataTable con columnas de empresas
        self._data_table = DataTable(
            columns=[
                {"key": "name", "label": "companies.columns.name", "sortable": True},
                {"key": "trigram", "label": "companies.columns.trigram", "sortable": True},
                {"key": "phone", "label": "companies.columns.phone", "sortable": False},
                {"key": "city", "label": "companies.columns.city", "sortable": True},
                {"key": "status", "label": "companies.columns.status", "sortable": True},
            ],
            on_row_click=self._on_row_click,
            on_edit=self._on_edit_company,
            on_delete=self._on_delete_company,
            page_size=self._page_size,
            on_page_change=self._on_page_change,
        )

        # Asignar datos al DataTable si hay empresas cargadas
        if self._companies:
            formatted_data = self._format_companies_for_table(self._companies)
            self._data_table.set_data(
                formatted_data,
                total=self._total_companies,
                current_page=self._current_page,
            )

        # Header con título y botón crear
        header = ft.Row(
            controls=[
                ft.Text(
                    t(f"{i18n_prefix}.list_title"),
                    size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                    expand=True,
                ),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    on_click=self._on_create_company,
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

        Carga las empresas y los datos de lookups.
        """
        logger.info("CompanyListView mounted, loading data")

        # Suscribirse a cambios de estado
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)

        # Cargar datos
        if self.page:
            self.page.run_task(self._load_initial_data)

    def will_unmount(self) -> None:
        """
        Lifecycle: Se ejecuta cuando el componente se desmonta.

        Limpia los observers.
        """
        logger.info("CompanyListView unmounting")
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def _load_initial_data(self) -> None:
        """Carga los datos iniciales (empresas y lookups)."""
        logger.info("Loading initial data for CompanyListView")

        # Cargar lookups para filtros
        await self._load_country_options()

        # Cargar empresas
        await self.load_companies()

    async def _load_country_options(self) -> None:
        """Carga las opciones de países desde la API de lookups."""
        try:
            logger.debug("Loading country options for filter")
            from src.frontend.services.api import LookupAPI

            lookup_api = LookupAPI()
            countries = await lookup_api.get_lookup("countries")

            # Actualizar opciones del filtro de país
            if self._filter_panel and countries:
                country_options = [{"label": "companies.filters.all", "value": "all"}]
                country_options.extend([
                    {"label": c["name"], "value": str(c["id"])}
                    for c in countries
                ])

                self._filter_panel.update_filter_options("country", country_options)
                logger.success(f"Loaded {len(countries)} country options")

        except Exception as e:
            logger.warning(f"Error loading country options: {e}")

    async def load_companies(self) -> None:
        """
        Carga las empresas desde la API.

        Aplica los filtros y búsqueda actuales.
        """
        logger.info(
            f"Loading companies: page={self._current_page}, "
            f"search='{self._search_query}', filters={self._get_active_filters()}"
        )

        self._is_loading = True
        self._error_message = ""

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import CompanyAPI

            company_api = CompanyAPI()

            # Preparar parámetros de búsqueda
            params: dict[str, Any] = {
                "page": self._current_page,
                "page_size": self._page_size,
            }

            # Agregar búsqueda si existe
            if self._search_query:
                response = await company_api.search(
                    query=self._search_query,
                    **params,
                )
            else:
                # Agregar filtros
                filters = self._get_active_filters()
                response = await company_api.get_all(**params, **filters)

            # Actualizar datos
            self._companies = response.get("items", [])
            self._total_companies = response.get("total", 0)

            logger.success(
                f"Loaded {len(self._companies)} companies "
                f"(total: {self._total_companies})"
            )

            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading companies: {e}")
            self._error_message = f"Error al cargar empresas: {str(e)}"
            self._is_loading = False

        # Reconstruir contenido con los datos cargados o error
        self.content = self.build()
        if self.page:
            self.update()

    def _format_companies_for_table(self, companies: list[dict]) -> list[dict]:
        """
        Formatea los datos de empresas para la tabla.

        Args:
            companies: Lista de empresas desde la API

        Returns:
            Lista formateada para DataTable
        """
        formatted = []
        for company in companies:
            formatted.append({
                "id": company.get("id"),
                "name": company.get("name", ""),
                "trigram": company.get("trigram", ""),
                "phone": company.get("phone", "-"),
                "city": company.get("city_name", "-"),
                "status": "Activa" if company.get("is_active") else "Inactiva",
                "_original": company,  # Guardar datos originales
            })
        return formatted

    def _get_active_filters(self) -> dict[str, Any]:
        """
        Obtiene los filtros activos (que no sean "all").

        Returns:
            Diccionario con filtros activos
        """
        filters: dict[str, Any] = {}

        if self._status_filter != "all":
            filters["is_active"] = self._status_filter == "active"

        if self._type_filter != "all":
            # Mapear tipo de empresa a ID (CLIENT=1, SUPPLIER=2)
            type_map = {"CLIENT": 1, "SUPPLIER": 2}
            filters["company_type_id"] = type_map.get(self._type_filter)

        if self._country_filter != "all":
            filters["country_code"] = self._country_filter

        return filters

    def _on_search(self, query: str) -> None:
        """
        Callback cuando se realiza una búsqueda.

        Args:
            query: Texto de búsqueda
        """
        logger.info(f"Search triggered: '{query}'")
        self._search_query = query
        self._current_page = 1  # Resetear a primera página
        if self.page:
            self.page.run_task(self.load_companies)

    def _on_clear_search(self) -> None:
        """Callback cuando se limpia la búsqueda."""
        logger.info("Search cleared")
        self._search_query = ""
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_companies)

    def _on_filter_change(self, filters: dict[str, Any]) -> None:
        """
        Callback cuando cambian los filtros.

        Args:
            filters: Diccionario con valores de filtros
        """
        logger.info(f"Filters changed: {filters}")
        self._status_filter = filters.get("status", "all")
        self._type_filter = filters.get("type", "all")
        self._country_filter = filters.get("country", "all")
        self._current_page = 1  # Resetear a primera página

        if self.page:
            self.page.run_task(self.load_companies)

    def _on_page_change(self, page: int) -> None:
        """
        Callback cuando cambia la página.

        Args:
            page: Número de página
        """
        logger.info(f"Page changed to: {page}")
        self._current_page = page
        if self.page:
            self.page.run_task(self.load_companies)

    def _on_row_click(self, row_data: dict) -> None:
        """
        Callback cuando se hace click en una fila.

        Args:
            row_data: Datos de la fila clickeada
        """
        company_id = row_data.get("id")
        logger.info(f"Company row clicked: ID={company_id}")

        # Navegar a vista de detalle
        if self._on_view_detail_callback:
            self._on_view_detail_callback(company_id, self._type_filter)

    def _on_create_company(self, e: ft.ControlEvent | None = None) -> None:
        """Callback para crear nueva empresa."""
        logger.info("Create company button clicked")

        # Navegar a formulario de creación
        if self._on_create_callback:
            self._on_create_callback(self._type_filter)

    def _on_edit_company(self, row_data: dict) -> None:
        """
        Callback para editar una empresa.

        Args:
            row_data: Datos de la fila a editar
        """
        company_id = row_data.get("id")
        logger.info(f"Edit company clicked: ID={company_id}")

        # Navegar a formulario de edición
        if self._on_edit_callback:
            self._on_edit_callback(company_id, self._type_filter)

    def _on_delete_company(self, row_data: dict) -> None:
        """
        Callback para eliminar una empresa.

        Args:
            row_data: Datos de la fila a eliminar
        """
        company_id = row_data.get("id")
        company_name = row_data.get("name")
        logger.info(f"Delete company clicked: ID={company_id}")

        i18n_prefix = self._get_i18n_key_prefix()

        # Mostrar diálogo de confirmación
        entity_type = t(f"{i18n_prefix}.title").lower()[:-1]  # Quitar la 's' final
        self._confirm_dialog = ConfirmDialog(
            title=t(f"{i18n_prefix}.delete"),
            message=f"¿Está seguro de que desea eliminar {entity_type} '{company_name}'?",
            on_confirm=lambda: self._confirm_delete_company(company_id),
        )

        if self.page:
            self.page.dialog = self._confirm_dialog
            self._confirm_dialog.open = True
            self.page.update()

    async def _confirm_delete_company(self, company_id: int) -> None:
        """
        Confirma y ejecuta la eliminación de una empresa.

        Args:
            company_id: ID de la empresa a eliminar
        """
        logger.info(f"Confirming deletion of company ID={company_id}")

        try:
            from src.frontend.services.api import CompanyAPI

            company_api = CompanyAPI()
            await company_api.delete(company_id)

            logger.success(f"Company {company_id} deleted successfully")

            # Recargar lista
            await self.load_companies()

            # TODO: Mostrar notificación de éxito

        except Exception as e:
            logger.exception(f"Error deleting company: {e}")
            # TODO: Mostrar notificación de error

    def _on_state_changed(self) -> None:
        """
        Observer: Se ejecuta cuando cambia el estado de tema o idioma.

        Actualiza la interfaz.
        """
        logger.debug("CompanyListView state changed, rebuilding content")
        # Reconstruir el contenido con las nuevas traducciones
        self.content = self.build()
        if self.page:
            self.update()

    def refresh(self) -> None:
        """
        Refresca el listado de empresas.

        Example:
            >>> company_list.refresh()
        """
        logger.info("Refreshing company list")
        if self.page:
            self.page.run_task(self.load_companies)
