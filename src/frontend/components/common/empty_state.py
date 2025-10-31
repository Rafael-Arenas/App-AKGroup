"""
Componente de estado vacío.

Muestra un mensaje cuando no hay datos disponibles con opción de acción.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.color_constants import ColorConstants
from src.frontend.layout_constants import LayoutConstants
from src.frontend.app_state import app_state


class EmptyState(ft.Container):
    """
    Estado vacío con ícono, título, mensaje y botón de acción opcional.

    Args:
        icon: Ícono a mostrar (de ft.icons)
        title: Título del estado vacío
        message: Mensaje descriptivo
        action_text: Texto del botón de acción (opcional)
        on_action: Callback para el botón de acción (opcional)

    Example:
        >>> def create_first():
        ...     print("Creating first item...")
        >>> empty = EmptyState(
        ...     icon=ft.Icons.INBOX,
        ...     title="No hay datos",
        ...     message="Comienza creando tu primer elemento",
        ...     action_text="Crear Primero",
        ...     on_action=create_first
        ... )
        >>> page.add(empty)
    """

    def __init__(
        self,
        icon: str,
        title: str,
        message: str,
        action_text: str | None = None,
        on_action: Callable[[], None] | None = None,
    ):
        """Inicializa el componente de empty state."""
        super().__init__()
        self.icon = icon
        self.title = title
        self.message = message
        self.action_text = action_text
        self.on_action = on_action
        logger.debug(f"EmptyState initialized with title={title}")

        # Suscribirse a cambios de tema
        app_state.theme.add_observer(self._on_theme_changed)

    def _on_theme_changed(self) -> None:
        """Callback cuando cambia el tema."""
        if self.page:
            self.update()

    def build(self) -> ft.Control:
        """
        Construye el componente de empty state.

        Returns:
            Control de Flet con el estado vacío
        """
        is_dark = app_state.theme.is_dark_mode

        content = [
            ft.Icon(
                name=self.icon,
                size=LayoutConstants.ICON_SIZE_XL * 2,
                color=ColorConstants.get_color_for_theme("ON_SURFACE_VARIANT", is_dark),
            ),
            ft.Text(
                self.title,
                size=LayoutConstants.FONT_SIZE_XXL,
                weight=LayoutConstants.FONT_WEIGHT_BOLD,
                color=ColorConstants.get_color_for_theme("ON_SURFACE", is_dark),
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                self.message,
                size=LayoutConstants.FONT_SIZE_MD,
                color=ColorConstants.get_color_for_theme("ON_SURFACE_VARIANT", is_dark),
                text_align=ft.TextAlign.CENTER,
            ),
        ]

        if self.action_text and self.on_action:
            content.append(
                ft.ElevatedButton(
                    text=self.action_text,
                    icon=ft.Icons.ADD,
                    on_click=self._handle_action,
                    bgcolor=ColorConstants.PRIMARY,
                    color=ft.colors.WHITE,
                )
            )

        return ft.Container(
            content=ft.Column(
                controls=content,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=LayoutConstants.SPACING_LG,
            ),
            alignment=ft.alignment.center,
            padding=LayoutConstants.PADDING_XL,
            expand=True,
        )

    def _handle_action(self, e: ft.ControlEvent) -> None:
        """
        Maneja el click en el botón de acción.

        Args:
            e: Evento de Flet
        """
        logger.info("Empty state action button clicked")
        if self.on_action:
            try:
                self.on_action()
            except Exception as ex:
                logger.error(f"Error in action callback: {ex}")

    def update_content(
        self,
        title: str | None = None,
        message: str | None = None,
        action_text: str | None = None,
    ) -> None:
        """
        Actualiza el contenido del empty state.

        Args:
            title: Nuevo título (opcional)
            message: Nuevo mensaje (opcional)
            action_text: Nuevo texto de acción (opcional)

        Example:
            >>> empty.update_content(title="Nuevo título", message="Nuevo mensaje")
            >>> empty.update()
        """
        if title is not None:
            self.title = title
        if message is not None:
            self.message = message
        if action_text is not None:
            self.action_text = action_text

        logger.debug(f"Updated empty state content: title={self.title}")
        if self.page:
            self.update()

    def will_unmount(self) -> None:
        """Limpieza cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_theme_changed)
