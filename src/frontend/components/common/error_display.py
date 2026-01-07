"""
Componente de visualización de errores.

Muestra mensajes de error con ícono y opción de reintentar.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t


class ErrorDisplay(ft.Container):
    """
    Display de errores con ícono, mensaje y botón de reintentar.

    Args:
        message: Mensaje de error a mostrar
        on_retry: Callback opcional para el botón "Reintentar"
        show_retry_button: Si True, muestra el botón de reintentar

    Example:
        >>> def handle_retry():
        ...     print("Retrying...")
        >>> error = ErrorDisplay(
        ...     message="Error al cargar datos",
        ...     on_retry=handle_retry
        ... )
        >>> page.add(error)
    """

    def __init__(
        self,
        message: str,
        on_retry: Callable[[], None] | None = None,
        show_retry_button: bool = True,
    ):
        """Inicializa el componente de error display."""
        super().__init__()
        self.message = message
        self.on_retry = on_retry
        self.show_retry_button = show_retry_button and on_retry is not None
        logger.debug(f"ErrorDisplay initialized with message={message}")

    def build(self) -> ft.Control:
        """
        Construye el componente de error display.

        Returns:
            Control de Flet con el mensaje de error
        """
        content = [
            ft.Icon(ft.Icons.ERROR_OUTLINE,
                size=LayoutConstants.ICON_SIZE_XL,
            ),
            ft.Text(
                self.message,
                size=LayoutConstants.FONT_SIZE_LG,
                text_align=ft.TextAlign.CENTER,
                weight=LayoutConstants.FONT_WEIGHT_MEDIUM,
            ),
        ]

        if self.show_retry_button:
            content.append(
                ft.Button(
                    content=ft.Text(t("common.retry")),
                    icon=ft.Icons.REFRESH,
                    on_click=self._handle_retry,
                )
            )

        return ft.Container(
            content=ft.Column(
                controls=content,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=LayoutConstants.SPACING_MD,
            ),
            alignment=ft.Alignment(0, 0),  # center
            padding=LayoutConstants.PADDING_LG,
        )

    def _handle_retry(self, e: ft.ControlEvent) -> None:
        """
        Maneja el click en el botón de reintentar.

        Args:
            e: Evento de Flet
        """
        logger.info("Retry button clicked")
        if self.on_retry:
            try:
                self.on_retry()
            except Exception as ex:
                logger.error(f"Error in retry callback: {ex}")

    def update_error(self, message: str) -> None:
        """
        Actualiza el mensaje de error.

        Args:
            message: Nuevo mensaje de error

        Example:
            >>> error.update_error("Nuevo error ocurrido")
            >>> error.update()
        """
        logger.debug(f"Updating error message to: {message}")
        self.message = message
        if self.page:
            self.update()

    def set_retry_callback(self, callback: Callable[[], None]) -> None:
        """
        Establece el callback de reintentar.

        Args:
            callback: Función a llamar cuando se hace click en reintentar

        Example:
            >>> error.set_retry_callback(my_retry_function)
            >>> error.update()
        """
        logger.debug("Setting retry callback")
        self.on_retry = callback
        self.show_retry_button = callback is not None
        if self.page:
            self.update()
