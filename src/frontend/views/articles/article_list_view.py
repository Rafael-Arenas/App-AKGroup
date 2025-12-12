"""
Vista de listado de artículos.

Muestra una tabla de artículos con filtros, búsqueda y paginación.
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


class ArticleListView(ft.Container):
    """
    Vista de listado de artículos con filtros y paginación.

    Muestra tabla de artículos con:
    - Búsqueda por código/nombre
    - Filtros por estado
    - Paginación
    - Acciones de editar/eliminar
    - Botón para crear nuevo artículo

    Example:
        >>> article_list = ArticleListView(
        ...     on_create=lambda: navigate_to_form(),
        ...     on_edit=lambda id: navigate_to_edit(id),
        ...     on_view_detail=lambda id: navigate_to_detail(id),
        ... )
        >>> page.add(article_list)
    """

    def __init__(
        self,
        on_view_detail: Callable[[int], None] | None = None,
        on_create: Callable[[], None] | None = None,
        on_edit: Callable[[int], None] | None = None,
    ):
        """
        Inicializa la vista de listado de artículos.

        Args:
            on_view_detail: Callback para ver detalle (article_id)
            on_create: Callback para crear nuevo artículo
            on_edit: Callback para editar artículo (article_id)
        """
        super().__init__()

        # Callbacks de navegación
        self._on_view_detail_callback = on_view_detail
        self._on_create_callback = on_create
        self._on_edit_callback = on_edit

        # Estado
        self._is_loading: bool = True
        self._error_message: str = ""
        self._articles: list[dict] = []
        self._total_articles: int = 0
        self._current_page: int = 1
        self._page_size: int = 20

        # Filtros
        self._search_query: str = ""
        self._status_filter: str = "all"

        # Componentes
        self._search_bar: SearchBar | None = None
        self._filter_panel: FilterPanel | None = None
        self._data_table: DataTable | None = None

        # ID del artículo pendiente de eliminar
        self._pending_delete_id: int | None = None

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = 0

        # Construir contenido inicial
        self.content = self.build()

        logger.info("ArticleListView initialized")

    def build(self) -> ft.Control:
        """Construye el componente de listado de artículos."""
        # Estados de carga/error/vacío
        if self._is_loading:
            return ft.Container(
                content=LoadingSpinner(message=f"Cargando {t('articles.title').lower()}..."),
                expand=True,
                alignment=ft.alignment.center,
            )

        if self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_articles,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )

        if not self._articles:
            return ft.Container(
                content=EmptyState(
                    icon=ft.Icons.INVENTORY_2_OUTLINED,
                    title=t("articles.title"),
                    message=t("articles.no_articles_message"),
                    action_text=t("articles.create_first"),
                    on_action=self._on_create_article,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )

        # Contenido principal con datos
        header = ft.Row(
            controls=[
                ft.Text(
                    t("articles.list_title"),
                    size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                    expand=True,
                ),
                ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    text=t("articles.create"),
                    on_click=self._on_create_article,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        self._search_bar = SearchBar(
            placeholder=t("articles.search_placeholder"),
            on_search=self._on_search,
        )

        self._filter_panel = FilterPanel(
            filters=[
                {
                    "key": "status",
                    "label": "articles.filters.status",
                    "type": "dropdown",
                    "options": [
                        {"label": "articles.filters.all", "value": "all"},
                        {"label": "articles.filters.active", "value": "active"},
                        {"label": "articles.filters.inactive", "value": "inactive"},
                    ],
                    "default": "all",
                },
            ],
            on_filter_change=self._on_filter_change,
        )

        self._data_table = DataTable(
            columns=[
                {"key": "code", "label": "articles.columns.code", "sortable": True},
                {"key": "name", "label": "articles.columns.name", "sortable": True},
                {"key": "unit", "label": "articles.columns.unit", "sortable": False},
                {"key": "cost", "label": "articles.columns.cost", "sortable": True},
                {"key": "status", "label": "articles.columns.status", "sortable": True},
            ],
            on_row_click=self._on_row_click,
            on_edit=self._on_edit_article,
            on_delete=self._on_delete_article,
            page_size=self._page_size,
            on_page_change=self._on_page_change,
        )

        # Asignar datos al DataTable si hay artículos cargados
        if self._articles:
            formatted_data = self._format_articles_for_table(self._articles)
            self._data_table.set_data(
                formatted_data,
                total=self._total_articles,
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
        logger.info("ArticleListView mounted")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        if self.page:
            self.page.run_task(self.load_articles)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_articles(self) -> None:
        """Carga los artículos desde la API."""
        logger.info(f"Loading articles: page={self._current_page}")
        self._is_loading = True
        self._error_message = ""

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
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

            self._articles = response.get("items", [])
            self._total_articles = response.get("total", 0)

            logger.success(f"Loaded {len(self._articles)} articles")
            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading articles: {e}")
            self._error_message = f"Error al cargar artículos: {str(e)}"
            self._is_loading = False

        # Reconstruir contenido con los datos cargados o error
        self.content = self.build()
        if self.page:
            self.update()

    def _format_articles_for_table(self, articles: list[dict]) -> list[dict]:
        """Formatea los datos de artículos para la tabla."""
        formatted = []
        for article in articles:
            formatted.append({
                "id": article.get("id"),
                "code": article.get("reference", ""),
                "name": article.get("designation_es", ""),
                "unit": article.get("unit", "-"),
                "cost": f"${float(article.get('cost_price', 0) or 0):.2f}",
                "status": t("common.active") if article.get("is_active") else t("common.inactive"),
                "_original": article,
            })
        return formatted

    def _get_active_filters(self) -> dict[str, Any]:
        """Obtiene los filtros activos."""
        filters: dict[str, Any] = {}
        if self._status_filter != "all":
            filters["is_active"] = self._status_filter == "active"

        # Filtrar solo artículos (no nomenclaturas)
        filters["product_type"] = "article"

        return filters

    def _on_search(self, query: str) -> None:
        """Callback cuando se realiza una búsqueda."""
        self._search_query = query
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_articles)

    def _on_clear_search(self) -> None:
        """Callback cuando se limpia la búsqueda."""
        self._search_query = ""
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_articles)

    def _on_filter_change(self, filters: dict[str, Any]) -> None:
        """Callback cuando cambian los filtros."""
        self._status_filter = filters.get("status", "all")
        self._current_page = 1
        if self.page:
            self.page.run_task(self.load_articles)

    def _on_page_change(self, page: int) -> None:
        """Callback cuando cambia la página."""
        self._current_page = page
        if self.page:
            self.page.run_task(self.load_articles)

    def _on_row_click(self, row_data: dict) -> None:
        """Callback cuando se hace click en una fila."""
        article_id = row_data.get("id")
        logger.info(f"Article row clicked: ID={article_id}")

        if self._on_view_detail_callback and article_id:
            self._on_view_detail_callback(article_id)

    def _on_create_article(self, e: ft.ControlEvent | None = None) -> None:
        """Callback para crear nuevo artículo."""
        logger.info("Create article button clicked")

        if self._on_create_callback:
            self._on_create_callback()

    def _on_edit_article(self, row_data: dict) -> None:
        """Callback para editar un artículo."""
        article_id = row_data.get("id")
        logger.info(f"Edit article clicked: ID={article_id}")

        if self._on_edit_callback and article_id:
            self._on_edit_callback(article_id)

    def _on_delete_article(self, row_data: dict) -> None:
        """Callback para eliminar un artículo."""
        article_id = row_data.get("id")
        article_name = row_data.get("name", "")
        logger.info(f"Delete article clicked: ID={article_id}")

        # Guardar ID para la confirmación
        self._pending_delete_id = article_id

        # Crear y mostrar diálogo de confirmación
        if self.page:
            confirm_dialog = ConfirmDialog(
                title=t("common.confirm_delete"),
                message=t("articles.messages.confirm_delete_message"),
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
            self.page.run_task(self._delete_article)

    def _on_cancel_delete(self) -> None:
        """Callback cuando se cancela la eliminación."""
        self._pending_delete_id = None

    async def _delete_article(self) -> None:
        """Elimina el artículo pendiente."""
        if not self._pending_delete_id:
            return

        article_id = self._pending_delete_id
        logger.info(f"Deleting article ID={article_id}")

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            await product_api.delete(article_id)

            logger.success(f"Article deleted: ID={article_id}")

            # Mostrar mensaje de éxito
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(t("articles.messages.deleted")),
                    bgcolor=ft.Colors.GREEN,
                    duration=3000,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()

            # Recargar lista
            await self.load_articles()

        except Exception as e:
            logger.exception(f"Error deleting article: {e}")

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
        logger.debug("ArticleListView state changed, rebuilding content")
        # Reconstruir el contenido con las nuevas traducciones
        self.content = self.build()
        if self.page:
            self.update()

    def refresh(self) -> None:
        """Refresca el listado de artículos."""
        if self.page:
            self.page.run_task(self.load_articles)
