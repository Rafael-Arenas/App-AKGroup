"""
Vista de formulario para crear/editar productos.

Permite crear nuevos productos o editar existentes.
Incluye sección especial para BOM (Bill of Materials) si es nomenclatura.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import BaseCard, LoadingSpinner, ErrorDisplay
from src.frontend.components.forms import ValidatedTextField, DropdownField


class ProductFormView(ft.Column):
    """
    Vista de formulario para crear/editar productos.

    Args:
        product_id: ID del producto a editar (None para crear nuevo)
        on_save: Callback cuando se guarda exitosamente
        on_cancel: Callback cuando se cancela

    Example:
        >>> form = ProductFormView(product_id=123, on_save=handle_save)
        >>> page.add(form)
    """

    def __init__(
        self,
        product_id: int | None = None,
        on_save: Callable[[dict], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ):
        """Inicializa el formulario de producto."""
        super().__init__()
        self.product_id = product_id
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel

        # Estado
        self._is_loading: bool = True
        self._is_saving: bool = False
        self._error_message: str = ""
        self._product_data: dict | None = None

        # Lookups
        self._product_types: list[dict] = []
        self._units: list[dict] = []
        self._components: list[dict] = []

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

        logger.info(f"ProductFormView initialized: product_id={product_id}")

    def _build_components(self) -> None:
        """Crea los componentes del formulario."""
        # Campos del formulario
        self._code_field = ValidatedTextField(
            label="Código *",
            hint_text="Código único del producto",
            required=True,
            prefix_icon=ft.Icons.TAG,
        )

        self._name_field = ValidatedTextField(
            label="Nombre *",
            hint_text="Nombre del producto",
            required=True,
            prefix_icon=ft.Icons.INVENTORY_2,
        )

        self._description_field = ValidatedTextField(
            label="Descripción",
            hint_text="Descripción detallada",
            multiline=True,
        )

        self._type_field = DropdownField(
            label="Tipo *",
            options=[],
            required=True,
            on_change=self._on_type_change,
        )

        self._unit_field = DropdownField(
            label="Unidad *",
            options=[],
            required=True,
        )

        self._cost_field = ValidatedTextField(
            label="Costo *",
            hint_text="0.00",
            required=True,
            prefix_icon=ft.Icons.ATTACH_MONEY,
        )

        self._is_active_switch = ft.Switch(
            label="Producto Activo",
            value=True,
        )

        # Sección BOM (se muestra solo si es nomenclatura)
        self._bom_section = ft.Container(
            content=BaseCard(
                title="Lista de Materiales (BOM)",
                icon=ft.Icons.LIST_ALT,
                content=ft.Column(
                    controls=[
                        ft.Text("Componentes del producto..."),
                        ft.ElevatedButton(
                            text="Agregar Componente",
                            icon=ft.Icons.ADD,
                            on_click=self._on_add_component,
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_MD,
                ),
            ),
            visible=False,
        )

        # Botones de acción
        self._save_button = ft.ElevatedButton(
            text="Guardar",
            icon=ft.Icons.SAVE,
            on_click=self._on_save_click,
        )

        self._cancel_button = ft.TextButton(
            text="Cancelar",
            on_click=self._on_cancel_click,
        )

    def _build_layout(self) -> list[ft.Control]:
        """Construye el layout de la vista."""
        is_edit = self.product_id is not None

        # Título
        title = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.EDIT if is_edit else ft.Icons.ADD_BOX,
                        size=32,
                    ),
                    ft.Text(
                        "Editar Producto" if is_edit else "Crear Producto",
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
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.info("ProductFormView mounted, loading form data")

        # Cargar datos del formulario
        if self.page:
            self.page.run_task(self._load_form_data)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        logger.info("ProductFormView unmounting")
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    def _show_loading(self) -> None:
        """Muestra el indicador de carga."""
        self.form_container.controls = [
            ft.Container(
                content=LoadingSpinner(message="Cargando formulario..."),
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
        # Sección información básica
        basic_section = BaseCard(
            title="Información Básica",
            icon=ft.Icons.INFO_OUTLINED,
            content=ft.Column(
                controls=[
                    self._code_field,
                    self._name_field,
                    self._description_field,
                    self._type_field,
                    self._unit_field,
                    self._cost_field,
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
            basic_section,
            self._bom_section,
            action_buttons,
        ]

        if self.page:
            self.update()

    async def _load_form_data(self) -> None:
        """Carga los datos del formulario."""
        logger.info("Loading form data")
        self._is_loading = True
        self._error_message = ""

        # Mostrar loading
        self._show_loading()

        try:
            # Cargar lookups
            await self._load_lookups()

            # Si es edición, cargar datos del producto
            if self.product_id:
                await self._load_product_data()

            self._is_loading = False
            self._error_message = ""

            # Construir el formulario
            self._build_form()

            # Poblar los campos si es edición
            if self.product_id and self._product_data:
                self._populate_form()

        except Exception as e:
            logger.exception(f"Error loading form data: {e}")
            self._error_message = f"Error al cargar datos: {str(e)}"
            self._is_loading = False
            self._show_error()

    async def _load_lookups(self) -> None:
        """Carga los datos de lookups."""
        logger.debug("Loading lookups for product form")

        try:
            from src.frontend.services.api import LookupAPI

            lookup_api = LookupAPI()

            # Cargar tipos de producto
            self._product_types = await lookup_api.get_lookup("product_types")
            type_options = [
                {"label": pt["name"], "value": pt["code"]}
                for pt in self._product_types
            ]
            self._type_field.set_options(type_options)

            # Cargar unidades
            self._units = await lookup_api.get_lookup("units")
            unit_options = [
                {"label": u["name"], "value": u["code"]} for u in self._units
            ]
            self._unit_field.set_options(unit_options)

            logger.success(
                f"Lookups loaded: {len(self._product_types)} types, "
                f"{len(self._units)} units"
            )

        except Exception as e:
            logger.exception(f"Error loading lookups: {e}")
            raise

    async def _load_product_data(self) -> None:
        """Carga los datos del producto a editar."""
        if not self.product_id:
            return

        logger.debug(f"Loading product data for ID={self.product_id}")

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            self._product_data = await product_api.get_by_id(self.product_id)

            logger.success(f"Product data loaded: {self._product_data.get('name')}")

        except Exception as e:
            logger.exception(f"Error loading product data: {e}")
            raise

    def _populate_form(self) -> None:
        """Pobla los campos del formulario con los datos cargados."""
        if not self._product_data:
            return

        logger.debug("Populating form fields with product data")

        # Poblar campos
        self._code_field.set_value(self._product_data.get("code", ""))
        self._name_field.set_value(self._product_data.get("name", ""))
        self._description_field.set_value(self._product_data.get("description", ""))
        self._type_field.set_value(self._product_data.get("product_type", ""))
        self._unit_field.set_value(self._product_data.get("unit", ""))
        self._cost_field.set_value(str(self._product_data.get("cost", 0)))
        self._is_active_switch.value = self._product_data.get("is_active", True)

        # Mostrar BOM si es nomenclatura
        if self._product_data.get("product_type") == "NOMENCLATURE":
            self._show_bom_section()

        logger.success("Form fields populated successfully")

        # Actualizar la UI después de poblar los campos
        if self.page:
            self.update()

    def _on_type_change(self, value: str) -> None:
        """Callback cuando cambia el tipo de producto."""
        if value == "NOMENCLATURE":
            self._show_bom_section()
        else:
            self._hide_bom_section()

    def _show_bom_section(self) -> None:
        """Muestra la sección de BOM."""
        if self._bom_section:
            self._bom_section.visible = True
            if self.page:
                self.update()

    def _hide_bom_section(self) -> None:
        """Oculta la sección de BOM."""
        if self._bom_section:
            self._bom_section.visible = False
            if self.page:
                self.update()

    def _on_add_component(self, e: ft.ControlEvent) -> None:
        """Callback para agregar componente a BOM."""
        logger.info("Add component clicked")
        # TODO: Mostrar diálogo para agregar componente

    def _validate_form(self) -> bool:
        """Valida todos los campos del formulario."""
        logger.debug("Validating product form")

        is_valid = True

        # Validar campos requeridos
        if not self._code_field.validate():
            is_valid = False

        if not self._name_field.validate():
            is_valid = False

        if not self._type_field.validate():
            is_valid = False

        if not self._unit_field.validate():
            is_valid = False

        if not self._cost_field.validate():
            is_valid = False

        logger.debug(f"Form validation result: {is_valid}")
        return is_valid

    def _get_form_data(self) -> dict:
        """Obtiene los datos del formulario."""
        return {
            "code": self._code_field.get_value(),
            "name": self._name_field.get_value(),
            "description": self._description_field.get_value() or None,
            "product_type": self._type_field.get_value(),
            "unit": self._unit_field.get_value(),
            "cost": float(self._cost_field.get_value() or 0),
            "is_active": self._is_active_switch.value,
        }

    def _on_save_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en guardar."""
        logger.info("Save button clicked")

        if self.page:
            self.page.run_task(self.handle_save)

    async def handle_save(self) -> None:
        """Maneja el guardado del producto."""
        logger.info("Handling product save")

        # Validar formulario
        if not self._validate_form():
            logger.warning("Form validation failed")
            return

        self._is_saving = True

        # Deshabilitar botones
        self._save_button.disabled = True
        self._save_button.text = "Guardando..."
        self._cancel_button.disabled = True

        if self.page:
            self.update()

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            form_data = self._get_form_data()

            if self.product_id:
                # Actualizar producto existente
                logger.debug(f"Updating product ID={self.product_id}")
                updated_product = await product_api.update(self.product_id, form_data)
                logger.success(f"Product updated: {updated_product.get('name')}")
                message = f"Producto '{updated_product.get('name')}' actualizado exitosamente"
            else:
                # Crear nuevo producto
                logger.debug("Creating new product")
                new_product = await product_api.create(form_data)
                logger.success(f"Product created: {new_product.get('name')}")
                updated_product = new_product
                message = f"Producto '{new_product.get('name')}' creado exitosamente"

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
                self.on_save_callback(updated_product)

        except Exception as e:
            logger.exception(f"Error saving product: {e}")

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
            self._save_button.text = "Guardar"
            self._cancel_button.disabled = False

            if self.page:
                try:
                    self.update()
                except AssertionError:
                    # El control ya fue removido de la página
                    pass

    def _on_cancel_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en cancelar."""
        logger.info("Cancel button clicked")

        if self.on_cancel_callback:
            self.on_cancel_callback()

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        logger.debug("State changed, updating ProductFormView")
        if self.page:
            self.update()
