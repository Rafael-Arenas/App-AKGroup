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


class ProductFormView(ft.Container):
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
        self.on_save = on_save
        self.on_cancel = on_cancel

        self._is_loading: bool = True
        self._is_saving: bool = False
        self._error_message: str = ""
        self._product_data: dict | None = None
        self._product_types: list[dict] = []
        self._units: list[dict] = []
        self._components: list[dict] = []

        # Campos
        self._code_field: ValidatedTextField | None = None
        self._name_field: ValidatedTextField | None = None
        self._description_field: ValidatedTextField | None = None
        self._type_field: DropdownField | None = None
        self._unit_field: DropdownField | None = None
        self._cost_field: ValidatedTextField | None = None
        self._is_active_switch: ft.Switch | None = None
        self._bom_section: ft.Container | None = None

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = 0

        # Construir contenido inicial
        self.content = self.build()

        logger.info(f"ProductFormView initialized: product_id={product_id}")

    def build(self) -> ft.Control:
        """Construye el componente del formulario."""
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
        is_edit = self.product_id is not None

        title = ft.Text(
            "Editar Producto" if is_edit else "Crear Producto",
            size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
            weight=LayoutConstants.FONT_WEIGHT_BOLD,
        )

        # Campos básicos
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

        # Botones
        save_button = ft.ElevatedButton(
            text="Guardar",
            icon=ft.Icons.SAVE,
            on_click=self._on_save_click,
            disabled=self._is_saving,
        )

        cancel_button = ft.TextButton(
            text="Cancelar",
            on_click=self._on_cancel_click,
            disabled=self._is_saving,
        )

        actions = ft.Row(
            controls=[save_button, cancel_button],
            spacing=LayoutConstants.SPACING_SM,
            alignment=ft.MainAxisAlignment.END,
        )

        # Contenido principal del formulario
        return ft.Container(
            content=ft.Column(
                controls=[title, basic_section, self._bom_section, actions],
                spacing=LayoutConstants.SPACING_LG,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            padding=LayoutConstants.PADDING_LG,
        )

    def did_mount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.info("ProductFormView mounted")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        if self.page:
            self.page.run_task(self._load_form_data)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def _load_form_data(self) -> None:
        """Carga los datos del formulario."""
        self._is_loading = True
        self._error_message = ""

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
        if self.page:
            self.update()

        try:
            await self._load_lookups()
            if self.product_id:
                await self._load_product_data()
            self._is_loading = False
        except Exception as e:
            logger.exception(f"Error loading form data: {e}")
            self._error_message = f"Error al cargar datos: {str(e)}"
            self._is_loading = False

        # Reconstruir contenido con los datos cargados o error
        self.content = self.build()
        if self.page:
            self.update()

        # Poblar los campos después de que se hayan creado
        if self.product_id and self._product_data:
            self._populate_form_fields()

    async def _load_lookups(self) -> None:
        """Carga los datos de lookups."""
        from src.frontend.services.api import LookupAPI

        lookup_api = LookupAPI()

        self._product_types = await lookup_api.get_lookup("product_types")
        if self._type_field:
            type_options = [
                {"label": pt["name"], "value": pt["code"]}
                for pt in self._product_types
            ]
            self._type_field.set_options(type_options)

        self._units = await lookup_api.get_lookup("units")
        if self._unit_field:
            unit_options = [
                {"label": u["name"], "value": u["code"]} for u in self._units
            ]
            self._unit_field.set_options(unit_options)

    async def _load_product_data(self) -> None:
        """Carga los datos del producto a editar."""
        if not self.product_id:
            return

        from src.frontend.services.api import ProductAPI

        product_api = ProductAPI()
        self._product_data = await product_api.get_by_id(self.product_id)

        logger.success(f"Product data loaded: {self._product_data.get('name')}")

    def _populate_form_fields(self) -> None:
        """Pobla los campos del formulario con los datos cargados."""
        if not self._product_data:
            return

        logger.debug("Populating form fields with product data")

        # Poblar campos
        if self._code_field:
            self._code_field.set_value(self._product_data.get("code", ""))
        if self._name_field:
            self._name_field.set_value(self._product_data.get("name", ""))
        if self._description_field:
            self._description_field.set_value(self._product_data.get("description", ""))
        if self._type_field:
            self._type_field.set_value(self._product_data.get("product_type", ""))
        if self._unit_field:
            self._unit_field.set_value(self._product_data.get("unit", ""))
        if self._cost_field:
            self._cost_field.set_value(str(self._product_data.get("cost", 0)))
        if self._is_active_switch:
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
        is_valid = True

        if self._code_field and not self._code_field.validate():
            is_valid = False
        if self._name_field and not self._name_field.validate():
            is_valid = False
        if self._type_field and not self._type_field.validate():
            is_valid = False
        if self._unit_field and not self._unit_field.validate():
            is_valid = False
        if self._cost_field and not self._cost_field.validate():
            is_valid = False

        return is_valid

    def _get_form_data(self) -> dict:
        """Obtiene los datos del formulario."""
        return {
            "code": self._code_field.get_value() if self._code_field else "",
            "name": self._name_field.get_value() if self._name_field else "",
            "description": (
                self._description_field.get_value() if self._description_field else ""
            ),
            "product_type": self._type_field.get_value() if self._type_field else "",
            "unit": self._unit_field.get_value() if self._unit_field else "",
            "cost": float(self._cost_field.get_value() if self._cost_field else 0),
            "is_active": self._is_active_switch.value if self._is_active_switch else True,
        }

    def _on_save_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en guardar."""
        if self.page:
            self.page.run_task(self.handle_save)

    async def handle_save(self) -> None:
        """Maneja el guardado del producto."""
        if not self._validate_form():
            logger.warning("Form validation failed")
            return

        self._is_saving = True
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            form_data = self._get_form_data()

            if self.product_id:
                updated_product = await product_api.update(self.product_id, form_data)
                logger.success(f"Product updated: {updated_product.get('name')}")
            else:
                new_product = await product_api.create(form_data)
                logger.success(f"Product created: {new_product.get('name')}")
                updated_product = new_product

            if self.on_save:
                self.on_save(updated_product)

        except Exception as e:
            logger.exception(f"Error saving product: {e}")

        finally:
            self._is_saving = False
            if self.page:
                self.update()

    def _on_cancel_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en cancelar."""
        if self.on_cancel:
            self.on_cancel()

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        if self.page:
            self.update()
