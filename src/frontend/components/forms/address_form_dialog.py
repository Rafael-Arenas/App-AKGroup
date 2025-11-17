"""
Diálogo de formulario para crear/editar direcciones.

Proporciona un formulario modal para agregar o editar direcciones de empresas.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.forms import ValidatedTextField, DropdownField
from src.shared.enums import AddressType


class AddressFormDialog:
    """
    Diálogo para crear o editar una dirección.

    Args:
        company_id: ID de la empresa
        mode: "create" o "edit"
        address_id: ID de la dirección (solo para modo edit)
        initial_data: Datos iniciales de la dirección (solo para modo edit)
        on_save: Callback cuando se guarda exitosamente
        on_cancel: Callback cuando se cancela

    Example:
        >>> def handle_save():
        ...     print("Dirección guardada")
        >>> dialog = AddressFormDialog(
        ...     company_id=1,
        ...     mode="create",
        ...     on_save=handle_save,
        ... )
        >>> dialog.show(page)
    """

    def __init__(
        self,
        company_id: int,
        mode: str = "create",
        address_id: int | None = None,
        initial_data: dict | None = None,
        on_save: Callable[[], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ):
        """Inicializa el diálogo de formulario de dirección."""
        self.company_id = company_id
        self.mode = mode
        self.address_id = address_id
        self.initial_data = initial_data or {}
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel

        # Estado
        self._is_loading = False
        self._error_message = ""
        self._dialog: ft.AlertDialog | None = None
        self._page: ft.Page | None = None

        # Referencias a los campos (se crearán en show())
        self._address_field = None
        self._city_field = None
        self._postal_code_field = None
        self._country_field = None
        self._type_dropdown = None
        self._is_default_checkbox = None
        self._error_banner = None
        self._cancel_button = None
        self._save_button = None

        logger.debug(f"AddressFormDialog initialized: mode={mode}, company_id={company_id}")

    def _load_initial_data(self) -> None:
        """Carga los datos iniciales en el formulario (modo edit)."""
        if not self.initial_data:
            return

        self._address_field.set_value(self.initial_data.get("address", ""))
        self._city_field.set_value(self.initial_data.get("city", ""))
        self._postal_code_field.set_value(self.initial_data.get("postal_code", ""))
        self._country_field.set_value(self.initial_data.get("country", ""))
        self._type_dropdown.set_value(self.initial_data.get("address_type", "delivery"))
        self._is_default_checkbox.value = self.initial_data.get("is_default", False)

        logger.debug(f"Initial data loaded: {self.initial_data.get('address')}")

    def _show_error(self, message: str) -> None:
        """Muestra un mensaje de error en el banner."""
        self._error_message = message
        error_text = self._error_banner.content.controls[1]
        error_text.value = message
        self._error_banner.visible = True
        if self._page:
            self._page.update()

    def _hide_error(self) -> None:
        """Oculta el banner de error."""
        self._error_message = ""
        self._error_banner.visible = False
        if self._page:
            self._page.update()

    def _set_loading(self, loading: bool) -> None:
        """Establece el estado de loading."""
        self._is_loading = loading
        self._save_button.disabled = loading
        self._save_button.text = "Guardando..." if loading else "Guardar"
        self._cancel_button.disabled = loading
        if self._page:
            self._page.update()

    def _validate_form(self) -> bool:
        """Valida todos los campos del formulario."""
        is_valid = True

        # Validar campos requeridos
        if not self._address_field.validate():
            is_valid = False

        if not self._type_dropdown.validate():
            is_valid = False

        return is_valid

    def _on_cancel_click(self, e: ft.ControlEvent) -> None:
        """Maneja el click en cancelar."""
        logger.info("Address form cancelled")
        self.close(e.page)
        if self.on_cancel_callback:
            self.on_cancel_callback()

    async def _on_save_click(self, e: ft.ControlEvent) -> None:
        """Maneja el click en guardar."""
        logger.info(f"Save address clicked: mode={self.mode}")

        # Ocultar errores previos
        self._hide_error()

        # Validar formulario
        if not self._validate_form():
            self._show_error("Por favor complete los campos obligatorios")
            return

        # Mostrar loading
        self._set_loading(True)

        try:
            import httpx

            # Preparar datos
            data = {
                "address": self._address_field.get_value(),
                "city": self._city_field.get_value() or None,
                "postal_code": self._postal_code_field.get_value() or None,
                "country": self._country_field.get_value() or None,
                "is_default": self._is_default_checkbox.value,
                "address_type": self._type_dropdown.get_value(),
                "company_id": self.company_id,
            }

            async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                if self.mode == "create":
                    # POST para crear
                    response = await client.post("/api/v1/addresses", json=data)
                else:
                    # PUT para editar
                    response = await client.put(
                        f"/api/v1/addresses/{self.address_id}",
                        json={k: v for k, v in data.items() if k != "company_id"}
                    )

                if response.status_code in [200, 201]:
                    logger.success(f"Address saved successfully: {self.mode}")

                    # Cerrar diálogo
                    self.close(e.page)

                    # Ejecutar callback
                    if self.on_save_callback:
                        self.on_save_callback()
                else:
                    error_detail = response.json().get("detail", "Error desconocido")
                    logger.error(f"Error saving address: {response.status_code} - {error_detail}")
                    self._show_error(f"Error al guardar: {error_detail}")
                    self._set_loading(False)

        except Exception as e:
            logger.exception(f"Error saving address: {e}")
            self._show_error(f"Error de conexión: {str(e)}")
            self._set_loading(False)

    def show(self, page: ft.Page) -> None:
        """
        Muestra el diálogo en la página.

        Args:
            page: Página de Flet donde mostrar el diálogo
        """
        logger.info(f"AddressFormDialog.show() called - mode={self.mode}")
        self._page = page
        title = "Agregar Dirección" if self.mode == "create" else "Editar Dirección"

        try:
            # Crear los campos del formulario AQUÍ (no en __init__)
            self._address_field = ValidatedTextField(
                label="Dirección *",
                hint_text="Calle, número, detalles...",
                required=True,
                min_length=5,
                validators=["required"],
                multiline=True,
                prefix_icon=ft.Icons.HOME,
            )

            self._city_field = ValidatedTextField(
                label="Ciudad",
                hint_text="Nombre de la ciudad",
                prefix_icon=ft.Icons.LOCATION_CITY,
            )

            self._postal_code_field = ValidatedTextField(
                label="Código Postal",
                hint_text="Ej: 7500000",
                max_length=20,
            )

            self._country_field = ValidatedTextField(
                label="País",
                hint_text="Nombre del país",
                prefix_icon=ft.Icons.PUBLIC,
            )

            self._type_dropdown = DropdownField(
                label="Tipo de Dirección *",
                hint_text="Seleccione el tipo",
                options=[
                    {"value": "delivery", "text": "Entrega"},
                    {"value": "billing", "text": "Facturación"},
                    {"value": "headquarters", "text": "Sede Principal"},
                    {"value": "branch", "text": "Sucursal"},
                ],
                required=True,
                prefix_icon=ft.Icons.CATEGORY,
            )

            self._is_default_checkbox = ft.Checkbox(
                label="Dirección principal",
                value=False,
            )

            # Rellenar con datos iniciales si es modo edit
            if self.mode == "edit" and self.initial_data:
                self._load_initial_data()

            # Error banner
            self._error_banner = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.ERROR, color=ft.Colors.WHITE),
                        ft.Text("", color=ft.Colors.WHITE, expand=True),
                    ],
                    spacing=LayoutConstants.SPACING_SM,
                ),
                bgcolor=ft.Colors.RED_400,
                padding=LayoutConstants.PADDING_MD,
                border_radius=LayoutConstants.RADIUS_SM,
                visible=False,
            )

            # Botones
            self._cancel_button = ft.TextButton(
                text="Cancelar",
                on_click=self._on_cancel_click,
            )

            self._save_button = ft.ElevatedButton(
                text="Guardar",
                icon=ft.Icons.SAVE,
                on_click=self._on_save_click,
            )

            self._dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(title, size=LayoutConstants.FONT_SIZE_LG),
                content=ft.Column(
                    controls=[
                        self._error_banner,
                        self._address_field,
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=self._city_field,
                                    expand=2,
                                ),
                                ft.Container(
                                    content=self._postal_code_field,
                                    expand=1,
                                ),
                            ],
                            spacing=LayoutConstants.SPACING_MD,
                        ),
                        self._country_field,
                        self._type_dropdown,
                        self._is_default_checkbox,
                    ],
                    spacing=LayoutConstants.SPACING_MD,
                    scroll=ft.ScrollMode.AUTO,
                    tight=True,
                ),
                actions=[
                    self._cancel_button,
                    self._save_button,
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            logger.info("AlertDialog created successfully")

            # Usar el mismo patrón que ConfirmDialog (que funciona)
            page.dialog = self._dialog
            self._dialog.open = True
            page.update()
            logger.success("Address dialog shown")
        except Exception as e:
            logger.exception(f"ERROR showing address dialog: {e}")

    def close(self, page: ft.Page) -> None:
        """
        Cierra el diálogo.

        Args:
            page: Página de Flet
        """
        if self._dialog:
            self._dialog.open = False
            page.update()
            logger.debug("Address dialog closed")
