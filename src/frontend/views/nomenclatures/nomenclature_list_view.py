"""
Vista de listado de nomenclaturas.

Muestra una tabla de nomenclaturas con filtros, búsqueda y paginación.
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


class NomenclatureListView(ft.Container):
    """
    Vista de listado de nomenclaturas con filtros y paginación.

    Muestra tabla de nomenclaturas con:
    - Búsqueda por código/nombre
    - Filtros por estado
    - Paginación
    - Acciones de editar/eliminar
    - Botón para crear nueva nomenclatura

    Example:
        >>> nomenclature_list = NomenclatureListView(
        ...     on_create=lambda: navigate_to_form(),
        ...     on_edit=lambda id: navigate_to_edit(id),
        ...     on_view_detail=lambda id: navigate_to_detail(id),
        ... )
        >>> page.add(nomenclature_list)
    """

    def __init__(
        self,
        on_view_detail: Callable[[int], None] | None = None,
        on_create: Callable[[], None] | None = None,
        on_edit: Callable[[int], None] | None = None,
    ):
        """
        Inicializa la vista de listado de nomenclaturas.

        Args:
            on_view_detail: Callback para ver detalle (nomenclature_id)
            on_create: Callback para crear nueva nomenclatura
            on_edit: Callback para editar nomenclatura (nomenclature_id)
        """
        super().__init__()

        # Callbacks de navegación
        self._on_view_detail_callback = on_view_detail
        self._on_create_callback = on_create
        self._on_edit_callback = on_edit

        # Estado
        self._is_loading: bool = True
        self._error_message: str = ""
        self._nomenclatures: list[dict] = []
        self._total_nomenclatures: int = 0
        self._current_page: int = 1
        self._page_size: int = 20

        # Filtros
        self._search_query: str = ""
        self._status_filter: str = "all"

        # Componentes
        self._search_bar: SearchBar | None = None
        self._filter_panel: FilterPanel | None = None
        self._data_table: DataTable | None = None

        # ID de la nomenclatura pendiente de eliminar
        self._pending_delete_id: int | None = None

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = 0

        # Construir contenido inicial
        self.content = self.build()

        logger.info("NomenclatureListView initialized")

    def build(self) -> ft.Control:
        """Construye el componente de listado de nomenclaturas."""
        # Estados de carga/error/vacío
        if self._is_loading:
            return ft.Container(
                content=LoadingSpinner(message=f"Cargando {t('nomenclatures.title').lower()}..."),
                expand=True,
                alignment=ft.alignment.center,
            )

        if self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_nomenclatures,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )

        if not self._nomenclatures:
            return ft.Container(
                content=EmptyState(
                    icon=ft.Icons.LIST_ALT_OUTLINED,
                    title=t("nomenclatures.title"),
                    message=t("nomenclatures.no_nomenclatures_message"),
                    action_text=t("nomenclatures.create_first"),
                    on_action=self._on_create_nomenclature,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )

        # Contenido principal con datos
        header = ft.Row(
            controls=[
                ft.Text(
                    t("nomenclatures.list_title"),
                    size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                    expand=True,
                ),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    text=t("nomenclatures.create"),
                    on_click=self._on_create_nomenclature,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self._search_bar = SearchBar(
            placeholder=t("nomenclatures.search_placeholder"),
            on_search=self._on_search,
        )

        self._filter_panel = FilterPanel(
            filters=[
                {
                    "key": "status",
                    "label": "nomenclatures.filters.status",
                    "type": "dropdown",
                    "options": [
                        {"label": "nomenclatures.filters.all", "value": "all"},
                        {"label": "nomenclatures.filters.active", "value": "active"},
                        {"label": "nomenclatures.filters.inactive", "value": "inactive"},
                    ],
                    "default": "all",
                },
            ],
            on_filter_change=self._on_filter_change,
        )

        self._data_table = DataTable(
            columns=[
                {"key": "revision", "label": "nomenclatures.columns.revision", "sortable": True},
                {"key": "reference", "label": "nomenclatures.columns.reference", "sortable": True},
                {"key": "name", "label": "nomenclatures.columns.name", "sortable": True},
                {"key": "articles", "label": "nomenclatures.columns.articles", "sortable": True},
                {"key": "quantity", "label": "nomenclatures.columns.stock", "sortable": True},
                {"key": "minimum_stock", "label": "nomenclatures.columns.minimum_stock", "sortable": True},
                {"key": "sales_type", "label": "nomenclatures.columns.sales_type", "sortable": True},
            ],
            on_row_click=self._on_row_click,
            on_edit=self._on_edit_nomenclature,
            on_delete=self._on_delete_nomenclature,
            page_size=self._page_size,
            on_page_change=self._on_page_change,
        )

        # Asignar datos al DataTable si hay nomenclaturas cargadas
        if self._nomenclatures:
            formatted_data = self._format_nomenclatures_for_table(self._nomenclatures)
            self._data_table.set_data(
                formatted_data,
                total=self._total_nomenclatures,
                current_page=self._current_page,
            )

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
        logger.info("NomenclatureListView mounted")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        if self.page:
            self.page.run_task(self.load_nomenclatures)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_nomenclatures(self) -> None:
        """Carga las nomenclaturas desde la API."""
        logger.info(f"Loading nomenclatures: page={self._current_page}")
        self._is_loading = True
        self._error_message = ""

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            
            # Calcular skip/limit para paginación
            skip = (self._current_page - 1) * self._page_size
            limit = self._page_size

            if self._search_query:
                response = await product_api.search(query=self._search_query)
                self._nomenclatures = response[:self._page_size]  # Aplicar paginación local
                self._total_nomenclatures = len(response)
            else:
                # Usar el endpoint específico para filtrar por tipo
                self._nomenclatures = await product_api.get_by_type(
                    product_type="nomenclature", 
                    skip=skip, 
                    limit=limit
                )
                # Para obtener el total, necesitamos hacer otra llamada sin límites
                all_nomenclatures = await product_api.get_by_type(product_type="nomenclature")
                self._total_nomenclatures = len(all_nomenclatures)

            logger.success(f"Loaded {len(self._nomenclatures)} nomenclatures")
            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading nomenclatures: {e}")
            self._error_message = f"Error al cargar nomenclaturas: {str(e)}"
            self._is_loading = False

        # Reconstruir contenido con los datos cargados o error
        self.content = self.build()
        if self.page:
            self.update()

    def _format_nomenclatures_for_table(self, nomenclatures: list[dict]) -> list[dict]:
        """Formatea los datos de nomenclaturas para la tabla."""
        formatted = []
        current_lang = app_state.i18n.current_language
        
        for nomenclature in nomenclatures:
            # Obtener designación según el idioma actual
            if current_lang == "en":
                designation = nomenclature.get("designation_en", nomenclature.get("designation_es", ""))
            elif current_lang == "fr":
                designation = nomenclature.get("designation_fr", nomenclature.get("designation_es", ""))
            else:
                designation = nomenclature.get("designation_es", "")
            
            # Obtener tipo de venta
            sales_type = nomenclature.get("sales_type", {})
            sales_type_name = sales_type.get("name", "") if sales_type else ""
            
            # Contar artículos si están disponibles
            articles_count = len(nomenclature.get("components", []))
            
            # Obtener texto para artículos según idioma
            if current_lang == "en":
                articles_text = f"{articles_count} articles" if articles_count != 1 else "1 article"
            elif current_lang == "fr":
                articles_text = f"{articles_count} articles" if articles_count != 1 else "1 article"
            else:
                articles_text = f"{articles_count} artículos" if articles_count != 1 else "1 artículo"
            
            formatted.append({
                "id": nomenclature.get("id"),
                "revision": nomenclature.get("revision", ""),
                "reference": nomenclature.get("reference", ""),
                "name": designation,
                "articles": articles_text,
                "quantity": f"{float(nomenclature.get('stock_quantity', 0) or 0):.3f}",
                "minimum_stock": f"{float(nomenclature.get('minimum_stock', 0) or 0):.3f}",
                "sales_type": sales_type_name,
                "_original": nomenclature,
            })
        return formatted

    def _get_active_filters(self) -> dict[str, Any]:
        """Obtiene los filtros activos."""
        filters: dict[str, Any] = {}
        if self._status_filter != "all":
            filters["is_active"] = self._status_filter == "active"

        # product_type se maneja en params, no aquí

        return filters

    def _on_search(self, query: str) -> None:
        """Callback cuando se realiza una búsqueda."""
        self._search_query = query
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_nomenclatures)

    def _on_clear_search(self) -> None:
        """Callback cuando se limpia la búsqueda."""
        self._search_query = ""
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_nomenclatures)

    def _on_filter_change(self, filters: dict[str, Any]) -> None:
        """Callback cuando cambian los filtros."""
        self._status_filter = filters.get("status", "all")
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_nomenclatures)

    def _on_page_change(self, page: int) -> None:
        """Callback cuando cambia la página."""
        self._current_page = page
        if self.page:
            self.page.run_task(self.load_nomenclatures)

    def _on_row_click(self, row_data: dict) -> None:
        """Callback cuando se hace click en una fila."""
        nomenclature_id = row_data.get("id")
        logger.info(f"Nomenclature row clicked: ID={nomenclature_id}")

        if self._on_view_detail_callback and nomenclature_id:
            self._on_view_detail_callback(nomenclature_id)

    def _on_create_nomenclature(self, e: ft.ControlEvent | None = None) -> None:
        """Callback para crear nueva nomenclatura."""
        logger.info("Create nomenclature button clicked")

        if self._on_create_callback:
            self._on_create_callback()

    def _on_edit_nomenclature(self, row_data: dict) -> None:
        """Callback para editar una nomenclatura."""
        nomenclature_id = row_data.get("id")
        logger.info(f"Edit nomenclature clicked: ID={nomenclature_id}")

        if self._on_edit_callback and nomenclature_id:
            self._on_edit_callback(nomenclature_id)

    def _on_delete_nomenclature(self, row_data: dict) -> None:
        """Callback para eliminar una nomenclatura."""
        nomenclature_id = row_data.get("id")
        nomenclature_name = row_data.get("name", "")
        logger.info(f"Delete nomenclature clicked: ID={nomenclature_id}")

        # Guardar ID para la confirmación
        self._pending_delete_id = nomenclature_id

        # Crear y mostrar diálogo de confirmación
        if self.page:
            confirm_dialog = ConfirmDialog(
                title=t("common.confirm_delete"),
                message=t("nomenclatures.messages.confirm_delete_message"),
                confirm_text=t("common.delete"),
                cancel_text=t("common.cancel"),
                on_confirm=self._on_confirm_delete,
                on_cancel=self._on_cancel_delete,
                variant="danger",
            )
            confirm_dialog.show(self.page)

    def _on_confirm_delete(self) -> None:
        """Callback cuando se confirma la eliminación."""
        if self._pending_delete_id and self.page:
            self.page.run_task(self._delete_nomenclature)

    def _on_cancel_delete(self) -> None:
        """Callback cuando se cancela la eliminación."""
        self._pending_delete_id = None

    async def _delete_nomenclature(self) -> None:
        """Elimina la nomenclatura pendiente."""
        if not self._pending_delete_id:
            return

        nomenclature_id = self._pending_delete_id
        logger.info(f"Deleting nomenclature ID={nomenclature_id}")

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            await product_api.delete(nomenclature_id)

            logger.success(f"Nomenclature deleted: ID={nomenclature_id}")

            # Mostrar mensaje de éxito
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(t("nomenclatures.messages.deleted")),
                    bgcolor=ft.Colors.GREEN,
                    duration=3000,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()

            # Recargar lista
            await self.load_nomenclatures()

        except Exception as e:
            logger.exception(f"Error deleting nomenclature: {e}")

            # Mostrar mensaje de error
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(f"Error: {str(e)}"),
                    bgcolor=ft.Colors.RED,
                    duration=5000,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()

        finally:
            self._pending_delete_id = None

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        logger.debug("NomenclatureListView state changed, rebuilding content")
        # Reconstruir el contenido con las nuevas traducciones
        self.content = self.build()
        if self.page:
            self.update()

    def refresh(self) -> None:
        """Refresca el listado de nomenclaturas."""
        if self.page:
            self.page.run_task(self.load_nomenclatures)
