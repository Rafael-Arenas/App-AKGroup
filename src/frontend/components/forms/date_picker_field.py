"""
Componente de campo de fecha con DatePicker.

Proporciona un campo de texto con selector de fecha integrado.
"""
from datetime import datetime
import flet as ft
from loguru import logger
import pendulum  # Para formateo de fechas (no para time provider)

from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t


class DatePickerField(ft.Container):
    """
    Campo de fecha con DatePicker popup.

    Args:
        label: Etiqueta del campo
        hint_text: Texto de ayuda
        required: Si True, el campo es obligatorio
        date_format: Formato de fecha (default: "YYYY-MM-DD")
        min_date: Fecha mínima permitida (datetime)
        max_date: Fecha máxima permitida (datetime)

    Example:
        >>> field = DatePickerField(
        ...     label="Fecha de nacimiento",
        ...     required=True,
        ...     date_format="DD/MM/YYYY"
        ... )
        >>> if field.validate():
        ...     date = field.get_date()
        ...     print(date)
    """

    def __init__(
        self,
        label: str,
        hint_text: str | None = None,
        required: bool = False,
        date_format: str = "YYYY-MM-DD",
        min_date: datetime | None = None,
        max_date: datetime | None = None,
    ):
        """Inicializa el date picker field."""
        super().__init__()
        self.label = label
        self.hint_text = hint_text or date_format
        self.required = required
        self.date_format = date_format
        self.min_date = min_date
        self.max_date = max_date
        self.error_message = ""
        self._text_field: ft.TextField | None = None
        self._error_text: ft.Text | None = None
        self._date_picker: ft.DatePicker | None = None
        self._selected_date: datetime | None = None
        logger.debug(f"DatePickerField initialized: label={label}, format={date_format}")

    def build(self) -> ft.Control:
        """
        Construye el componente de date picker.

        Returns:
            Control de Flet con el campo de fecha
        """
        self._text_field = ft.TextField(
            label=self.label,
            hint_text=self.hint_text,
            read_only=True,
            suffix_icon=ft.Icons.CALENDAR_TODAY,
            on_click=self._open_date_picker,
        )

        self._error_text = ft.Text(
            "",
            size=LayoutConstants.FONT_SIZE_SM,
            visible=False,
        )

        # Crear DatePicker - usar 1970 como mínimo para evitar errores de timezone en Windows
        first_date = self.min_date or datetime(1970, 1, 1, 12, 0)
        last_date = self.max_date or datetime(2100, 12, 31, 12, 0)

        self._date_picker = ft.DatePicker(
            value=None,
            first_date=first_date,
            last_date=last_date,
            on_change=self._on_date_selected,
            on_dismiss=self._on_date_picker_dismiss,
        )

        return ft.Column(
            controls=[
                self._text_field,
                self._error_text,
                self._date_picker,
            ],
            spacing=LayoutConstants.SPACING_XS,
        )

    def _open_date_picker(self, e: ft.ControlEvent) -> None:
        """
        Abre el date picker.

        Args:
            e: Evento de Flet
        """
        if self._date_picker and e.page:
            self._date_picker.pick_date()
            logger.debug("Date picker opened")

    def _on_date_selected(self, e: ft.ControlEvent) -> None:
        """
        Callback cuando se selecciona una fecha.

        Args:
            e: Evento de Flet
        """
        if self._date_picker and self._date_picker.value:
            self._selected_date = self._date_picker.value
            formatted_date = self._format_date(self._selected_date)
            if self._text_field:
                self._text_field.value = formatted_date
            self.clear_error()
            logger.info(f"Date selected: {formatted_date}")
            if self.page:
                self.update()

    def _on_date_picker_dismiss(self, e: ft.ControlEvent) -> None:
        """
        Callback cuando se cierra el date picker.

        Args:
            e: Evento de Flet
        """
        logger.debug("Date picker dismissed")

    def _format_date(self, date: datetime) -> str:
        """
        Formatea una fecha según el formato configurado.

        Args:
            date: Fecha a formatear

        Returns:
            Fecha formateada como string
        """
        pend_date = pendulum.instance(date)
        return pend_date.format(self.date_format)

    def _parse_date(self, date_str: str) -> datetime | None:
        """
        Parsea una fecha desde string.

        Args:
            date_str: String de fecha

        Returns:
            Datetime o None si no se puede parsear
        """
        try:
            pend_date = pendulum.from_format(date_str, self.date_format)
            return pend_date
        except Exception as e:
            logger.warning(f"Error parsing date '{date_str}': {e}")
            return None

    def validate(self) -> bool:
        """
        Valida el campo.

        Returns:
            True si válido, False si hay errores

        Example:
            >>> if field.validate():
            ...     print("Valid!")
        """
        if self.required and not self._selected_date:
            self.set_error(t("validation.required", {"field": self.label}))
            return False

        if self._selected_date:
            # Validar rango de fechas
            if self.min_date and self._selected_date < self.min_date:
                self.set_error(t("validation.date_too_early"))
                return False

            if self.max_date and self._selected_date > self.max_date:
                self.set_error(t("validation.date_too_late"))
                return False

        self.clear_error()
        return True

    def get_date(self) -> datetime | None:
        """
        Obtiene la fecha seleccionada.

        Returns:
            Datetime o None si no hay selección

        Example:
            >>> date = field.get_date()
        """
        return self._selected_date

    def get_date_string(self) -> str:
        """
        Obtiene la fecha como string formateado.

        Returns:
            String de fecha formateada (vacío si no hay selección)

        Example:
            >>> date_str = field.get_date_string()
        """
        if self._selected_date:
            return self._format_date(self._selected_date)
        return ""

    def set_date(self, date: datetime) -> None:
        """
        Establece la fecha seleccionada.

        Args:
            date: Fecha a establecer

        Example:
            >>> from datetime import datetime
            >>> field.set_date(datetime.now())
            >>> field.update()
        """
        self._selected_date = date
        if self._text_field:
            self._text_field.value = self._format_date(date)
        logger.debug(f"Date set to: {self._format_date(date)}")
        if self.page:
            self.update()

    def set_date_string(self, date_str: str) -> bool:
        """
        Establece la fecha desde un string.

        Args:
            date_str: String de fecha en el formato configurado

        Returns:
            True si se pudo parsear y establecer, False si no

        Example:
            >>> field.set_date_string("2024-01-15")
        """
        parsed_date = self._parse_date(date_str)
        if parsed_date:
            self.set_date(parsed_date)
            return True
        return False

    def set_error(self, message: str) -> None:
        """
        Establece un mensaje de error.

        Args:
            message: Mensaje de error a mostrar

        Example:
            >>> field.set_error("Fecha inválida")
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
            >>> field.clear_error()
        """
        self.error_message = ""
        if self._error_text:
            self._error_text.visible = False

        if self.page:
            self.update()

    def clear(self) -> None:
        """
        Limpia la selección de fecha.

        Example:
            >>> field.clear()
        """
        self._selected_date = None
        if self._text_field:
            self._text_field.value = ""
        self.clear_error()
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
