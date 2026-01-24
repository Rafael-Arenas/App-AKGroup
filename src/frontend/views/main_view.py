"""
Vista principal de la aplicación.

Contenedor principal que integra AppBar, NavigationRail, Breadcrumb y área de contenido.
Usa navegadores especializados para delegar la lógica de navegación específica de cada módulo.
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

# Navegadores especializados
from src.frontend.navigation import (
    CompanyNavigator,
    ArticleNavigator,
    NomenclatureNavigator,
    QuoteNavigator,
    OrderNavigator,
)


class MainView(ft.Container):
    """
    Vista principal contenedora de la aplicación.

    Proporciona la estructura base con navegación, breadcrumb y área de contenido.
    Implementa observers para actualizaciones automáticas de navegación, idioma y tema.
    Delega la navegación específica de cada módulo a navegadores especializados.

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

        # Inicializar navegadores especializados
        self.company_navigator = CompanyNavigator(self)
        self.article_navigator = ArticleNavigator(self)
        self.nomenclature_navigator = NomenclatureNavigator(self)
        self.quote_navigator = QuoteNavigator(self)
        self.order_navigator = OrderNavigator(self)

        # Construir el contenido
        self.content = self._build()

        logger.info("MainView initialized with specialized navigators")

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

        # Layout principal (la vista inicial se carga en did_mount)
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

        # Cargar vista inicial (Dashboard)
        self._load_initial_view()

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
        from src.frontend.views.dashboard.dashboard_view import DashboardView
        from src.frontend.views.companies.company_list_view import CompanyListView
        from src.frontend.views.articles.article_list_view import ArticleListView
        from src.frontend.views.nomenclatures.nomenclature_list_view import NomenclatureListView
        from src.frontend.views.quotes.quote_list_view import QuoteListView
        from src.frontend.views.orders.order_list_view import OrderListView

        match index:
            case 0:
                logger.debug("Creating DashboardView")
                return DashboardView()
            case 1:
                logger.debug("Creating CompanyListView (Clientes)")
                return CompanyListView(
                    default_type_filter="CLIENT",
                    on_view_detail=self.navigate_to_company_dashboard,
                    on_create=lambda ctype: self.navigate_to_company_form(None, ctype),
                    on_edit=self.navigate_to_company_form,
                )
            case 2:
                logger.debug("Creating CompanyListView (Proveedores)")
                return CompanyListView(
                    default_type_filter="SUPPLIER",
                    on_view_detail=self.navigate_to_company_dashboard,
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
            case 5:
                logger.debug("Creating QuoteListView")
                return QuoteListView(
                    on_view_detail=lambda qid, cid, ctype: self.navigate_to_quote_detail(cid, ctype, qid, from_quote_list=True),
                    on_edit=lambda qid, cid, ctype: self.navigate_to_quote_form(cid, ctype, qid, from_quote_list=True),
                )
            case 6:
                logger.debug("Creating OrderListView")
                return OrderListView(
                    on_view_detail=lambda oid, cid, ctype: self.navigate_to_order_detail(cid, ctype, oid, from_order_list=True),
                    on_edit=lambda oid, cid, ctype: self.navigate_to_order_form(cid, ctype, None, oid, from_order_list=True),
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
                    ft.Icon(ft.Icons.CONSTRUCTION,
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
            alignment=ft.Alignment(0, 0),  # center
        )

    def _update_breadcrumb(self) -> None:
        """Actualiza el breadcrumb con el estado actual de navegación."""
        if self._breadcrumb:
            breadcrumb_path = app_state.navigation.breadcrumb_path
            translated_path: list[dict[str, str | None]] = []
            for item in breadcrumb_path:
                raw_label = item["label"]
                label = t(raw_label) if "." in raw_label else raw_label
                translated_path.append({"label": label, "route": item.get("route")})
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

        # Manejar rutas dinámicas
        if route.startswith("/companies/dashboard/"):
            try:
                # Formato esperado: /companies/dashboard/{id}/{type}[/action]
                parts = route.split("/")
                if len(parts) >= 5:
                    company_id = int(parts[3])
                    company_type = parts[4]
                    
                    # Check for specific actions
                    if len(parts) >= 6:
                        action = parts[5]
                        if action == "quotes":
                            self.company_navigator.navigate_to_quotes(company_id, company_type)
                            return
                        elif action == "orders":
                            self.company_navigator.navigate_to_orders(company_id, company_type)
                            return
                        elif action == "deliveries":
                            self.company_navigator.navigate_to_deliveries(company_id, company_type)
                            return
                        elif action == "invoices":
                            self.company_navigator.navigate_to_invoices(company_id, company_type)
                            return

                    # Default to dashboard
                    self.company_navigator.navigate_to_dashboard(company_id, company_type)
                    return
            except Exception as e:
                logger.error(f"Error parsing dashboard route {route}: {e}")
            return

        # Manejar rutas dinámicas de nomenclaturas
        if route.startswith("/nomenclatures/"):
            try:
                # Formato esperado: /nomenclatures/{id}/edit o /nomenclatures/{id}/articles
                parts = route.split("/")
                if len(parts) >= 4:
                    nomenclature_id = int(parts[2])
                    action = parts[3]
                    
                    if action == "edit":
                        self.nomenclature_navigator.navigate_to_form(nomenclature_id)
                        return
                    elif action == "articles":
                        self.nomenclature_navigator.navigate_to_articles(nomenclature_id)
                        return
                elif len(parts) >= 3 and parts[2].isdigit():
                    # /nomenclatures/{id} - ir al detalle
                    nomenclature_id = int(parts[2])
                    self.nomenclature_navigator.navigate_to_detail(nomenclature_id)
                    return
            except Exception as e:
                logger.error(f"Error parsing nomenclature route {route}: {e}")
            return

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

    # =========================================================================
    # MÉTODOS PÚBLICOS DE NAVEGACIÓN - Delegados a navegadores especializados
    # =========================================================================
    
    # COMPANIES
    def navigate_to_company_detail(self, company_id: int, company_type: str = "CLIENT", from_dashboard: bool = False) -> None:
        """Delega a company_navigator."""
        self.company_navigator.navigate_to_detail(company_id, company_type, from_dashboard)

    def navigate_to_company_form(self, company_id: int | None = None, company_type: str = "CLIENT") -> None:
        """Delega a company_navigator."""
        self.company_navigator.navigate_to_form(company_id, company_type)

    def navigate_to_company_dashboard(self, company_id: int, company_type: str = "CLIENT") -> None:
        """Delega a company_navigator."""
        self.company_navigator.navigate_to_dashboard(company_id, company_type)

    def navigate_to_company_quotes(self, company_id: int, company_type: str) -> None:
        """Delega a company_navigator."""
        self.company_navigator.navigate_to_quotes(company_id, company_type)

    def navigate_to_company_orders(self, company_id: int, company_type: str) -> None:
        """Delega a company_navigator."""
        self.company_navigator.navigate_to_orders(company_id, company_type)

    def navigate_to_company_deliveries(self, company_id: int, company_type: str) -> None:
        """Delega a company_navigator."""
        self.company_navigator.navigate_to_deliveries(company_id, company_type)

    def navigate_to_company_invoices(self, company_id: int, company_type: str) -> None:
        """Delega a company_navigator."""
        self.company_navigator.navigate_to_invoices(company_id, company_type)

    # ARTICLES
    def navigate_to_article_detail(self, article_id: int) -> None:
        """Delega a article_navigator."""
        self.article_navigator.navigate_to_detail(article_id)

    def navigate_to_article_form(self, article_id: int | None = None) -> None:
        """Delega a article_navigator."""
        self.article_navigator.navigate_to_form(article_id)

    # NOMENCLATURES
    def navigate_to_nomenclature_detail(self, nomenclature_id: int) -> None:
        """Delega a nomenclature_navigator."""
        self.nomenclature_navigator.navigate_to_detail(nomenclature_id)

    def navigate_to_nomenclature_form(self, nomenclature_id: int | None = None) -> None:
        """Delega a nomenclature_navigator."""
        self.nomenclature_navigator.navigate_to_form(nomenclature_id)

    def navigate_to_nomenclature_articles(self, nomenclature_id: int) -> None:
        """Delega a nomenclature_navigator."""
        self.nomenclature_navigator.navigate_to_articles(nomenclature_id)

    # QUOTES
    def navigate_to_quote_detail(self, company_id: int, company_type: str, quote_id: int, from_quote_list: bool = False) -> None:
        """Delega a quote_navigator."""
        self.quote_navigator.navigate_to_detail(company_id, company_type, quote_id, from_quote_list)

    def navigate_to_quote_form(self, company_id: int, company_type: str, quote_id: int | None = None, from_quote_list: bool = False) -> None:
        """Delega a quote_navigator."""
        self.quote_navigator.navigate_to_form(company_id, company_type, quote_id, from_quote_list)

    def navigate_to_quote_products(self, company_id: int, company_type: str, quote_id: int, from_quote_list: bool = False) -> None:
        """Delega a quote_navigator."""
        self.quote_navigator.navigate_to_products(company_id, company_type, quote_id, from_quote_list)

    # ORDERS
    def navigate_to_order_detail(self, company_id: int, company_type: str, order_id: int, from_order_list: bool = False) -> None:
        """Delega a order_navigator."""
        self.order_navigator.navigate_to_detail(company_id, company_type, order_id, from_order_list)

    def navigate_to_order_form(self, company_id: int, company_type: str, quote_id: int | None = None, order_id: int | None = None, from_order_list: bool = False) -> None:
        """Delega a order_navigator."""
        self.order_navigator.navigate_to_form(company_id, company_type, quote_id, order_id, from_order_list)
