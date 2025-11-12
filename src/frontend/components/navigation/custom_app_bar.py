"""
CustomAppBar - Barra superior personalizada de la aplicación.

Muestra logo, título de sección, selector de idioma, selector de tema,
notificaciones y perfil de usuario.
"""

import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t
from src.frontend.components.navigation.language_selector import LanguageSelector
from src.frontend.components.navigation.notification_badge import NotificationBadge
from src.frontend.components.navigation.user_profile_menu import UserProfileMenu


class CustomAppBar(ft.Container):
    """
    Barra superior personalizada de la aplicación.

    Características:
    - Logo de la aplicación (izquierda)
    - Título dinámico de sección (centro-izquierda)
    - Selector de idioma
    - Selector de tema (claro/oscuro/sistema)
    - Badge de notificaciones (derecha)
    - Menú de perfil de usuario (extrema derecha)
    """

    def __init__(
        self,
        section_title: str = "Inicio",
        notification_count: int = 0,
        has_urgent_notifications: bool = False,
        user_name: str = "Usuario",
        user_role: str = "Administrador",
        user_avatar: str | None = None,
        on_notifications_click: callable = None,
        on_profile_click: callable = None,
        on_settings_click: callable = None,
        on_logout: callable = None,
    ):
        """
        Inicializa el CustomAppBar.

        Args:
            section_title: Título de la sección actual
            notification_count: Número de notificaciones
            has_urgent_notifications: Si hay notificaciones urgentes
            user_name: Nombre del usuario
            user_role: Rol del usuario
            user_avatar: URL del avatar
            on_notifications_click: Callback para click en notificaciones
            on_profile_click: Callback para ver perfil
            on_settings_click: Callback para configuración
            on_logout: Callback para cerrar sesión

        Example:
            >>> app_bar = CustomAppBar(
            ...     section_title="Dashboard",
            ...     user_name="Juan Pérez"
            ... )
        """
        super().__init__()

        self.section_title_text = section_title
        self.on_notifications_click_callback = on_notifications_click

        # Configurar container
        self.height = LayoutConstants.APPBAR_HEIGHT
        self.padding = ft.padding.symmetric(
            horizontal=LayoutConstants.PADDING_LG
        )

        # Crear componentes
        self.logo = self._build_logo()
        self.title = self._build_title()
        self.language_selector = LanguageSelector()
        self.theme_selector = self._build_theme_selector()
        self.notification_badge = NotificationBadge(
            count=notification_count,
            has_urgent=has_urgent_notifications,
            on_click=self._on_notifications_click,
        )
        self.user_menu = UserProfileMenu(
            user_name=user_name,
            user_role=user_role,
            avatar_url=user_avatar,
            on_profile_click=on_profile_click,
            on_settings_click=on_settings_click,
            on_logout=on_logout,
        )

        # Layout
        self.content = ft.Row(
            [
                self.logo,
                ft.Container(width=LayoutConstants.SPACING_LG),
                self.title,
                ft.Container(expand=True),  # Spacer
                self.language_selector,
                ft.Container(width=LayoutConstants.SPACING_SM),
                self.theme_selector,
                ft.Container(width=LayoutConstants.SPACING_SM),
                self.notification_badge,
                ft.Container(width=LayoutConstants.SPACING_SM),
                self.user_menu,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )

        # Suscribirse a cambios de idioma para actualizar título
        app_state.i18n.add_observer(self._on_language_change)

        # Suscribirse a cambios de tema
        app_state.theme.add_observer(self._on_theme_change)

    def _build_logo(self) -> ft.Control:
        """
        Construye el logo de la aplicación.

        Returns:
            Control con el logo
        """
        # Logo de AK Group
        return ft.Container(
            content=ft.Icon(
                ft.Icons.BUSINESS_CENTER,
                size=LayoutConstants.ICON_SIZE_LG,
            ),
            width=LayoutConstants.ICON_SIZE_LG,
            height=LayoutConstants.ICON_SIZE_LG,
        )

    def _build_title(self) -> ft.Control:
        """
        Construye el título de la sección.

        Returns:
            Control con el título
        """
        return ft.Text(
            self.section_title_text,
            size=LayoutConstants.FONT_SIZE_XL,
            weight=ft.FontWeight.BOLD,
        )

    def _build_theme_selector(self) -> ft.PopupMenuButton:
        """
        Construye el selector de tema.

        Returns:
            PopupMenuButton con opciones de tema
        """
        current_theme = app_state.theme.theme_mode

        items = []

        # Tema Claro
        items.append(
            ft.PopupMenuItem(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.LIGHT_MODE, size=18),
                        ft.Container(width=8),
                        ft.Text(t("navigation.theme.light"), size=14),
                        ft.Container(expand=True),
                        ft.Icon(
                            ft.Icons.CHECK,
                            size=18,
                            visible=(current_theme == "light"),
                        ),
                    ],
                    spacing=0,
                ),
                on_click=lambda e: self._on_theme_select("light"),
            )
        )

        # Tema Oscuro
        items.append(
            ft.PopupMenuItem(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.DARK_MODE, size=18),
                        ft.Container(width=8),
                        ft.Text(t("navigation.theme.dark"), size=14),
                        ft.Container(expand=True),
                        ft.Icon(
                            ft.Icons.CHECK,
                            size=18,
                            visible=(current_theme == "dark"),
                        ),
                    ],
                    spacing=0,
                ),
                on_click=lambda e: self._on_theme_select("dark"),
            )
        )

        # Tema Sistema
        items.append(
            ft.PopupMenuItem(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.BRIGHTNESS_AUTO, size=18),
                        ft.Container(width=8),
                        ft.Text(t("navigation.theme.system"), size=14),
                        ft.Container(expand=True),
                        ft.Icon(
                            ft.Icons.CHECK,
                            size=18,
                            visible=(current_theme == "system"),
                        ),
                    ],
                    spacing=0,
                ),
                on_click=lambda e: self._on_theme_select("system"),
            )
        )

        return ft.PopupMenuButton(
            icon=ft.Icons.BRIGHTNESS_6,
            tooltip=t("navigation.theme.title"),
            items=items,
        )

    def _on_theme_select(self, theme_mode: str):
        """
        Maneja la selección de tema.

        Args:
            theme_mode: Modo de tema seleccionado
        """
        logger.info(f"Cambiando tema a: {theme_mode}")
        app_state.theme.set_theme_mode(theme_mode)

    def _on_notifications_click(self, e):
        """
        Handler para click en notificaciones.

        Args:
            e: Evento de Flet
        """
        logger.debug("Notifications clicked from AppBar")
        if self.on_notifications_click_callback:
            self.on_notifications_click_callback(e)

    def update_title(self, title: str) -> None:
        """
        Actualiza el título de la sección.

        Args:
            title: Nuevo título

        Example:
            >>> app_bar.update_title("Empresas")
        """
        self.section_title_text = title
        self.title.value = title
        if self.page:
            self.update()
        logger.debug(f"AppBar title actualizado: {title}")

    def update_notifications(
        self,
        count: int,
        has_urgent: bool = False
    ) -> None:
        """
        Actualiza el badge de notificaciones.

        Args:
            count: Número de notificaciones
            has_urgent: Si hay notificaciones urgentes

        Example:
            >>> app_bar.update_notifications(5, has_urgent=True)
        """
        self.notification_badge.update_count(count, has_urgent)
        logger.debug(
            f"AppBar notifications actualizadas: {count} "
            f"({'urgentes' if has_urgent else 'normales'})"
        )

    def update_user(
        self,
        user_name: str | None = None,
        user_role: str | None = None,
        avatar_url: str | None = None,
    ) -> None:
        """
        Actualiza la información del usuario.

        Args:
            user_name: Nuevo nombre
            user_role: Nuevo rol
            avatar_url: Nueva URL de avatar

        Example:
            >>> app_bar.update_user(user_name="María García")
        """
        self.user_menu.update_user(user_name, user_role, avatar_url)
        logger.debug("AppBar user info actualizada")

    def _on_language_change(self) -> None:
        """
        Actualiza el título cuando cambia el idioma.

        El título será actualizado por el MainView a través de update_title(),
        que se llama desde el observer de navegación.
        """
        # Reconstruir selector de tema con nuevas traducciones
        self.theme_selector = self._build_theme_selector()
        self._rebuild_content()

        if self.page:
            self.update()
        logger.debug("AppBar actualizado por cambio de idioma")

    def _on_theme_change(self) -> None:
        """Actualiza el AppBar cuando cambia el tema."""
        # Reconstruir logo y título
        self.logo = self._build_logo()
        self.title = self._build_title()
        self.theme_selector = self._build_theme_selector()
        self._rebuild_content()

        if self.page:
            self.update()
        logger.debug("AppBar actualizado por cambio de tema")

    def _rebuild_content(self) -> None:
        """Reconstruye el contenido del AppBar."""
        self.content = ft.Row(
            [
                self.logo,
                ft.Container(width=LayoutConstants.SPACING_LG),
                self.title,
                ft.Container(expand=True),  # Spacer
                self.language_selector,
                ft.Container(width=LayoutConstants.SPACING_SM),
                self.theme_selector,
                ft.Container(width=LayoutConstants.SPACING_SM),
                self.notification_badge,
                ft.Container(width=LayoutConstants.SPACING_SM),
                self.user_menu,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )


# Exportar
__all__ = ["CustomAppBar"]
