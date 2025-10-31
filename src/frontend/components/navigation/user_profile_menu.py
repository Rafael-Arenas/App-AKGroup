"""
UserProfileMenu - Menú desplegable de perfil de usuario.

Muestra el avatar del usuario y un menú con opciones
como perfil, configuración y cerrar sesión.
"""

import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.color_constants import ColorConstants
from src.frontend.i18n.translation_manager import t
from src.frontend.layout_constants import LayoutConstants


class UserProfileMenu(ft.PopupMenuButton):
    """
    Menú de perfil de usuario con avatar y opciones.

    Características:
    - Avatar circular (imagen o iniciales)
    - Menú desplegable con opciones
    - Acciones: Ver perfil, Configuración, Cerrar sesión
    """

    def __init__(
        self,
        user_name: str = "Usuario",
        user_role: str = "Administrador",
        avatar_url: str | None = None,
        on_profile_click: callable = None,
        on_settings_click: callable = None,
        on_logout: callable = None,
    ):
        """
        Inicializa el UserProfileMenu.

        Args:
            user_name: Nombre del usuario
            user_role: Rol del usuario
            avatar_url: URL del avatar (opcional)
            on_profile_click: Callback para "Ver Perfil"
            on_settings_click: Callback para "Configuración"
            on_logout: Callback para "Cerrar Sesión"

        Example:
            >>> menu = UserProfileMenu(
            ...     user_name="Juan Pérez",
            ...     user_role="Administrador"
            ... )
        """
        self.user_name = user_name
        self.user_role = user_role
        self.avatar_url = avatar_url
        self.on_profile_click_callback = on_profile_click
        self.on_settings_click_callback = on_settings_click
        self.on_logout_callback = on_logout

        # Suscribirse a cambios de idioma
        app_state.i18n.add_observer(self._on_language_change)

        # Inicializar PopupMenuButton
        super().__init__(
            content=self._build_avatar(),
            items=self._build_menu_items(),
            tooltip=f"{user_name} ({user_role})",
        )

    def _build_avatar(self) -> ft.Control:
        """
        Construye el avatar (imagen o iniciales).

        Returns:
            Control con el avatar
        """
        avatar_size = 36

        if self.avatar_url:
            # Avatar con imagen
            return ft.Container(
                content=ft.Image(
                    src=self.avatar_url,
                    width=avatar_size,
                    height=avatar_size,
                    fit=ft.ImageFit.COVER,
                ),
                width=avatar_size,
                height=avatar_size,
                border_radius=avatar_size // 2,
                clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            )
        else:
            # Avatar con iniciales
            initials = self._get_initials(self.user_name)
            is_dark = app_state.theme.is_dark_mode

            return ft.Container(
                content=ft.Text(
                    initials,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ColorConstants.APPBAR_ON_BACKGROUND,
                ),
                width=avatar_size,
                height=avatar_size,
                border_radius=avatar_size // 2,
                bgcolor=ColorConstants.PRIMARY,
                alignment=ft.alignment.center,
            )

    def _get_initials(self, name: str) -> str:
        """
        Obtiene las iniciales del nombre.

        Args:
            name: Nombre completo

        Returns:
            Iniciales (máximo 2 caracteres)

        Example:
            >>> self._get_initials("Juan Pérez")
            'JP'
        """
        parts = name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        elif len(parts) == 1 and len(parts[0]) > 0:
            return parts[0][0].upper()
        else:
            return "U"

    def _build_menu_items(self) -> list[ft.PopupMenuItem]:
        """
        Construye los items del menú.

        Returns:
            Lista de items del menú
        """
        items = []
        is_dark = app_state.theme.is_dark_mode
        secondary_color = ColorConstants.get_color_for_theme("ON_SURFACE_VARIANT", is_dark)

        # Header con nombre y rol
        items.append(
            ft.PopupMenuItem(
                content=ft.Column(
                    [
                        ft.Text(
                            self.user_name,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            self.user_role,
                            size=12,
                            color=secondary_color,
                        ),
                    ],
                    spacing=2,
                    tight=True,
                ),
                on_click=None,  # No clickeable
            )
        )

        # Divider
        items.append(ft.PopupMenuItem())

        # Ver Perfil
        items.append(
            ft.PopupMenuItem(
                icon=ft.Icons.PERSON_OUTLINE,
                text=t("navigation.profile"),
                on_click=self._on_profile_click,
            )
        )

        # Configuración
        items.append(
            ft.PopupMenuItem(
                icon=ft.Icons.SETTINGS_OUTLINED,
                text=t("navigation.settings"),
                on_click=self._on_settings_click,
            )
        )

        # Divider
        items.append(ft.PopupMenuItem())

        # Cerrar Sesión
        items.append(
            ft.PopupMenuItem(
                icon=ft.Icons.LOGOUT,
                text=t("navigation.logout"),
                on_click=self._on_logout,
            )
        )

        return items

    def _on_profile_click(self, e):
        """
        Handler para Ver Perfil.

        Args:
            e: Evento de Flet
        """
        logger.info("Ver Perfil clicked")
        if self.on_profile_click_callback:
            self.on_profile_click_callback(e)

    def _on_settings_click(self, e):
        """
        Handler para Configuración.

        Args:
            e: Evento de Flet
        """
        logger.info("Configuración clicked")
        if self.on_settings_click_callback:
            self.on_settings_click_callback(e)

    def _on_logout(self, e):
        """
        Handler para Cerrar Sesión.

        Args:
            e: Evento de Flet
        """
        logger.info("Cerrar Sesión clicked")
        if self.on_logout_callback:
            self.on_logout_callback(e)

    def _on_language_change(self):
        """Actualiza los textos del menú cuando cambia el idioma."""
        # Reconstruir items del menú con las nuevas traducciones
        self.items = self._build_menu_items()
        if self.page:
            self.update()

    def update_user(
        self,
        user_name: str | None = None,
        user_role: str | None = None,
        avatar_url: str | None = None,
    ) -> None:
        """
        Actualiza la información del usuario.

        Args:
            user_name: Nuevo nombre (opcional)
            user_role: Nuevo rol (opcional)
            avatar_url: Nueva URL de avatar (opcional)

        Example:
            >>> menu.update_user(user_name="María García")
        """
        if user_name is not None:
            self.user_name = user_name
        if user_role is not None:
            self.user_role = user_role
        if avatar_url is not None:
            self.avatar_url = avatar_url

        # Reconstruir componente
        self.content = self._build_avatar()
        self.items = self._build_menu_items()
        self.tooltip = f"{self.user_name} ({self.user_role})"
        if self.page:
            self.update()

        logger.debug(f"UserProfileMenu actualizado: {self.user_name}")


# Exportar
__all__ = ["UserProfileMenu"]
