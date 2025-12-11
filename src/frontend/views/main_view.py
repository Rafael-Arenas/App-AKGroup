"""
Vista principal de la aplicación.

Contenedor principal que integra AppBar, NavigationRail, Breadcrumb y área de contenido.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.navigation_config import get_navigation_item_by_index
from src.frontend.i18n.translation_manager import t
from src.frontend.components.navigation import (
    CustomAppBar,
    CustomNavigationRail,
    Breadcrumb,
)


class MainView(ft.Container):
    """
    Vista principal contenedora de la aplicación.

    Proporciona la estructura base con navegación, breadcrumb y área de contenido.
    Implementa observers para actualizaciones automáticas de navegación, idioma y tema.

    Args:
        on_logout: Callback cuando el usuario hace logout
        on_profile: Callback cuando el usuario accede a perfil
        on_theme_change: Callback cuando cambia el tema
        on_language_change: Callback cuando cambia el idioma

    Example:
        >>> main_view = MainView(
        ...     on_logout=handle_logout,
        ...     on_profile=handle_profile,
        ... )
        >>> page.add(main_view)
    """

    def __init__(
        self,
        on_logout: Callable[[], None] | None = None,
        on_profile: Callable[[], None] | None = None,
        on_theme_change: Callable[[str], None] | None = None,
        on_language_change: Callable[[str], None] | None = None,
    ):
        """Inicializa la vista principal."""
        super().__init__()
        self.on_logout = on_logout
        self.on_profile = on_profile
        self.on_theme_change = on_theme_change
        self.on_language_change = on_language_change

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = 0

        # Componentes principales
        self._app_bar: CustomAppBar | None = None
        self._navigation_rail: CustomNavigationRail | None = None
        self._breadcrumb: Breadcrumb | None = None
        self._breadcrumb_container: ft.Container | None = None
        self._content_area: ft.Container | None = None
        self._current_view: ft.Control | None = None

        # Construir el contenido
        self.content = self._build()

        logger.info("MainView initialized")

    def _build(self) -> ft.Control:
        """
        Construye el componente de vista principal.

        Returns:
            Control de Flet con la estructura completa
        """
        is_dark = app_state.theme.is_dark_mode

        # Crear AppBar
        self._app_bar = CustomAppBar(
            on_logout=self.on_logout,
            on_profile_click=self.on_profile,
            on_settings_click=None,  # TODO: Implementar settings
        )

        # Crear NavigationRail
        self._navigation_rail = CustomNavigationRail(
            on_destination_change=self._on_destination_change,
        )

        # Crear Breadcrumb con contenedor
        self._breadcrumb = Breadcrumb(on_navigate=self._on_breadcrumb_navigate)
        self._breadcrumb_container = ft.Container(
            content=self._breadcrumb,
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_LG,
                vertical=LayoutConstants.PADDING_SM,
            ),
            border=ft.border.only(
                bottom=ft.BorderSide(1),
            ),
        )

        # Crear área de contenido
        self._content_area = ft.Container(
            content=ft.Column(
                controls=[],
                expand=True,
            ),
            expand=True,
            padding=0,
        )

        # Cargar vista inicial (Dashboard)
        self._load_initial_view()

        # Layout principal
        main_layout = ft.Column(
            controls=[
                self._app_bar,
                ft.Row(
                    controls=[
                        self._navigation_rail,
                        ft.Column(
                            controls=[
                                self._breadcrumb_container,
                                self._content_area,
                            ],
                            expand=True,
                            spacing=0,
                        ),
                    ],
                    expand=True,
                    spacing=0,
                ),
            ],
            spacing=0,
            expand=True,
        )

        return ft.Container(
            content=main_layout,
            expand=True,
            padding=0,
        )

    def did_mount(self) -> None:
        """
        Lifecycle: Se ejecuta cuando el componente se monta en la página.

        Suscribe observers a los estados de navegación, idioma y tema.
        """
        logger.info("MainView mounted, subscribing to state observers")

        # Suscribirse a cambios de navegación
        app_state.navigation.add_observer(self._on_navigation_changed)

        # Actualizar breadcrumb inicial
        self._update_breadcrumb()

        # Suscribirse a cambios de idioma
        app_state.i18n.add_observer(self._on_i18n_changed)

        # Suscribirse a cambios de tema
        app_state.theme.add_observer(self._on_theme_changed)

        logger.success("MainView observers subscribed successfully")

    def will_unmount(self) -> None:
        """
        Lifecycle: Se ejecuta cuando el componente se desmonta.

        Limpia los observers para evitar memory leaks.
        """
        logger.info("MainView unmounting, removing observers")

        # Remover observers
        app_state.navigation.remove_observer(self._on_navigation_changed)
        app_state.i18n.remove_observer(self._on_i18n_changed)
        app_state.theme.remove_observer(self._on_theme_changed)

        logger.success("MainView observers removed")

    def _load_initial_view(self) -> None:
        """Carga la vista inicial (Dashboard)."""
        logger.info("Loading initial view (Dashboard)")
        self._set_view_content(0)

        # Actualizar breadcrumb para dashboard
        app_state.navigation.set_breadcrumb([
            {"label": "dashboard.title", "route": "/"}
        ])

    def _on_destination_change(self, index: int) -> None:
        """
        Callback cuando cambia el destino de navegación.

        Args:
            index: Índice de la sección seleccionada

        Example:
            >>> self._on_destination_change(1)  # Navega a Companies
        """
        logger.info(f"Navigation destination changed to index: {index}")

        # Obtener información del item de navegación
        nav_item = get_navigation_item_by_index(index)
        if not nav_item:
            logger.error(f"Navigation item not found for index: {index}")
            return

        # Actualizar estado de navegación
        app_state.navigation.set_section(
            index=index,
            title=nav_item["label"],
            route=nav_item["route"],
        )

        # Actualizar breadcrumb
        app_state.navigation.set_breadcrumb([
            {"label": nav_item["label"], "route": nav_item["route"]}
        ])

        # Cambiar vista
        self._set_view_content(index)

    def _set_view_content(self, index: int) -> None:
        """
        Establece el contenido de la vista según el índice.

        Args:
            index: Índice de la sección
        """
        logger.debug(f"Setting view content for index: {index}")

        # Obtener vista correspondiente
        view = self._get_view_for_section(index)

        if view:
            self._current_view = view
            if self._content_area:
                self._content_area.content = view
                if self.page:
                    self.update()
            logger.success(f"View content set for index: {index}")
        else:
            logger.error(f"No view found for index: {index}")

    def _get_view_for_section(self, index: int) -> ft.Control:
        """
        Obtiene la vista correspondiente al índice de sección.

        Args:
            index: Índice de la sección

        Returns:
            Control de Flet con la vista correspondiente

        Example:
            >>> view = self._get_view_for_section(1)  # Clientes
            >>> view = self._get_view_for_section(2)  # Proveedores
        """
        # Lazy import para evitar imports circulares
        from src.frontend.views.dashboard.dashboard_view import DashboardView
        from src.frontend.views.companies.company_list_view import CompanyListView
        from src.frontend.views.articles.article_list_view import ArticleListView
        from src.frontend.views.nomenclatures.nomenclature_list_view import NomenclatureListView

        match index:
            case 0:
                logger.debug("Creating DashboardView")
                return DashboardView()
            case 1:
                logger.debug("Creating CompanyListView (Clientes)")
                return CompanyListView(
                    default_type_filter="CLIENT",
                    on_view_detail=self.navigate_to_company_detail,
                    on_create=lambda ctype: self.navigate_to_company_form(None, ctype),
                    on_edit=self.navigate_to_company_form,
                )
            case 2:
                logger.debug("Creating CompanyListView (Proveedores)")
                return CompanyListView(
                    default_type_filter="SUPPLIER",
                    on_view_detail=self.navigate_to_company_detail,
                    on_create=lambda ctype: self.navigate_to_company_form(None, ctype),
                    on_edit=self.navigate_to_company_form,
                )
            case 3:
                logger.debug("Creating ArticleListView")
                return ArticleListView(
                    on_view_detail=self.navigate_to_article_detail,
                    on_create=self.navigate_to_article_form,
                    on_edit=self.navigate_to_article_form,
                )
            case 4:
                logger.debug("Creating NomenclatureListView")
                return NomenclatureListView(
                    on_view_detail=self.navigate_to_nomenclature_detail,
                    on_create=self.navigate_to_nomenclature_form,
                    on_edit=self.navigate_to_nomenclature_form,
                )
            case _:
                logger.warning(f"No view implemented for index: {index}")
                return self._create_placeholder_view(index)

    def _create_placeholder_view(self, index: int) -> ft.Control:
        """
        Crea una vista placeholder para secciones no implementadas.

        Args:
            index: Índice de la sección

        Returns:
            Control de Flet con mensaje placeholder
        """
        nav_item = get_navigation_item_by_index(index)
        title = nav_item["label"] if nav_item else f"Sección {index}"

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        name=ft.Icons.CONSTRUCTION,
                        size=LayoutConstants.ICON_SIZE_XL,
                    ),
                    ft.Text(
                        f"{title} - En Construcción",
                        size=LayoutConstants.FONT_SIZE_XL,
                        weight=LayoutConstants.FONT_WEIGHT_BOLD,
                    ),
                    ft.Text(
                        "Esta sección estará disponible próximamente.",
                        size=LayoutConstants.FONT_SIZE_MD,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=LayoutConstants.SPACING_MD,
            ),
            expand=True,
            alignment=ft.alignment.center,
        )

    def _update_breadcrumb(self) -> None:
        """Actualiza el breadcrumb con el estado actual de navegación."""
        if self._breadcrumb:
            breadcrumb_path = app_state.navigation.breadcrumb_path
            translated_path = [
                {
                    "label": t(item["label"]),
                    "route": item.get("route")
                }
                for item in breadcrumb_path
            ]
            self._breadcrumb.update_path(translated_path)
            logger.debug(f"Breadcrumb updated with {len(translated_path)} items: {[p['label'] for p in translated_path]}")

    def _on_breadcrumb_navigate(self, route: str) -> None:
        """
        Maneja la navegación cuando se hace clic en un item del breadcrumb.

        Args:
            route: Ruta a la que navegar

        Example:
            >>> _on_breadcrumb_navigate("/companies/clients")
        """
        logger.info(f"Breadcrumb navigation to: {route}")

        # Mapear rutas a índices de navegación
        route_mapping = {
            "/": 0,  # Dashboard
            "/companies/clients": 1,  # Clientes
            "/companies/suppliers": 2,  # Proveedores
            "/articles": 3,  # Artículos
            "/nomenclatures": 4,  # Nomenclaturas
            "/quotes": 5,  # Cotizaciones
            "/orders": 6,  # Órdenes
            "/deliveries": 7,  # Entregas
            "/invoices": 8,  # Facturas
            "/staff": 9,  # Personal
            "/settings": 10,  # Configuración
        }

        # Obtener el índice correspondiente a la ruta
        index = route_mapping.get(route)
        if index is not None:
            # Usar el método existente de navegación
            self._on_destination_change(index)
        else:
            logger.warning(f"Unknown route in breadcrumb: {route}")

    def _on_navigation_changed(self) -> None:
        """
        Observer: Se ejecuta cuando cambia el estado de navegación.

        Actualiza el breadcrumb y el navigation rail.
        """
        logger.debug("Navigation state changed, updating UI")

        # Actualizar breadcrumb
        self._update_breadcrumb()

        if self.page:
            self.update()

    def _on_i18n_changed(self) -> None:
        """
        Observer: Se ejecuta cuando cambia el idioma.

        Actualiza todos los textos de la interfaz.
        """
        logger.debug("Language changed, updating UI")

        # Actualizar breadcrumb con nuevas traducciones
        self._update_breadcrumb()

        if self.page:
            self.update()

    def _on_theme_changed(self) -> None:
        """
        Observer: Se ejecuta cuando cambia el tema.

        Actualiza los colores de la interfaz.
        """
        logger.debug("Theme changed, updating UI")

        if self.page:
            self.update()

    def _handle_theme_change(self, theme_mode: str) -> None:
        """
        Maneja el cambio de tema desde el AppBar.

        Args:
            theme_mode: Modo de tema ("light", "dark", "system")
        """
        logger.info(f"Theme change requested: {theme_mode}")
        app_state.theme.set_theme_mode(theme_mode)

        if self.on_theme_change:
            self.on_theme_change(theme_mode)

    def _handle_language_change(self, language: str) -> None:
        """
        Maneja el cambio de idioma desde el AppBar.

        Args:
            language: Código de idioma ("es", "en", "fr")
        """
        logger.info(f"Language change requested: {language}")
        app_state.i18n.set_language(language)

        if self.on_language_change:
            self.on_language_change(language)

    def navigate_to(self, index: int) -> None:
        """
        Navega programáticamente a una sección.

        Args:
            index: Índice de la sección de destino

        Example:
            >>> main_view.navigate_to(1)  # Navega a Companies
        """
        logger.info(f"Programmatic navigation to index: {index}")
        if self._navigation_rail:
            self._navigation_rail.set_selected_index(index)
        self._on_destination_change(index)

    def navigate_to_route(self, route: str) -> None:
        """
        Navega programáticamente a una ruta.

        Args:
            route: Ruta de destino (ej: "/companies")

        Example:
            >>> main_view.navigate_to_route("/companies")
        """
        from src.frontend.navigation_config import get_navigation_item_by_route

        nav_item = get_navigation_item_by_route(route)
        if nav_item:
            self.navigate_to(nav_item["index"])
        else:
            logger.warning(f"Route not found: {route}")

    def navigate_to_company_detail(
        self,
        company_id: int,
        company_type: str = "CLIENT",
    ) -> None:
        """
        Navega a la vista de detalle de una empresa.

        Args:
            company_id: ID de la empresa
            company_type: Tipo de empresa ("CLIENT" o "SUPPLIER")

        Example:
            >>> main_view.navigate_to_company_detail(123, "CLIENT")
        """
        from src.frontend.views.companies.company_detail_view import CompanyDetailView

        logger.info(f"Navigating to company detail: ID={company_id}, type={company_type}")

        # Crear vista de detalle
        detail_view = CompanyDetailView(
            company_id=company_id,
            on_edit=lambda cid: self.navigate_to_company_form(cid, company_type),
            on_delete=lambda cid: self._on_company_deleted(cid, company_type),
            on_back=lambda: self._on_back_to_company_list(company_type),
        )

        # Actualizar contenido y breadcrumb
        if self._content_area:
            self._content_area.content = detail_view
            if self.page:
                self.update()

        # Actualizar breadcrumb
        section_key = "clients" if company_type == "CLIENT" else "suppliers"
        app_state.navigation.set_breadcrumb([
            {"label": f"{section_key}.title", "route": f"/companies/{company_type.lower()}s"},
            {"label": f"{section_key}.detail", "route": None},
        ])

    def navigate_to_company_form(
        self,
        company_id: int | None = None,
        company_type: str = "CLIENT",
    ) -> None:
        """
        Navega a la vista de formulario de empresa (crear/editar).

        Args:
            company_id: ID de la empresa a editar (None para crear)
            company_type: Tipo de empresa ("CLIENT" o "SUPPLIER")

        Example:
            >>> main_view.navigate_to_company_form(None, "CLIENT")  # Crear cliente
            >>> main_view.navigate_to_company_form(123, "SUPPLIER")  # Editar proveedor
        """
        from src.frontend.views.companies.company_form_view import CompanyFormView

        logger.info(
            f"Navigating to company form: ID={company_id}, type={company_type}, "
            f"mode={'edit' if company_id else 'create'}"
        )

        # Crear vista de formulario
        form_view = CompanyFormView(
            company_id=company_id,
            default_type=company_type,
            on_save=lambda company: self._on_company_saved(company, company_type),
            on_cancel=lambda: self._on_back_to_company_list(company_type),
        )

        # Actualizar contenido y breadcrumb
        if self._content_area:
            self._content_area.content = form_view
            if self.page:
                self.update()

        # Actualizar breadcrumb
        section_key = "clients" if company_type == "CLIENT" else "suppliers"
        action_key = f"{section_key}.edit" if company_id else f"{section_key}.create"
        app_state.navigation.set_breadcrumb([
            {"label": f"{section_key}.title", "route": f"/companies/{company_type.lower()}s"},
            {"label": action_key, "route": None},
        ])

    def _on_company_saved(self, company: dict, company_type: str) -> None:
        """
        Callback cuando se guarda una empresa exitosamente.

        Args:
            company: Datos de la empresa guardada
            company_type: Tipo de empresa
        """
        logger.success(f"Company saved: {company.get('name')}")
        # Volver a la lista
        self._on_back_to_company_list(company_type)

    def _on_company_deleted(self, company_id: int, company_type: str) -> None:
        """
        Callback cuando se elimina una empresa.

        Args:
            company_id: ID de la empresa eliminada
            company_type: Tipo de empresa
        """
        logger.success(f"Company deleted: ID={company_id}")
        # Volver a la lista
        self._on_back_to_company_list(company_type)

    def _on_back_to_company_list(self, company_type: str) -> None:
        """
        Navega de vuelta a la lista de empresas.

        Args:
            company_type: Tipo de empresa ("CLIENT" o "SUPPLIER")
        """
        logger.info(f"Navigating back to company list: type={company_type}")
        # Navegar al índice correspondiente
        index = 1 if company_type == "CLIENT" else 2
        self.navigate_to(index)

    # =========================================================================
    # NAVEGACIÓN DE ARTÍCULOS
    # =========================================================================

    def navigate_to_article_detail(self, article_id: int) -> None:
        """
        Navega a la vista de detalle de un artículo.

        Args:
            article_id: ID del artículo a mostrar

        Example:
            >>> main_view.navigate_to_article_detail(123)
        """
        from src.frontend.views.articles.article_detail_view import ArticleDetailView

        logger.info(f"Navigating to article detail: ID={article_id}")

        # Crear vista de detalle
        detail_view = ArticleDetailView(
            article_id=article_id,
            on_edit=self.navigate_to_article_form,
            on_delete=self._on_article_deleted,
            on_back=self._on_back_to_article_list,
        )

        # Actualizar contenido y breadcrumb
        if self._content_area:
            self._content_area.content = detail_view
            if self.page:
                self.update()

        app_state.navigation.set_breadcrumb([
            {"label": "articles.title", "route": "/articles"},
            {"label": "articles.detail", "route": None},
        ])

    def navigate_to_article_form(self, article_id: int | None = None) -> None:
        """
        Navega a la vista de formulario de artículo.

        Args:
            article_id: ID del artículo a editar (None para crear nuevo)

        Example:
            >>> main_view.navigate_to_article_form(None)  # Crear nuevo
            >>> main_view.navigate_to_article_form(123)   # Editar existente
        """
        from src.frontend.views.articles.article_form_view import ArticleFormView

        logger.info(
            f"Navigating to article form: ID={article_id}, "
            f"mode={'edit' if article_id else 'create'}"
        )

        # Crear vista de formulario
        form_view = ArticleFormView(
            article_id=article_id,
            on_save=self._on_article_saved,
            on_cancel=self._on_back_to_article_list,
        )

        # Actualizar contenido y breadcrumb
        if self._content_area:
            self._content_area.content = form_view
            if self.page:
                self.update()

        action_key = "articles.edit" if article_id else "articles.create"
        app_state.navigation.set_breadcrumb([
            {"label": "articles.title", "route": "/articles"},
            {"label": action_key, "route": None},
        ])

    def _on_article_saved(self, article: dict) -> None:
        """
        Callback cuando se guarda un artículo exitosamente.

        Args:
            article: Datos del artículo guardado
        """
        logger.success(f"Article saved: {article.get('reference', article.get('code'))}")
        self._on_back_to_article_list()

    def _on_article_deleted(self, article_id: int) -> None:
        """
        Callback cuando se elimina un artículo.

        Args:
            article_id: ID del artículo eliminado
        """
        logger.success(f"Article deleted: ID={article_id}")
        self._on_back_to_article_list()

    def _on_back_to_article_list(self) -> None:
        """
        Navega de vuelta a la lista de artículos.
        """
        logger.info("Navigating back to article list")
        self.navigate_to(3)

    # =========================================================================
    # NAVEGACIÓN DE NOMENCLATURAS
    # =========================================================================

    def navigate_to_nomenclature_detail(self, nomenclature_id: int) -> None:
        """
        Navega a la vista de detalle de una nomenclatura.

        Args:
            nomenclature_id: ID de la nomenclatura a mostrar

        Example:
            >>> main_view.navigate_to_nomenclature_detail(123)
        """
        from src.frontend.views.nomenclatures.nomenclature_detail_view import NomenclatureDetailView

        logger.info(f"Navigating to nomenclature detail: ID={nomenclature_id}")

        # Crear vista de detalle
        detail_view = NomenclatureDetailView(
            nomenclature_id=nomenclature_id,
            on_edit=self.navigate_to_nomenclature_form,
            on_delete=self._on_nomenclature_deleted,
            on_back=self._on_back_to_nomenclature_list,
        )

        # Actualizar contenido y breadcrumb
        if self._content_area:
            self._content_area.content = detail_view
            if self.page:
                self.update()

        app_state.navigation.set_breadcrumb([
            {"label": "nomenclatures.title", "route": "/nomenclatures"},
            {"label": "nomenclatures.detail", "route": None},
        ])

    def navigate_to_nomenclature_form(self, nomenclature_id: int | None = None) -> None:
        """
        Navega a la vista de formulario de nomenclatura.

        Args:
            nomenclature_id: ID de la nomenclatura a editar (None para crear nueva)

        Example:
            >>> main_view.navigate_to_nomenclature_form(None)  # Crear nueva
            >>> main_view.navigate_to_nomenclature_form(123)   # Editar existente
        """
        from src.frontend.views.nomenclatures.nomenclature_form_view import NomenclatureFormView

        logger.info(
            f"Navigating to nomenclature form: ID={nomenclature_id}, "
            f"mode={'edit' if nomenclature_id else 'create'}"
        )

        # Crear vista de formulario
        form_view = NomenclatureFormView(
            nomenclature_id=nomenclature_id,
            on_save=self._on_nomenclature_saved,
            on_cancel=self._on_back_to_nomenclature_list,
        )

        # Actualizar contenido y breadcrumb
        if self._content_area:
            self._content_area.content = form_view
            if self.page:
                self.update()

        action_key = "nomenclatures.edit" if nomenclature_id else "nomenclatures.create"
        app_state.navigation.set_breadcrumb([
            {"label": "nomenclatures.title", "route": "/nomenclatures"},
            {"label": action_key, "route": None},
        ])

    def _on_nomenclature_saved(self, nomenclature: dict) -> None:
        """
        Callback cuando se guarda una nomenclatura exitosamente.

        Args:
            nomenclature: Datos de la nomenclatura guardada
        """
        logger.success(f"Nomenclature saved: {nomenclature.get('reference', nomenclature.get('code'))}")
        self._on_back_to_nomenclature_list()

    def _on_nomenclature_deleted(self, nomenclature_id: int) -> None:
        """
        Callback cuando se elimina una nomenclatura.

        Args:
            nomenclature_id: ID de la nomenclatura eliminada
        """
        logger.success(f"Nomenclature deleted: ID={nomenclature_id}")
        self._on_back_to_nomenclature_list()

    def _on_back_to_nomenclature_list(self) -> None:
        """
        Navega de vuelta a la lista de nomenclaturas.
        """
        logger.info("Navigating back to nomenclature list")
        self.navigate_to(4)
