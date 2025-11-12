"""
Componente de indicador de carga.

Proporciona un spinner circular con mensaje opcional y tamaños configurables.
"""
from typing import Literal
import flet as ft
from loguru import logger

from src.frontend.layout_constants import LayoutConstants


class LoadingSpinner(ft.Container):
    """
    Indicador de carga con ProgressRing y mensaje opcional.

    Args:
        message: Mensaje de texto opcional a mostrar
        size: Tamaño del spinner ("small", "medium", "large")
        color: Color del spinner (default: PRIMARY)

    Example:
        >>> spinner = LoadingSpinner(message="Cargando datos...", size="medium")
        >>> page.add(spinner)
    """

    def __init__(
        self,
        message: str | None = None,
        size: Literal["small", "medium", "large"] = "medium",
        color: str | None = None,
    ):
        """Inicializa el componente de loading spinner."""
        super().__init__()
        self.message = message
        self.size = size
        self.color = color
        self._size_map = {
            "small": 24,
            "medium": 40,
            "large": 64,
        }
        logger.debug(f"LoadingSpinner initialized with size={size}, message={message}")

    def build(self) -> ft.Control:
        """
        Construye el componente de loading spinner.

        Returns:
            Control de Flet con el spinner y mensaje opcional
        """
        spinner_size = self._size_map.get(self.size, 40)

        spinner_kwargs = {
            "width": spinner_size,
            "height": spinner_size,
            "stroke_width": 3 if self.size == "small" else 4,
        }
        if self.color:
            spinner_kwargs["color"] = self.color

        content = [ft.ProgressRing(**spinner_kwargs)]

        if self.message:
            content.append(
                ft.Text(
                    self.message,
                    size=LayoutConstants.FONT_SIZE_MD,
                    text_align=ft.TextAlign.CENTER,
                )
            )

        return ft.Container(
            content=ft.Column(
                controls=content,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=LayoutConstants.SPACING_MD,
            ),
            alignment=ft.alignment.center,
            expand=False,
        )

    def update_message(self, message: str) -> None:
        """
        Actualiza el mensaje del spinner.

        Args:
            message: Nuevo mensaje a mostrar

        Example:
            >>> spinner.update_message("Procesando...")
            >>> spinner.update()
        """
        logger.debug(f"Updating spinner message to: {message}")
        self.message = message
        if self.page:
            self.update()

    def update_size(self, size: Literal["small", "medium", "large"]) -> None:
        """
        Actualiza el tamaño del spinner.

        Args:
            size: Nuevo tamaño del spinner

        Example:
            >>> spinner.update_size("large")
            >>> spinner.update()
        """
        logger.debug(f"Updating spinner size to: {size}")
        self.size = size
        if self.page:
            self.update()
