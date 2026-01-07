"""
Diálogo de formulario para crear/editar contactos.

Proporciona un formulario modal para agregar o editar contactos de empresas.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.forms import ValidatedTextField


class ContactFormDialog:
    """
    Diálogo para crear o editar un contacto.

    Args:
        company_id: ID de la empresa
        mode: "create" o "edit"
        contact_id: ID del contacto (solo para modo edit)
        initial_data: Datos iniciales del contacto (solo para modo edit)
        on_save: Callback cuando se guarda exitosamente
        on_cancel: Callback cuando se cancela

    Example:
        >>> def handle_save():
        ...     print("Contacto guardado")
        >>> dialog = ContactFormDialog(
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
        contact_id: int | None = None,
        initial_data: dict | None = None,
        on_save: Callable[[], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ):
        """Inicializa el diálogo de formulario de contacto."""
        self.company_id = company_id
        self.mode = mode
        self.contact_id = contact_id
        self.initial_data = initial_data or {}
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel

        # Estado
        self._is_loading = False
        self._error_message = ""
        self._dialog: ft.AlertDialog | None = None
        self._page: ft.Page | None = None

        # Referencias a los campos (se crearán en show())
        self._first_name_field = None
        self._last_name_field = None
        self._email_field = None
        self._phone_field = None
        self._mobile_field = None
        self._position_field = None
        self._error_banner = None
        self._cancel_button = None
        self._save_button = None

        logger.debug(f"ContactFormDialog initialized: mode={mode}, company_id={company_id}")

    def _load_initial_data(self) -> None:
        """Carga los datos iniciales en el formulario (modo edit)."""
        if not self.initial_data:
            return

        self._first_name_field.set_value(self.initial_data.get("first_name", ""))
        self._last_name_field.set_value(self.initial_data.get("last_name", ""))
        self._email_field.set_value(self.initial_data.get("email", ""))
        self._phone_field.set_value(self.initial_data.get("phone", ""))
        self._mobile_field.set_value(self.initial_data.get("mobile", ""))
        self._position_field.set_value(self.initial_data.get("position", ""))

        logger.debug(f"Initial data loaded: {self.initial_data.get('first_name')} {self.initial_data.get('last_name')}")

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
        self._save_button.content = ft.Text("Guardando..." if loading else "Guardar")
        self._cancel_button.disabled = loading
        if self._page:
            self._page.update()

    def _validate_form(self) -> bool:
        """Valida todos los campos del formulario."""
        is_valid = True

        # Validar campos requeridos
        if not self._first_name_field.validate():
            is_valid = False

        if not self._last_name_field.validate():
            is_valid = False

        # Validar email si tiene valor
        email_value = self._email_field.get_value()
        if email_value and not self._email_field.validate():
            is_valid = False

        # Validar teléfonos si tienen valor
        phone_value = self._phone_field.get_value()
        if phone_value and not self._phone_field.validate():
            is_valid = False

        mobile_value = self._mobile_field.get_value()
        if mobile_value and not self._mobile_field.validate():
            is_valid = False

        return is_valid

    def _on_cancel_click(self, e: ft.ControlEvent) -> None:
        """Maneja el click en cancelar."""
        logger.info("Contact form cancelled")
        self.close(e.page)
        if self.on_cancel_callback:
            self.on_cancel_callback()

    async def _on_save_click(self, e: ft.ControlEvent) -> None:
        """Maneja el click en guardar."""
        logger.info(f"Save contact clicked: mode={self.mode}")

        # Ocultar errores previos
        self._hide_error()

        # Validar formulario
        if not self._validate_form():
            self._show_error("Por favor complete los campos obligatorios correctamente")
            return

        # Mostrar loading
        self._set_loading(True)

        try:
            import httpx

            # Preparar datos
            data = {
                "first_name": self._first_name_field.get_value(),
                "last_name": self._last_name_field.get_value(),
                "email": self._email_field.get_value() or None,
                "phone": self._phone_field.get_value() or None,
                "mobile": self._mobile_field.get_value() or None,
                "position": self._position_field.get_value() or None,
                "company_id": self.company_id,
            }

            async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                if self.mode == "create":
                    # POST para crear
                    response = await client.post("/api/v1/contacts", json=data)
                else:
                    # PUT para editar
                    response = await client.put(
                        f"/api/v1/contacts/{self.contact_id}",
                        json={k: v for k, v in data.items() if k != "company_id"}
                    )

                if response.status_code in [200, 201]:
                    logger.success(f"Contact saved successfully: {self.mode}")

                    # Cerrar diálogo
                    self.close(e.page)

                    # Ejecutar callback
                    if self.on_save_callback:
                        self.on_save_callback()
                else:
                    error_detail = response.json().get("detail", "Error desconocido")
                    logger.error(f"Error saving contact: {response.status_code} - {error_detail}")
                    self._show_error(f"Error al guardar: {error_detail}")
                    self._set_loading(False)

        except Exception as e:
            logger.exception(f"Error saving contact: {e}")
            self._show_error(f"Error de conexión: {str(e)}")
            self._set_loading(False)

    def show(self, page: ft.Page) -> None:
        """
        Muestra el diálogo en la página.

        Args:
            page: Página de Flet donde mostrar el diálogo
        """
        logger.info(f"ContactFormDialog.show() called - mode={self.mode}")
        self._page = page
        title = "Agregar Contacto" if self.mode == "create" else "Editar Contacto"

        try:
            # Crear los campos del formulario AQUÍ (no en __init__)
            self._first_name_field = ValidatedTextField(
                label="Nombre *",
                hint_text="Nombre del contacto",
                required=True,
                validators=["required"],
                prefix_icon=ft.Icons.PERSON,
            )

            self._last_name_field = ValidatedTextField(
                label="Apellido *",
                hint_text="Apellido del contacto",
                required=True,
                validators=["required"],
                prefix_icon=ft.Icons.PERSON_OUTLINE,
            )

            self._email_field = ValidatedTextField(
                label="Email",
                hint_text="correo@ejemplo.com",
                validators=["email"],
                prefix_icon=ft.Icons.EMAIL,
            )

            self._phone_field = ValidatedTextField(
                label="Teléfono",
                hint_text="Ej: +56 2 1234 5678",
                max_length=20,
                prefix_icon=ft.Icons.PHONE,
            )

            self._mobile_field = ValidatedTextField(
                label="Móvil",
                hint_text="Ej: +56 9 8765 4321",
                max_length=20,
                prefix_icon=ft.Icons.SMARTPHONE,
            )

            self._position_field = ValidatedTextField(
                label="Cargo",
                hint_text="Ej: Gerente de Ventas",
                prefix_icon=ft.Icons.WORK,
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
            self._cancel_button = ft.TextButton(content=ft.Text("Cancelar"),
                on_click=self._on_cancel_click,
            )

            self._save_button = ft.Button(content=ft.Text("Guardar"),
                icon=ft.Icons.SAVE,
                on_click=self._on_save_click,
            )

            self._dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(title, size=LayoutConstants.FONT_SIZE_LG),
                content=ft.Column(
                    controls=[
                        self._error_banner,
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=self._first_name_field,
                                    expand=1,
                                ),
                                ft.Container(
                                    content=self._last_name_field,
                                    expand=1,
                                ),
                            ],
                            spacing=LayoutConstants.SPACING_MD,
                        ),
                        self._email_field,
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=self._phone_field,
                                    expand=1,
                                ),
                                ft.Container(
                                    content=self._mobile_field,
                                    expand=1,
                                ),
                            ],
                            spacing=LayoutConstants.SPACING_MD,
                        ),
                        self._position_field,
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
            logger.success("Contact dialog shown")
        except Exception as e:
            logger.exception(f"ERROR showing contact dialog: {e}")

    def close(self, page: ft.Page) -> None:
        """
        Cierra el diálogo.

        Args:
            page: Página de Flet
        """
        if self._dialog:
            self._dialog.open = False
            page.update()
            logger.debug("Contact dialog closed")
