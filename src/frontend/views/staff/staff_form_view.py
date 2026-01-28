"""
Vista de formulario de personal (Staff).

Formulario para crear y editar usuarios del sistema.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import (
    LoadingSpinner,
    ErrorDisplay,
)
from src.frontend.components.forms import ValidatedTextField
from src.frontend.i18n.translation_manager import t


class StaffFormView(ft.Column):
    """
    Vista de formulario para crear/editar personal.

    Args:
        staff_id: ID del personal a editar (None para crear)
        on_save: Callback cuando se guarda exitosamente
        on_cancel: Callback para cancelar
    """

    def __init__(
        self,
        staff_id: int | None = None,
        on_save: Callable[[int], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ):
        """Inicializa el formulario de personal."""
        super().__init__()
        self.staff_id = staff_id
        self.on_save = on_save
        self.on_cancel = on_cancel

        # Estado
        self._is_loading: bool = staff_id is not None
        self._is_saving: bool = False
        self._error_message: str = ""
        self._staff: dict | None = None
        self._is_edit_mode: bool = staff_id is not None

        # Configurar propiedades del Column
        self.expand = True
        self.spacing = LayoutConstants.SPACING_MD
        self.scroll = ft.ScrollMode.AUTO

        # Construir componentes y layout
        self._build_components()
        self.controls = self.build()

        logger.info(f"StaffFormView initialized: staff_id={staff_id}, edit_mode={self._is_edit_mode}")

    def _build_components(self) -> None:
        """Inicializa los componentes del formulario."""
        # Título y Botones (se actualizarán en build)
        self._fake_data_button = ft.IconButton(
            icon=ft.Icons.CASINO,
            tooltip=t("orders.form.generate_fake_data"),
            on_click=self._on_generate_fake_data,
            visible=not self._is_edit_mode,
        )

        # Campos del formulario
        self._username_field = ValidatedTextField(
            label=t("staff.fields.username"),
            hint_text="ejemplo: jperez",
            prefix_icon=ft.Icons.PERSON,
            max_length=50,
            read_only=self._is_edit_mode,
            required=not self._is_edit_mode,
            validators=["required"] if not self._is_edit_mode else [],
        )

        self._email_field = ValidatedTextField(
            label=t("staff.fields.email"),
            hint_text="ejemplo@akgroup.com",
            prefix_icon=ft.Icons.EMAIL,
            validators=["required", "email"],
            required=True,
            max_length=100,
        )

        self._first_name_field = ValidatedTextField(
            label=t("staff.fields.first_name"),
            hint_text="Juan",
            prefix_icon=ft.Icons.BADGE,
            validators=["required"],
            required=True,
            max_length=50,
        )

        self._last_name_field = ValidatedTextField(
            label=t("staff.fields.last_name"),
            hint_text="Pérez",
            prefix_icon=ft.Icons.BADGE,
            validators=["required"],
            required=True,
            max_length=50,
        )

        self._trigram_field = ValidatedTextField(
            label=t("staff.fields.trigram"),
            hint_text="JPE",
            prefix_icon=ft.Icons.SHORT_TEXT,
            max_length=3,
            validators=["max_length"],
        )

        self._phone_field = ValidatedTextField(
            label=t("staff.fields.phone"),
            hint_text="+56912345678",
            prefix_icon=ft.Icons.PHONE,
            validators=["phone"],
            max_length=20,
        )

        self._position_field = ValidatedTextField(
            label=t("staff.fields.position"),
            hint_text="Gerente de Ventas",
            prefix_icon=ft.Icons.WORK,
            max_length=100,
        )

        self._is_active_checkbox = ft.Checkbox(
            label=t("staff.fields.is_active"),
            value=True,
        )

        self._is_admin_checkbox = ft.Checkbox(
            label=t("staff.fields.is_admin"),
            value=False,
        )

    def build(self) -> list[ft.Control]:
        """
        Construye el layout del formulario.

        Returns:
            Lista de controles de Flet
        """
        if self._is_loading:
            return [
                ft.Container(
                    content=LoadingSpinner(message=t("staff.messages.loading")),
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                )
            ]

        if self._error_message and not self._staff and self._is_edit_mode:
            return [
                ft.Container(
                    content=ErrorDisplay(
                        message=self._error_message,
                        on_retry=self.load_staff,
                    ),
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                )
            ]

        # Título
        title = t("staff.edit_title") if self._is_edit_mode else t("staff.create_title")

        # Error message container
        error_container = ft.Container(
            content=ft.Text(
                self._error_message,
                color=ft.Colors.RED,
                size=LayoutConstants.FONT_SIZE_SM,
            ),
            visible=bool(self._error_message),
            padding=ft.padding.only(bottom=LayoutConstants.PADDING_SM),
        )

        return [
            # Header
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            tooltip=t("common.back"),
                            on_click=self._on_cancel_click,
                        ),
                        ft.Text(
                            title,
                            size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                            weight=LayoutConstants.FONT_WEIGHT_BOLD,
                            expand=True,
                        ),
                        self._fake_data_button,
                    ],
                    spacing=LayoutConstants.SPACING_SM,
                ),
            ),
            ft.Divider(),
            ft.Container(
                content=ft.Column(
                    controls=[
                        error_container,
                        # Sección de credenciales
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        t("staff.sections.credentials"),
                                        size=LayoutConstants.FONT_SIZE_LG,
                                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Container(content=self._username_field, expand=True),
                                            ft.Container(content=self._email_field, expand=True),
                                        ],
                                        spacing=LayoutConstants.SPACING_MD,
                                    ),
                                ],
                                spacing=LayoutConstants.SPACING_SM,
                            ),
                            padding=ft.padding.only(bottom=LayoutConstants.PADDING_MD),
                        ),
                        # Sección de información personal
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        t("staff.sections.personal_info"),
                                        size=LayoutConstants.FONT_SIZE_LG,
                                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Container(content=self._first_name_field, expand=True),
                                            ft.Container(content=self._last_name_field, expand=True),
                                            ft.Container(content=self._trigram_field, width=120),
                                        ],
                                        spacing=LayoutConstants.SPACING_MD,
                                    ),
                                ],
                                spacing=LayoutConstants.SPACING_SM,
                            ),
                            padding=ft.padding.only(bottom=LayoutConstants.PADDING_MD),
                        ),
                        # Sección de contacto
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        t("staff.sections.contact_info"),
                                        size=LayoutConstants.FONT_SIZE_LG,
                                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Container(content=self._phone_field, expand=True),
                                            ft.Container(content=self._position_field, expand=True),
                                        ],
                                        spacing=LayoutConstants.SPACING_MD,
                                    ),
                                ],
                                spacing=LayoutConstants.SPACING_SM,
                            ),
                            padding=ft.padding.only(bottom=LayoutConstants.PADDING_MD),
                        ),
                        # Sección de permisos
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        t("staff.sections.permissions"),
                                        size=LayoutConstants.FONT_SIZE_LG,
                                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                                    ),
                                    ft.Row(
                                        controls=[
                                            self._is_active_checkbox,
                                            self._is_admin_checkbox,
                                        ],
                                        spacing=LayoutConstants.SPACING_LG,
                                    ),
                                ],
                                spacing=LayoutConstants.SPACING_SM,
                            ),
                            padding=ft.padding.only(bottom=LayoutConstants.PADDING_LG),
                        ),
                        # Botones de acción
                        ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    content=ft.Text(t("common.save")),
                                    icon=ft.Icons.SAVE,
                                    on_click=self._on_save_click,
                                    disabled=self._is_saving,
                                ),
                                ft.ElevatedButton(
                                    content=ft.Text(t("common.cancel")),
                                    icon=ft.Icons.CANCEL,
                                    on_click=self._on_cancel_click,
                                    disabled=self._is_saving,
                                ),
                                ft.ProgressRing(
                                    visible=self._is_saving,
                                    width=20,
                                    height=20,
                                    stroke_width=2,
                                ),
                            ],
                            spacing=LayoutConstants.SPACING_MD,
                        ),
                    ],
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=LayoutConstants.PADDING_LG,
                expand=True,
            ),
        ]

    def did_mount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.info(f"StaffFormView mounted, edit_mode={self._is_edit_mode}")

        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)

        if self._is_edit_mode and self.page:
            self.page.run_task(self.load_staff)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        logger.info("StaffFormView unmounting")
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_staff(self) -> None:
        """Carga los datos del personal para edición."""
        if not self.staff_id:
            return

        logger.info(f"Loading staff data for ID={self.staff_id}")

        self._is_loading = True
        self._error_message = ""

        self.controls = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import StaffAPI

            staff_api = StaffAPI()
            self._staff = await staff_api.get_by_id(self.staff_id)

            logger.success(f"Staff loaded: {self._staff.get('username')}")

            self._is_loading = False
            self._populate_form()

        except Exception as e:
            logger.exception(f"Error loading staff: {e}")
            self._error_message = t("staff.messages.error_loading").replace("{error}", str(e))
            self._is_loading = False

        self.controls = self.build()
        if self.page:
            self.update()

    def _populate_form(self) -> None:
        """Pobla el formulario con los datos cargados."""
        if not self._staff:
            return

        self._username_field.set_value(self._staff.get("username", ""))
        self._email_field.set_value(self._staff.get("email", ""))
        self._first_name_field.set_value(self._staff.get("first_name", ""))
        self._last_name_field.set_value(self._staff.get("last_name", ""))
        self._trigram_field.set_value(self._staff.get("trigram", ""))
        self._phone_field.set_value(self._staff.get("phone", ""))
        self._position_field.set_value(self._staff.get("position", ""))
        self._is_active_checkbox.value = self._staff.get("is_active", True)
        self._is_admin_checkbox.value = self._staff.get("is_admin", False)

    def _on_save_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace clic en guardar."""
        logger.info("Save button clicked")

        if self.page:
            self.page.run_task(self._save_staff)

    async def _save_staff(self) -> None:
        """Guarda los datos del personal."""
        # Validar campos requeridos
        errors = self._validate_form()
        if errors:
            self._error_message = errors[0]
            self.controls = self.build()
            if self.page:
                self.update()
            return

        self._is_saving = True
        self._error_message = ""
        self.controls = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import StaffAPI

            staff_api = StaffAPI()

            # Preparar datos
            data = {
                "email": self._email_field.get_value().strip(),
                "first_name": self._first_name_field.get_value().strip(),
                "last_name": self._last_name_field.get_value().strip(),
                "trigram": self._trigram_field.get_value().strip().upper() if self._trigram_field.get_value().strip() else None,
                "phone": self._phone_field.get_value().strip() if self._phone_field.get_value().strip() else None,
                "position": self._position_field.get_value().strip() if self._position_field.get_value().strip() else None,
                "is_active": self._is_active_checkbox.value,
                "is_admin": self._is_admin_checkbox.value,
            }

            if self._is_edit_mode:
                # Actualizar
                result = await staff_api.update(self.staff_id, data)
                staff_id = self.staff_id
                logger.success(f"Staff updated: ID={staff_id}")
            else:
                # Crear
                data["username"] = self._username_field.get_value().strip().lower()
                result = await staff_api.create(data)
                staff_id = result.get("id")
                logger.success(f"Staff created: ID={staff_id}")

            self._is_saving = False

            if self.on_save:
                self.on_save(staff_id)

        except Exception as e:
            logger.exception(f"Error saving staff: {e}")
            self._error_message = t("staff.messages.error_saving").replace("{error}", str(e))
            self._is_saving = False

            self.controls = self.build()
            if self.page:
                self.update()

    def _validate_form(self) -> list[str]:
        """
        Valida los campos del formulario.

        Returns:
            Lista de errores (vacía si todo es válido)
        """
        errors = []
        is_valid = True

        if not self._is_edit_mode:
            if not self._username_field.validate():
                is_valid = False

        if not self._email_field.validate():
            is_valid = False

        if not self._first_name_field.validate():
            is_valid = False

        if not self._last_name_field.validate():
            is_valid = False
            
        # Validar longitud exacta de trigrama si se ingresó
        trigram_val = self._trigram_field.get_value()
        if trigram_val and len(trigram_val) != 3:
            self._trigram_field.set_error(t("staff.validation.trigram_length"))
            is_valid = False
        elif not self._trigram_field.validate():
            is_valid = False

        if not self._phone_field.validate():
            is_valid = False
            
        if not self._position_field.validate():
            is_valid = False

        if not is_valid:
            errors.append(t("validation.check_errors"))

        return errors

    def _on_cancel_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace clic en cancelar."""
        logger.info("Cancel button clicked")
        if self.on_cancel:
            self.on_cancel()

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado de tema o idioma."""
        logger.debug("StaffFormView state changed, rebuilding content")
        self._build_components() # Rebuild components to refresh translations
        self.controls = self.build()
        if self.page:
            self.update()

    def _on_generate_fake_data(self, e: ft.ControlEvent) -> None:
        """Genera datos ficticios para el formulario."""
        if self._is_edit_mode:
            return

        logger.info("Generating fake staff data")

        try:
            from src.frontend.utils.fake_data_generator import FakeDataGenerator

            FakeDataGenerator.populate_staff_form(self)

            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(t("staff.messages.fake_data_success")),
                    bgcolor=ft.Colors.GREEN,
                    duration=2000,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.update() # Update the view to show new data
                self.page.update()

        except Exception as ex:
            logger.exception(f"Error generating fake staff data: {ex}")
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(t("staff.messages.fake_data_error").replace("{error}", str(ex))),
                    bgcolor=ft.Colors.RED,
                    duration=3000,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.update()
                self.page.update()



