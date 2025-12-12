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
from src.frontend.i18n.translation_manager import t


class CompanyFormView(ft.Column):
    """
    Vista de formulario para crear/editar empresas.

    Args:
        company_id: ID de la empresa a editar (None para crear nueva)
        default_type: Tipo por defecto ("CLIENT" o "SUPPLIER")
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
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel

        # Estado
        self._is_loading: bool = True
        self._is_saving: bool = False
        self._error_message: str = ""
        self._company_data: dict | None = None

        # Lookups
        self._company_types: list[dict] = []
        self._countries: list[dict] = []
        self._cities: list[dict] = []

        # Configuración del layout
        self.spacing = LayoutConstants.SPACING_MD
        self.expand = True
        self.scroll = ft.ScrollMode.AUTO

        # Suscribirse a cambios de estado
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)

        # Construir componentes
        self._build_components()

        # Contenedor para el formulario
        self.form_container = ft.Column(
            spacing=LayoutConstants.SPACING_LG,
            expand=True,
        )

        # Construir layout inicial
        self.controls = self._build_layout()

        logger.info(
            f"CompanyFormView initialized: "
            f"company_id={company_id}, default_type={default_type}, "
            f"mode={'edit' if company_id else 'create'}"
        )

    def _build_components(self) -> None:
        """Crea los componentes del formulario."""
        # Campos del formulario
        self._name_field = ValidatedTextField(
            label=t("companies.form.name") + " *",
            hint_text=t("companies.form.name_hint"),
            required=True,
            prefix_icon=ft.Icons.BUSINESS,
        )

        self._trigram_field = ValidatedTextField(
            label=t("companies.form.trigram") + " *",
            hint_text=t("companies.form.trigram_hint"),
            required=True,
            max_length=3,
            validators=["max_length"],
            prefix_icon=ft.Icons.TAG,
        )

        self._company_type_field = DropdownField(
            label=t("companies.form.company_type") + " *",
            options=[],  # Se cargarán dinámicamente
            required=True,
        )

        self._phone_field = ValidatedTextField(
            label=t("companies.form.phone"),
            hint_text=t("companies.form.phone_hint"),
            validators=["phone"],
            prefix_icon=ft.Icons.PHONE,
        )

        self._website_field = ValidatedTextField(
            label=t("companies.form.website"),
            hint_text=t("companies.form.website_hint"),
            validators=["url"],
            prefix_icon=ft.Icons.LANGUAGE,
        )

        self._country_field = DropdownField(
            label=t("companies.form.country"),
            options=[],  # Se cargarán dinámicamente
            on_change=self._on_country_change,
        )

        self._city_field = DropdownField(
            label=t("companies.columns.city"),
            options=[],  # Se cargarán dinámicamente
        )

        self._is_active_switch = ft.Switch(
            label=t("companies.form.is_active"),
            value=True,
        )

        # Botones de acción
        self._save_button = ft.ElevatedButton(
            text=t("common.save"),
            icon=ft.Icons.SAVE,
            on_click=self._on_save_click,
        )

        self._cancel_button = ft.ElevatedButton(
            text=t("common.cancel"),
            on_click=self._on_cancel_click,
        )

    def _get_form_title(self) -> str:
        """Obtiene el título del formulario según el tipo y modo."""
        is_edit = self.company_id is not None
        
        # Si es edición, obtener el tipo de los datos cargados
        if is_edit and self._company_data:
            company_type = self._company_data.get("company_type", "").upper()
        elif is_edit:
            # Si aún no se cargaron los datos, usar título genérico
            return t("companies.form.edit_title")
        else:
            # Si es creación, usar el tipo por defecto
            company_type = self.default_type.upper()
        
        # Determinar el título según el tipo
        if company_type == "CLIENT":
            return t("companies.form.edit_client" if is_edit else "companies.form.create_client")
        elif company_type == "SUPPLIER":
            return t("companies.form.edit_supplier" if is_edit else "companies.form.create_supplier")
        else:
            return t("companies.form.edit_title" if is_edit else "companies.form.create_title")

    def _build_layout(self) -> list[ft.Control]:
        """Construye el layout de la vista."""
        is_edit = self.company_id is not None

        # Título
        title = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.EDIT if is_edit else ft.Icons.ADD_BUSINESS,
                        size=32,
                    ),
                    ft.Text(
                        self._get_form_title(),
                        size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                        weight=LayoutConstants.FONT_WEIGHT_BOLD,
                    ),
                ],
                spacing=LayoutConstants.SPACING_SM,
            ),
            padding=LayoutConstants.PADDING_MD,
        )

        # Contenedor para el formulario o estados de loading/error
        form_content = ft.Container(
            content=self.form_container,
            padding=LayoutConstants.PADDING_LG,
            expand=True,
        )

        return [
            title,
            ft.Divider(height=1, opacity=0.2),
            form_content,
        ]

    def did_mount(self) -> None:
        """
        Lifecycle: Se ejecuta cuando el componente se monta.

        Carga los lookups y datos de la empresa si es edición.
        """
        logger.info("CompanyFormView mounted, loading form data")

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

    def _show_loading(self) -> None:
        """Muestra el indicador de carga."""
        self.form_container.controls = [
            ft.Container(
                content=LoadingSpinner(message=t("companies.form.loading")),
                expand=True,
                alignment=ft.alignment.center,
            )
        ]
        if self.page:
            self.update()

    def _show_error(self) -> None:
        """Muestra el error."""
        self.form_container.controls = [
            ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self._load_form_data,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )
        ]
        if self.page:
            self.update()

    def _build_form(self) -> None:
        """Construye el formulario completo."""
        # Sección: Información Básica
        basic_info_section = BaseCard(
            title=t("companies.form.basic_info"),
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
            title=t("companies.form.contact_info"),
            icon=ft.Icons.CONTACT_MAIL_OUTLINED,
            content=ft.Column(
                controls=[
                    self._phone_field,
                    self._website_field,
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Sección: Ubicación
        location_section = BaseCard(
            title=t("companies.form.location"),
            icon=ft.Icons.LOCATION_ON_OUTLINED,
            content=ft.Column(
                controls=[
                    self._country_field,
                    self._city_field,
                    self._is_active_switch,
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Botones de acción
        action_buttons = ft.Row(
            controls=[self._save_button, self._cancel_button],
            spacing=LayoutConstants.SPACING_SM,
            alignment=ft.MainAxisAlignment.END,
        )

        # Actualizar el contenedor del formulario
        self.form_container.controls = [
            basic_info_section,
            contact_info_section,
            location_section,
            action_buttons,
        ]

        if self.page:
            self.update()

    async def _load_form_data(self) -> None:
        """Carga los datos del formulario (lookups y empresa si es edición)."""
        logger.info("Loading form data")
        self._is_loading = True
        self._error_message = ""

        # Mostrar loading
        self._show_loading()

        try:
            # Cargar lookups
            await self._load_lookups()

            # Si es edición, cargar datos de la empresa
            if self.company_id:
                await self._load_company_data()

            self._is_loading = False
            self._error_message = ""

            # Construir el formulario
            self._build_form()

            # Poblar los campos si es edición
            if self.company_id and self._company_data:
                self._populate_form()
                # Reconstruir el layout para actualizar el título con el tipo correcto
                self.controls = self._build_layout()

        except Exception as e:
            logger.exception(f"Error loading form data: {e}")
            self._error_message = t("companies.form.error_loading").format(error=str(e))
            self._is_loading = False
            self._show_error()

    async def _load_lookups(self) -> None:
        """Carga los datos de lookups (tipos de empresa y países)."""
        logger.debug("Loading lookups for company form")

        try:
            from src.frontend.services.api import LookupAPI

            lookup_api = LookupAPI()

            # Cargar tipos de empresa
            self._company_types = await lookup_api.get_lookup("company_types")
            type_options = [
                {"label": ct["name"], "value": str(ct["id"])}
                for ct in self._company_types
            ]
            self._company_type_field.set_options(type_options)

            # Establecer valor por defecto si es formulario de creación
            if not self.company_id and self.default_type:
                matching_type = next(
                    (ct for ct in self._company_types if ct["name"].upper() == self.default_type),
                    None
                )
                if matching_type:
                    self._company_type_field.set_value(str(matching_type["id"]))

            # Cargar países
            self._countries = await lookup_api.get_lookup("countries")
            country_options = [
                {"label": c["name"], "value": str(c["id"])}
                for c in self._countries
            ]
            self._country_field.set_options(country_options)

            # Cargar ciudades
            self._cities = await lookup_api.get_lookup("cities")
            city_options = [
                {"label": c["name"], "value": str(c["id"])}
                for c in self._cities
            ]
            self._city_field.set_options(city_options)

            logger.success(
                f"Lookups loaded: {len(self._company_types)} types, "
                f"{len(self._countries)} countries, {len(self._cities)} cities"
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

    def _populate_form(self) -> None:
        """Pobla los campos del formulario con los datos cargados."""
        if not self._company_data:
            return

        logger.debug("Populating form fields with company data")

        # Poblar campos con datos existentes
        self._name_field.set_value(self._company_data.get("name", ""))
        self._trigram_field.set_value(self._company_data.get("trigram", ""))

        # El API devuelve company_type_id como entero
        company_type_id = self._company_data.get("company_type_id")
        if company_type_id:
            self._company_type_field.set_value(str(company_type_id))

        self._phone_field.set_value(self._company_data.get("phone", ""))
        self._website_field.set_value(self._company_data.get("website", ""))

        # El API devuelve country_id como entero
        # Primero establecer el país (esto filtrará las ciudades automáticamente)
        country_id = self._company_data.get("country_id")
        if country_id:
            self._country_field.set_value(str(country_id))
            # Filtrar ciudades manualmente ya que set_value no dispara on_change
            self._on_country_change(str(country_id))

        # El API devuelve city_id como entero
        # Establecer la ciudad después de filtrar por país
        city_id = self._company_data.get("city_id")
        if city_id:
            self._city_field.set_value(str(city_id))

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
        if not self._name_field.validate():
            is_valid = False

        if not self._trigram_field.validate():
            is_valid = False

        if not self._company_type_field.validate():
            is_valid = False

        # Validar campos opcionales con validators
        if self._phone_field.get_value():
            if not self._phone_field.validate():
                is_valid = False

        if self._website_field.get_value():
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
        company_type_value = self._company_type_field.get_value()
        company_type_id = int(company_type_value) if company_type_value else None

        # Obtener y convertir country_id
        country_value = self._country_field.get_value()
        country_id = int(country_value) if country_value else None

        # Obtener y convertir city_id
        city_value = self._city_field.get_value()
        city_id = int(city_value) if city_value else None

        data = {
            "name": self._name_field.get_value(),
            "trigram": self._trigram_field.get_value(),
            "company_type_id": company_type_id,
            "phone": self._phone_field.get_value() or None,
            "website": self._website_field.get_value() or None,
            "country_id": country_id,
            "city_id": city_id,
            "is_active": self._is_active_switch.value,
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
            return

        self._is_saving = True

        # Deshabilitar botones
        self._save_button.disabled = True
        self._save_button.text = t("companies.form.saving")
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
                message = t("companies.form.updated_success").format(name=updated_company.get('name'))
            else:
                # Crear nueva empresa
                logger.debug("Creating new company")
                new_company = await company_api.create(form_data)
                logger.success(f"Company created: {new_company.get('name')}")
                updated_company = new_company
                message = t("companies.form.created_success").format(name=new_company.get('name'))

            # Mostrar mensaje de éxito
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=ft.Colors.GREEN,
                    duration=3000,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()

            # Llamar callback de guardado
            if self.on_save_callback:
                self.on_save_callback(updated_company)

        except Exception as e:
            logger.exception(f"Error saving company: {e}")

            # Mostrar mensaje de error
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(f"Error: {str(e)}"),
                    bgcolor=ft.Colors.RED,
                    duration=5000,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()

        finally:
            self._is_saving = False

            # Rehabilitar botones
            self._save_button.disabled = False
            self._save_button.text = t("common.save")
            self._cancel_button.disabled = False

            if self.page:
                try:
                    self.update()
                except AssertionError:
                    # El control ya fue removido de la página
                    pass

    def _on_country_change(self, country_id: str) -> None:
        """
        Callback cuando cambia el país seleccionado.

        Filtra las ciudades para mostrar solo las del país seleccionado.

        Args:
            country_id: ID del país seleccionado
        """
        logger.debug(f"Country changed to: {country_id}")

        # Limpiar la ciudad seleccionada
        self._city_field.clear()

        # Filtrar ciudades por país
        if country_id and self._cities:
            filtered_cities = [
                city for city in self._cities
                if str(city.get("country_id")) == country_id
            ]

            city_options = [
                {"label": c["name"], "value": str(c["id"])}
                for c in filtered_cities
            ]

            self._city_field.set_options(city_options)
            logger.debug(f"Filtered {len(filtered_cities)} cities for country {country_id}")
        else:
            # Si no hay país seleccionado, mostrar todas las ciudades
            city_options = [
                {"label": c["name"], "value": str(c["id"])}
                for c in self._cities
            ]
            self._city_field.set_options(city_options)

    def _on_cancel_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en cancelar."""
        logger.info("Cancel button clicked")

        if self.on_cancel_callback:
            self.on_cancel_callback()

    def _on_state_changed(self) -> None:
        """
        Observer: Se ejecuta cuando cambia el estado de tema o idioma.

        Actualiza la interfaz.
        """
        logger.debug("CompanyFormView state changed, rebuilding content")
        # Reconstruir los componentes del formulario con nuevas traducciones
        self._build_components()
        # Reconstruir el contenido del formulario
        self._build_form()
        # Reconstruir el layout principal
        self.controls = self._build_layout()
        if self.page:
            self.update()
