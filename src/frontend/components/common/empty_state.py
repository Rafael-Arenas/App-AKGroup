"""
Componente de estado vacío.

Muestra un mensaje cuando no hay datos disponibles con opción de acción.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.layout_constants import LayoutConstants
from src.frontend.app_state import app_state


class EmptyState(ft.Container):
    """
    Estado vacío con ícono, título, mensaje y botón de acción opcional.

    Args:
        icon: Ícono a mostrar (de ft.Icons)
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
        self._icon = icon
        self._title = title
        self._message = message
        self._action_text = action_text
        self._on_action = on_action
        logger.debug(f"EmptyState initialized with title={title}")

        # Suscribirse a cambios de tema
        app_state.theme.add_observer(self._on_theme_changed)

        # Construir el contenido
        self._build_content()

    def _on_theme_changed(self) -> None:
        """Callback cuando cambia el tema."""
        self._build_content()
        if self.page:
            self.update()

    def _build_content(self) -> None:
        """
        Construye el componente de empty state.

        Establece las propiedades del Container directamente.
        """
        controls = [
            ft.Icon(self._icon,
                size=LayoutConstants.ICON_SIZE_XL * 2,
            ),
            ft.Text(
                self._title,
                size=LayoutConstants.FONT_SIZE_XXL,
                weight=LayoutConstants.FONT_WEIGHT_BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                self._message,
                size=LayoutConstants.FONT_SIZE_MD,
                text_align=ft.TextAlign.CENTER,
            ),
        ]

        if self._action_text and self._on_action:
            controls.append(
                ft.Button(content=ft.Text(self._action_text),
                    icon=ft.Icons.ADD,
                    on_click=self._handle_action,
                )
            )

        # Establecer las propiedades del Container directamente
        self.content = ft.Column(
            controls=controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=LayoutConstants.SPACING_LG,
        )
        self.alignment = ft.Alignment(0, 0)  # center
        self.padding = LayoutConstants.PADDING_XL
        self.expand = True

    def _handle_action(self, e: ft.ControlEvent) -> None:
        """
        Maneja el click en el botón de acción.

        Args:
            e: Evento de Flet
        """
        logger.info("Empty state action button clicked")
        if self._on_action:
            try:
                self._on_action()
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
            self._title = title
        if message is not None:
            self._message = message
        if action_text is not None:
            self._action_text = action_text

        # Reconstruir el contenido con los nuevos valores
        self._build_content()

        logger.debug(f"Updated empty state content: title={self._title}")
        if self.page:
            self.update()

    def will_unmount(self) -> None:
        """Limpieza cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_theme_changed)
