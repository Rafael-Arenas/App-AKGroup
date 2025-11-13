"""
Vista de formulario para crear/editar empresas.

Permite crear nuevas empresas o editar existentes con validación completa.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import BaseCard, LoadingSpinner, ErrorDisplay
from src.frontend.components.forms import ValidatedTextField, DropdownField


class CompanyFormView(ft.Container):
    """
    Vista de formulario para crear/editar empresas.

    Args:
        company_id: ID de la empresa a editar (None para crear nueva)
        on_save: Callback cuando se guarda exitosamente
        on_cancel: Callback cuando se cancela

    Example:
        >>> form = CompanyFormView(
        ...     company_id=123,
        ...     on_save=handle_save,
        ...     on_cancel=handle_cancel,
        ... )
        >>> page.add(form)
    """

    def __init__(
        self,
        company_id: int | None = None,
        default_type: str = "CLIENT",
        on_save: Callable[[dict], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ):
        """
        Inicializa el formulario de empresa.

        Args:
            company_id: ID de la empresa a editar (None para crear)
            default_type: Tipo por defecto ("CLIENT" o "SUPPLIER")
            on_save: Callback cuando se guarda
            on_cancel: Callback cuando se cancela
        """
        super().__init__()
        self.company_id = company_id
        self.default_type = default_type
        self.on_save = on_save
        self.on_cancel = on_cancel

        # Estado
        self._is_loading: bool = True
        self._is_saving: bool = False
        self._error_message: str = ""
        self._company_data: dict | None = None

        # Lookups
        self._company_types: list[dict] = []
        self._countries: list[dict] = []

        # Campos del formulario
        self._name_field: ValidatedTextField | None = None
        self._trigram_field: ValidatedTextField | None = None
        self._company_type_field: DropdownField | None = None
        self._phone_field: ValidatedTextField | None = None
        self._email_field: ValidatedTextField | None = None
        self._website_field: ValidatedTextField | None = None
        self._country_field: DropdownField | None = None
        self._is_active_switch: ft.Switch | None = None

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = 0

        # Construir contenido inicial
        self.content = self.build()

        logger.info(
            f"CompanyFormView initialized: "
            f"company_id={company_id}, default_type={default_type}, "
            f"mode={'edit' if company_id else 'create'}"
        )

    def build(self) -> ft.Control:
        """
        Construye el componente del formulario.

        Returns:
            Control de Flet con el formulario completo
        """
        # Estados de carga/error
        if self._is_loading:
            return ft.Container(
                content=LoadingSpinner(message="Cargando formulario..."),
                expand=True,
                alignment=ft.alignment.center,
            )

        if self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self._load_form_data,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )

        # Formulario principal
        is_edit = self.company_id is not None

        # Título
        title = ft.Text(
            "Editar Empresa" if is_edit else "Crear Empresa",
            size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
            weight=LayoutConstants.FONT_WEIGHT_BOLD,
        )

        # Campos del formulario
        self._name_field = ValidatedTextField(
            label="Nombre *",
            hint_text="Nombre completo de la empresa",
            required=True,
            prefix_icon=ft.Icons.BUSINESS,
        )

        self._trigram_field = ValidatedTextField(
            label="Trigrama *",
            hint_text="Código de 3 letras",
            required=True,
            max_length=3,
            validators=["max_length"],
            prefix_icon=ft.Icons.TAG,
        )

        self._company_type_field = DropdownField(
            label="Tipo de Empresa *",
            options=[],  # Se cargarán dinámicamente
            required=True,
        )

        self._phone_field = ValidatedTextField(
            label="Teléfono",
            hint_text="+123456789",
            validators=["phone"],
            prefix_icon=ft.Icons.PHONE,
        )

        self._email_field = ValidatedTextField(
            label="Email",
            hint_text="contacto@empresa.com",
            validators=["email"],
            prefix_icon=ft.Icons.EMAIL,
        )

        self._website_field = ValidatedTextField(
            label="Sitio Web",
            hint_text="https://www.empresa.com",
            validators=["url"],
            prefix_icon=ft.Icons.LANGUAGE,
        )

        self._country_field = DropdownField(
            label="País",
            options=[],  # Se cargarán dinámicamente
        )

        self._is_active_switch = ft.Switch(
            label="Empresa Activa",
            value=True,
        )

        # Sección: Información Básica
        basic_info_section = BaseCard(
            title="Información Básica",
            icon=ft.Icons.INFO_OUTLINED,
            content=ft.Column(
                controls=[
                    self._name_field,
                    self._trigram_field,
                    self._company_type_field,
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Sección: Información de Contacto
        contact_info_section = BaseCard(
            title="Información de Contacto",
            icon=ft.Icons.CONTACT_MAIL_OUTLINED,
            content=ft.Column(
                controls=[
                    self._phone_field,
                    self._email_field,
                    self._website_field,
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Sección: Ubicación
        location_section = BaseCard(
            title="Ubicación",
            icon=ft.Icons.LOCATION_ON_OUTLINED,
            content=ft.Column(
                controls=[
                    self._country_field,
                    self._is_active_switch,
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Botones de acción
        self._save_button = ft.ElevatedButton(
            text="Guardar",
            icon=ft.Icons.SAVE,
            on_click=self._on_save_click,
            disabled=self._is_saving,
        )

        self._cancel_button = ft.TextButton(
            text="Cancelar",
            on_click=self._on_cancel_click,
            disabled=self._is_saving,
        )

        action_buttons = ft.Row(
            controls=[self._save_button, self._cancel_button],
            spacing=LayoutConstants.SPACING_SM,
            alignment=ft.MainAxisAlignment.END,
        )

        # Contenido principal del formulario
        return ft.Container(
            content=ft.Column(
                controls=[
                    title,
                    basic_info_section,
                    contact_info_section,
                    location_section,
                    action_buttons,
                ],
                spacing=LayoutConstants.SPACING_LG,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            padding=LayoutConstants.PADDING_LG,
        )

    def did_mount(self) -> None:
        """
        Lifecycle: Se ejecuta cuando el componente se monta.

        Carga los lookups y datos de la empresa si es edición.
        """
        logger.info("CompanyFormView mounted, loading form data")

        # Suscribirse a cambios de estado
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)

        # Cargar datos del formulario
        if self.page:
            self.page.run_task(self._load_form_data)

    def will_unmount(self) -> None:
        """
        Lifecycle: Se ejecuta cuando el componente se desmonta.

        Limpia los observers.
        """
        logger.info("CompanyFormView unmounting")
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def _load_form_data(self) -> None:
        """Carga los datos del formulario (lookups y empresa si es edición)."""
        logger.info("Loading form data")
        self._is_loading = True
        self._error_message = ""

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
        if self.page:
            self.update()

        try:
            # Cargar lookups
            await self._load_lookups()

            # Si es edición, cargar datos de la empresa
            if self.company_id:
                await self._load_company_data()

            self._is_loading = False
            self._error_message = ""

        except Exception as e:
            logger.exception(f"Error loading form data: {e}")
            self._error_message = f"Error al cargar datos del formulario: {str(e)}"
            self._is_loading = False

        # Reconstruir contenido con los datos cargados o error
        self.content = self.build()
        if self.page:
            self.update()

        # Poblar los campos después de que se hayan creado
        if self.company_id and self._company_data:
            self._populate_form_fields()

    async def _load_lookups(self) -> None:
        """Carga los datos de lookups (tipos de empresa y países)."""
        logger.debug("Loading lookups for company form")

        try:
            from src.frontend.services.api import LookupAPI

            lookup_api = LookupAPI()

            # Cargar tipos de empresa
            self._company_types = await lookup_api.get_lookup("company_types")
            if self._company_type_field:
                type_options = [
                    {"label": ct["name"], "value": str(ct["id"])}
                    for ct in self._company_types
                ]
                self._company_type_field.set_options(type_options)

                # Establecer valor por defecto si es formulario de creación
                # default_type puede ser "CLIENT" o "SUPPLIER", buscar el ID correspondiente
                if not self.company_id and self.default_type:
                    # Buscar el tipo por nombre
                    matching_type = next(
                        (ct for ct in self._company_types if ct["name"].upper() == self.default_type),
                        None
                    )
                    if matching_type:
                        self._company_type_field.set_value(str(matching_type["id"]))

            # Cargar países
            self._countries = await lookup_api.get_lookup("countries")
            if self._country_field:
                country_options = [
                    {"label": c["name"], "value": str(c["id"])}
                    for c in self._countries
                ]
                self._country_field.set_options(country_options)

            logger.success(
                f"Lookups loaded: {len(self._company_types)} types, "
                f"{len(self._countries)} countries"
            )

        except Exception as e:
            logger.exception(f"Error loading lookups: {e}")
            raise

    async def _load_company_data(self) -> None:
        """Carga los datos de la empresa a editar."""
        if not self.company_id:
            return

        logger.debug(f"Loading company data for ID={self.company_id}")

        try:
            from src.frontend.services.api import CompanyAPI

            company_api = CompanyAPI()
            self._company_data = await company_api.get_by_id(self.company_id)

            logger.success(f"Company data loaded: {self._company_data.get('name')}")

        except Exception as e:
            logger.exception(f"Error loading company data: {e}")
            raise

    def _populate_form_fields(self) -> None:
        """Pobla los campos del formulario con los datos cargados."""
        if not self._company_data:
            return

        logger.debug("Populating form fields with company data")

        # Poblar campos con datos existentes
        if self._name_field:
            self._name_field.set_value(self._company_data.get("name", ""))

        if self._trigram_field:
            self._trigram_field.set_value(self._company_data.get("trigram", ""))

        if self._company_type_field:
            # El API devuelve company_type_id como entero
            company_type_id = self._company_data.get("company_type_id")
            if company_type_id:
                self._company_type_field.set_value(str(company_type_id))

        if self._phone_field:
            self._phone_field.set_value(self._company_data.get("phone", ""))

        if self._email_field:
            self._email_field.set_value(self._company_data.get("email", ""))

        if self._website_field:
            self._website_field.set_value(self._company_data.get("website", ""))

        if self._country_field:
            # El API devuelve country_id como entero
            country_id = self._company_data.get("country_id")
            if country_id:
                self._country_field.set_value(str(country_id))

        if self._is_active_switch:
            self._is_active_switch.value = self._company_data.get("is_active", True)

        logger.success("Form fields populated successfully")

        # Actualizar la UI después de poblar los campos
        if self.page:
            self.update()

    def _validate_form(self) -> bool:
        """
        Valida todos los campos del formulario.

        Returns:
            True si todos los campos son válidos, False en caso contrario
        """
        logger.debug("Validating company form")

        is_valid = True

        # Validar campos requeridos
        if self._name_field and not self._name_field.validate():
            is_valid = False

        if self._trigram_field and not self._trigram_field.validate():
            is_valid = False

        if self._company_type_field and not self._company_type_field.validate():
            is_valid = False

        # Validar campos opcionales con validators
        if self._phone_field and self._phone_field.get_value():
            if not self._phone_field.validate():
                is_valid = False

        if self._email_field and self._email_field.get_value():
            if not self._email_field.validate():
                is_valid = False

        if self._website_field and self._website_field.get_value():
            if not self._website_field.validate():
                is_valid = False

        logger.debug(f"Form validation result: {is_valid}")
        return is_valid

    def _get_form_data(self) -> dict:
        """
        Obtiene los datos del formulario.

        Returns:
            Diccionario con los datos del formulario
        """
        # Obtener y convertir company_type_id
        company_type_value = self._company_type_field.get_value() if self._company_type_field else None
        company_type_id = int(company_type_value) if company_type_value else None

        # Obtener y convertir country_id
        country_value = self._country_field.get_value() if self._country_field else None
        country_id = int(country_value) if country_value else None

        data = {
            "name": self._name_field.get_value() if self._name_field else "",
            "trigram": self._trigram_field.get_value() if self._trigram_field else "",
            "company_type_id": company_type_id,
            "phone": self._phone_field.get_value() if self._phone_field else None,
            "email": self._email_field.get_value() if self._email_field else None,
            "website": self._website_field.get_value() if self._website_field else None,
            "country_id": country_id,
            "is_active": (
                self._is_active_switch.value if self._is_active_switch else True
            ),
        }

        # Eliminar campos None para actualización parcial
        return {k: v for k, v in data.items() if v is not None or k == "is_active"}

    def _on_save_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en guardar."""
        logger.info("Save button clicked")

        if self.page:
            self.page.run_task(self.handle_save)

    async def handle_save(self) -> None:
        """
        Maneja el guardado de la empresa.

        Valida y envía los datos a la API.
        """
        logger.info("Handling company save")

        # Validar formulario
        if not self._validate_form():
            logger.warning("Form validation failed")
            # TODO: Mostrar notificación de error
            return

        self._is_saving = True

        # Deshabilitar botones
        if hasattr(self, '_save_button'):
            self._save_button.disabled = True
            self._cancel_button.disabled = True

        if self.page:
            self.update()

        try:
            from src.frontend.services.api import CompanyAPI

            company_api = CompanyAPI()
            form_data = self._get_form_data()

            if self.company_id:
                # Actualizar empresa existente
                logger.debug(f"Updating company ID={self.company_id}")
                updated_company = await company_api.update(self.company_id, form_data)
                logger.success(f"Company updated: {updated_company.get('name')}")
            else:
                # Crear nueva empresa
                logger.debug("Creating new company")
                new_company = await company_api.create(form_data)
                logger.success(f"Company created: {new_company.get('name')}")
                updated_company = new_company

            # Llamar callback de guardado
            if self.on_save:
                self.on_save(updated_company)

            # TODO: Mostrar notificación de éxito

        except Exception as e:
            logger.exception(f"Error saving company: {e}")
            # TODO: Mostrar notificación de error

        finally:
            self._is_saving = False

            # Rehabilitar botones
            if hasattr(self, '_save_button'):
                self._save_button.disabled = False
                self._cancel_button.disabled = False

            if self.page:
                self.update()

    def _on_cancel_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en cancelar."""
        logger.info("Cancel button clicked")

        if self.on_cancel:
            self.on_cancel()

    def _on_state_changed(self) -> None:
        """
        Observer: Se ejecuta cuando cambia el estado de tema o idioma.

        Actualiza la interfaz.
        """
        logger.debug("State changed, updating CompanyFormView")
        if self.page:
            self.update()
