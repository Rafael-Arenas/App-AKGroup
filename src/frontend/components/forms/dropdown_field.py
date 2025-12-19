"""
Componente de Dropdown con validación.

Proporciona un campo de selección con validación.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t


class DropdownField(ft.Container):
    """
    Dropdown con validación integrada.

    Args:
        label: Etiqueta del campo
        hint_text: Texto de ayuda
        options: Lista de diccionarios con {"value": ..., "text": ...}
        required: Si True, el campo es obligatorio
        prefix_icon: Ícono prefijo (opcional)

    Example:
        >>> options = [
        ...     {"value": "1", "text": "Opción 1"},
        ...     {"value": "2", "text": "Opción 2"},
        ... ]
        >>> dropdown = DropdownField(
        ...     label="Seleccionar",
        ...     options=options,
        ...     required=True
        ... )
        >>> if dropdown.validate():
        ...     print(dropdown.get_value())
    """

    def __init__(
        self,
        label: str,
        hint_text: str | None = None,
        options: list[dict[str, str]] | None = None,
        required: bool = False,
        prefix_icon: str | None = None,
        on_change: Callable[[str], None] | None = None,
    ):
        """Inicializa el dropdown field."""
        super().__init__()
        self.label = label
        self.hint_text = hint_text
        self.options = options or []
        self.required = required
        self.prefix_icon = prefix_icon
        self.on_change_callback = on_change
        self.error_message = ""

        # Asegurar que el control ocupe todo el ancho disponible
        self.expand = True

        # Inicializar controles internos inmediatamente
        dropdown_options = [
            ft.dropdown.Option(
                key=opt["value"],
                text=opt.get("text", opt.get("label", ""))
            )
            for opt in self.options
        ]

        self._dropdown = ft.Dropdown(
            label=self.label,
            hint_text=self.hint_text,
            options=dropdown_options,
            prefix_icon=self.prefix_icon,
            on_change=self._on_change,
            expand=True,
        )

        self._error_text = ft.Text(
            "",
            size=LayoutConstants.FONT_SIZE_SM,
            visible=False,
        )

        # Establecer content del Container
        self.content = ft.Column(
            controls=[
                self._dropdown,
                self._error_text,
            ],
            spacing=LayoutConstants.SPACING_XS,
            expand=True,
        )

        logger.debug(f"DropdownField initialized: label={label}, options={len(self.options)}")

    def _on_change(self, e: ft.ControlEvent) -> None:
        """
        Callback cuando cambia el valor del dropdown.

        Args:
            e: Evento de Flet
        """
        # Limpiar error al seleccionar
        if self.error_message:
            self.clear_error()

        # Llamar al callback personalizado si existe
        if self.on_change_callback:
            value = self.get_value()
            self.on_change_callback(value)

    def validate(self) -> bool:
        """
        Valida el campo.

        Returns:
            True si válido, False si hay errores

        Example:
            >>> if dropdown.validate():
            ...     print("Valid!")
        """
        value = self.get_value()

        if self.required and not value:
            self.set_error(t("validation.required", {"field": self.label}))
            return False

        self.clear_error()
        return True

    def get_value(self) -> str:
        """
        Obtiene el valor seleccionado.

        Returns:
            Valor seleccionado como string (vacío si no hay selección)

        Example:
            >>> value = dropdown.get_value()
        """
        if self._dropdown:
            return self._dropdown.value or ""
        return ""

    def get_selected_text(self) -> str:
        """
        Obtiene el texto de la opción seleccionada.

        Returns:
            Texto de la opción seleccionada

        Example:
            >>> text = dropdown.get_selected_text()
        """
        value = self.get_value()
        for opt in self.options:
            if opt["value"] == value:
                return opt.get("text", opt.get("label", ""))
        return ""

    def set_value(self, value: str) -> None:
        """
        Establece el valor seleccionado.

        Args:
            value: Valor a seleccionar

        Example:
            >>> dropdown.set_value("1")
            >>> dropdown.update()
        """
        if self._dropdown:
            self._dropdown.value = value
            if self.page:
                self.update()

    def set_options(self, options: list[dict[str, str]]) -> None:
        """
        Actualiza las opciones del dropdown.

        Args:
            options: Nueva lista de opciones

        Example:
            >>> new_options = [{"value": "3", "text": "Opción 3"}]
            >>> dropdown.set_options(new_options)
            >>> dropdown.update()
        """
        self.options = options
        if self._dropdown:
            self._dropdown.options = [
                ft.dropdown.Option(
                    key=opt["value"],
                    text=opt.get("text", opt.get("label", ""))
                )
                for opt in options
            ]
            if self.page:
                self.update()

    def set_error(self, message: str) -> None:
        """
        Establece un mensaje de error.

        Args:
            message: Mensaje de error a mostrar

        Example:
            >>> dropdown.set_error("Debe seleccionar una opción")
        """
        self.error_message = message
        if self._error_text:
            self._error_text.value = message
            self._error_text.visible = True

        logger.debug(f"Validation error set: {message}")
        if self.page:
            self.update()

    def clear_error(self) -> None:
        """
        Limpia el mensaje de error.

        Example:
            >>> dropdown.clear_error()
        """
        self.error_message = ""
        if self._error_text:
            self._error_text.visible = False

        if self.page:
            self.update()

    def set_enabled(self, enabled: bool) -> None:
        """
        Habilita o deshabilita el campo.

        Args:
            enabled: True para habilitar, False para deshabilitar

        Example:
            >>> dropdown.set_enabled(False)
        """
        if self._dropdown:
            self._dropdown.disabled = not enabled
            if self.page:
                self.update()

    def clear(self) -> None:
        """
        Limpia la selección.

        Example:
            >>> dropdown.clear()
        """
        if self._dropdown:
            self._dropdown.value = None
            self.clear_error()
            if self.page:
                self.update()
