"""
Vista principal de la aplicación.

Contenedor principal que integra AppBar, NavigationRail, Breadcrumb y área de contenido.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.color_constants import ColorConstants
from src.frontend.layout_constants import LayoutConstants
from src.frontend.navigation_config import get_navigation_item_by_index
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

        # Crear Breadcrumb
        self._breadcrumb = Breadcrumb()

        # Crear área de contenido
        self._content_area = ft.Container(
            content=ft.Column(
                controls=[],
                expand=True,
            ),
            expand=True,
            bgcolor=ColorConstants.get_color_for_theme("BACKGROUND", is_dark),
            padding=LayoutConstants.PADDING_LG,
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
                                self._breadcrumb,
                                self._content_area,
                            ],
                            expand=True,
                            spacing=LayoutConstants.SPACING_SM,
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
            >>> view = self._get_view_for_section(1)  # CompanyListView
        """
        # Lazy import para evitar imports circulares
        from src.frontend.views.dashboard.dashboard_view import DashboardView
        from src.frontend.views.companies.company_list_view import CompanyListView
        from src.frontend.views.products.product_list_view import ProductListView

        match index:
            case 0:
                logger.debug("Creating DashboardView")
                return DashboardView()
            case 1:
                logger.debug("Creating CompanyListView")
                return CompanyListView()
            case 2:
                logger.debug("Creating ProductListView")
                return ProductListView()
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
                        color=ColorConstants.get_color_for_theme(
                            "ON_SURFACE_VARIANT",
                            app_state.theme.is_dark_mode,
                        ),
                    ),
                    ft.Text(
                        f"{title} - En Construcción",
                        size=LayoutConstants.FONT_SIZE_XL,
                        weight=LayoutConstants.FONT_WEIGHT_BOLD,
                        color=ColorConstants.get_color_for_theme(
                            "ON_SURFACE",
                            app_state.theme.is_dark_mode,
                        ),
                    ),
                    ft.Text(
                        "Esta sección estará disponible próximamente.",
                        size=LayoutConstants.FONT_SIZE_MD,
                        color=ColorConstants.get_color_for_theme(
                            "ON_SURFACE_VARIANT",
                            app_state.theme.is_dark_mode,
                        ),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=LayoutConstants.SPACING_MD,
            ),
            expand=True,
            alignment=ft.alignment.center,
        )

    def _on_navigation_changed(self) -> None:
        """
        Observer: Se ejecuta cuando cambia el estado de navegación.

        Actualiza el breadcrumb y el navigation rail.
        """
        logger.debug("Navigation state changed, updating UI")
        if self.page:
            self.update()

    def _on_i18n_changed(self) -> None:
        """
        Observer: Se ejecuta cuando cambia el idioma.

        Actualiza todos los textos de la interfaz.
        """
        logger.debug("Language changed, updating UI")
        if self.page:
            self.update()

    def _on_theme_changed(self) -> None:
        """
        Observer: Se ejecuta cuando cambia el tema.

        Actualiza los colores de la interfaz.
        """
        logger.debug("Theme changed, updating UI")
        if self._content_area:
            is_dark = app_state.theme.is_dark_mode
            self._content_area.bgcolor = ColorConstants.get_color_for_theme(
                "BACKGROUND",
                is_dark,
            )
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
