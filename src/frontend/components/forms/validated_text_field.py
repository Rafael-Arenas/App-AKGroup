"""
Componente de TextField con validación.

Proporciona un campo de texto con validadores integrados y custom.
"""
from typing import Callable
import re
import flet as ft
from loguru import logger

from src.frontend.color_constants import ColorConstants
from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t


class ValidatedTextField(ft.Container):
    """
    TextField con validación integrada.

    Args:
        label: Etiqueta del campo
        hint_text: Texto de ayuda (placeholder)
        required: Si True, el campo es obligatorio
        validators: Lista de nombres de validadores ("email", "phone", "url", "min_length", "max_length")
        custom_validator: Función de validación custom que retorna None si válido o mensaje de error
        min_length: Longitud mínima (para validator min_length)
        max_length: Longitud máxima (para validator max_length)
        password: Si True, muestra el campo como contraseña
        multiline: Si True, permite múltiples líneas
        prefix_icon: Ícono prefijo (opcional)
        suffix_icon: Ícono sufijo (opcional)

    Example:
        >>> def custom_validation(value: str) -> str | None:
        ...     if "test" in value.lower():
        ...         return "No puede contener 'test'"
        ...     return None
        >>> field = ValidatedTextField(
        ...     label="Email",
        ...     validators=["required", "email"],
        ...     prefix_icon=ft.Icons.EMAIL
        ... )
        >>> if field.validate():
        ...     print(field.get_value())
    """

    def __init__(
        self,
        label: str,
        hint_text: str | None = None,
        required: bool = False,
        validators: list[str] | None = None,
        custom_validator: Callable[[str], str | None] | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        password: bool = False,
        multiline: bool = False,
        prefix_icon: str | None = None,
        suffix_icon: str | None = None,
    ):
        """Inicializa el campo de texto validado."""
        super().__init__()
        self.label = label
        self.hint_text = hint_text
        self.required = required
        self.validators = validators or []
        self.custom_validator = custom_validator
        self.min_length = min_length
        self.max_length = max_length
        self.password = password
        self.multiline = multiline
        self.prefix_icon = prefix_icon
        self.suffix_icon = suffix_icon
        self.error_message = ""
        self._text_field: ft.TextField | None = None
        self._error_text: ft.Text | None = None
        logger.debug(f"ValidatedTextField initialized: label={label}, validators={validators}")

    def build(self) -> ft.Control:
        """
        Construye el componente de text field.

        Returns:
            Control de Flet con el campo de texto
        """
        self._text_field = ft.TextField(
            label=self.label,
            hint_text=self.hint_text,
            password=self.password,
            can_reveal_password=self.password,
            multiline=self.multiline,
            min_lines=3 if self.multiline else 1,
            max_lines=5 if self.multiline else 1,
            prefix_icon=self.prefix_icon,
            suffix_icon=self.suffix_icon,
            border_color=ColorConstants.BORDER_LIGHT,
            focused_border_color=ColorConstants.PRIMARY,
            on_change=self._on_change,
        )

        self._error_text = ft.Text(
            "",
            size=LayoutConstants.FONT_SIZE_SM,
            color=ColorConstants.ERROR,
            visible=False,
        )

        return ft.Column(
            controls=[
                self._text_field,
                self._error_text,
            ],
            spacing=LayoutConstants.SPACING_XS,
        )

    def _on_change(self, e: ft.ControlEvent) -> None:
        """
        Callback cuando cambia el valor del campo.

        Args:
            e: Evento de Flet
        """
        # Limpiar error al escribir
        if self.error_message:
            self.clear_error()

    def validate(self) -> bool:
        """
        Valida el campo según los validadores configurados.

        Returns:
            True si válido, False si hay errores

        Example:
            >>> if field.validate():
            ...     print("Valid!")
        """
        value = self.get_value()

        # Validar requerido
        if self.required and not value.strip():
            self.set_error(t("validation.required", {"field": self.label}))
            return False

        # Si está vacío y no es requerido, es válido
        if not value.strip() and not self.required:
            self.clear_error()
            return True

        # Aplicar validadores
        for validator in self.validators:
            error_msg = self._apply_validator(validator, value)
            if error_msg:
                self.set_error(error_msg)
                return False

        # Aplicar validador custom
        if self.custom_validator:
            error_msg = self.custom_validator(value)
            if error_msg:
                self.set_error(error_msg)
                return False

        self.clear_error()
        return True

    def _apply_validator(self, validator: str, value: str) -> str | None:
        """
        Aplica un validador específico.

        Args:
            validator: Nombre del validador
            value: Valor a validar

        Returns:
            Mensaje de error o None si válido
        """
        if validator == "email":
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, value):
                return t("validation.email_invalid")

        elif validator == "phone":
            pattern = r'^\+?[\d\s\-\(\)]{10,}$'
            if not re.match(pattern, value):
                return t("validation.phone_invalid")

        elif validator == "url":
            pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            if not re.match(pattern, value):
                return t("validation.url_invalid")

        elif validator == "min_length":
            if self.min_length and len(value) < self.min_length:
                return t("validation.min_length", {"min": str(self.min_length)})

        elif validator == "max_length":
            if self.max_length and len(value) > self.max_length:
                return t("validation.max_length", {"max": str(self.max_length)})

        return None

    def get_value(self) -> str:
        """
        Obtiene el valor actual del campo.

        Returns:
            Valor del campo como string

        Example:
            >>> value = field.get_value()
        """
        if self._text_field:
            return self._text_field.value or ""
        return ""

    def set_value(self, value: str) -> None:
        """
        Establece el valor del campo.

        Args:
            value: Nuevo valor

        Example:
            >>> field.set_value("nuevo valor")
            >>> field.update()
        """
        if self._text_field:
            self._text_field.value = value
            if self.page:
                self.update()

    def set_error(self, message: str) -> None:
        """
        Establece un mensaje de error.

        Args:
            message: Mensaje de error a mostrar

        Example:
            >>> field.set_error("Este campo es inválido")
        """
        self.error_message = message
        if self._error_text:
            self._error_text.value = message
            self._error_text.visible = True
        if self._text_field:
            self._text_field.border_color = ColorConstants.ERROR
            self._text_field.focused_border_color = ColorConstants.ERROR

        logger.debug(f"Validation error set: {message}")
        if self.page:
            self.update()

    def clear_error(self) -> None:
        """
        Limpia el mensaje de error.

        Example:
            >>> field.clear_error()
        """
        self.error_message = ""
        if self._error_text:
            self._error_text.visible = False
        if self._text_field:
            self._text_field.border_color = ColorConstants.BORDER_LIGHT
            self._text_field.focused_border_color = ColorConstants.PRIMARY

        if self.page:
            self.update()

    def set_enabled(self, enabled: bool) -> None:
        """
        Habilita o deshabilita el campo.

        Args:
            enabled: True para habilitar, False para deshabilitar

        Example:
            >>> field.set_enabled(False)
        """
        if self._text_field:
            self._text_field.disabled = not enabled
            if self.page:
                self.update()
