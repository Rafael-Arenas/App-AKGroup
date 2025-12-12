"""
Vista de formulario para crear/editar nomenclaturas.

Permite crear nuevas nomenclaturas o editar existentes.
Incluye sección especial para BOM (Bill of Materials).
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import BaseCard, LoadingSpinner, ErrorDisplay
from src.frontend.components.forms import ValidatedTextField, DropdownField
from src.frontend.i18n.translation_manager import t
from src.frontend.views.products.components import BOMComponentRow


class NomenclatureFormView(ft.Column):
    """
    Vista de formulario para crear/editar nomenclaturas.

    Args:
        nomenclature_id: ID de la nomenclatura a editar (None para crear nueva)
        on_save: Callback cuando se guarda exitosamente
        on_cancel: Callback cuando se cancela

    Example:
        >>> form = NomenclatureFormView(nomenclature_id=123, on_save=handle_save)
        >>> page.add(form)
    """

    def __init__(
        self,
        nomenclature_id: int | None = None,
        on_save: Callable[[dict], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ):
        """Inicializa el formulario de nomenclatura."""
        super().__init__()
        self.nomenclature_id = nomenclature_id
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel

        # Estado
        self._is_loading: bool = True
        self._is_saving: bool = False
        self._error_message: str = ""
        self._nomenclature_data: dict | None = None

        # Lookups
        self._units: list[dict] = []
        self._family_types: list[dict] = []
        self._matters: list[dict] = []

        # BOM components state
        self._bom_components: list[dict] = []
        self._bom_rows: list[BOMComponentRow] = []

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

        logger.info(f"NomenclatureFormView initialized: nomenclature_id={nomenclature_id}")

    def _build_components(self) -> None:
        """Crea los componentes del formulario."""
        # Campos de información básica
        self._code_field = ValidatedTextField(
            label=t("nomenclatures.form.code") + " *",
            hint_text=t("nomenclatures.form.code_hint"),
            required=True,
            prefix_icon=ft.Icons.TAG,
            max_length=50,
        )

        self._name_field = ValidatedTextField(
            label=t("nomenclatures.form.name") + " *",
            hint_text=t("nomenclatures.form.name_hint"),
            required=True,
            prefix_icon=ft.Icons.LIST_ALT,
            max_length=200,
        )

        self._description_field = ValidatedTextField(
            label=t("nomenclatures.form.description"),
            hint_text=t("nomenclatures.form.description_hint"),
            multiline=True,
            max_length=1000,
        )

        # Campo de unidad
        self._unit_field = DropdownField(
            label=t("nomenclatures.form.unit"),
            options=[],
            required=False,
        )

        # Campos de clasificación (opcionales)
        self._family_type_field = DropdownField(
            label=t("nomenclatures.form.family_type"),
            options=[],
        )

        self._matter_field = DropdownField(
            label=t("nomenclatures.form.matter"),
            options=[],
        )

        # Campos de precios
        self._cost_price_field = ValidatedTextField(
            label=t("nomenclatures.form.cost_price"),
            hint_text="0.00",
            prefix_icon=ft.Icons.ATTACH_MONEY,
            validators=["numeric"],
        )

        self._sale_price_field = ValidatedTextField(
            label=t("nomenclatures.form.sale_price"),
            hint_text="0.00",
            prefix_icon=ft.Icons.SELL,
            validators=["numeric"],
        )

        self._is_active_switch = ft.Switch(
            label=t("nomenclatures.form.is_active"),
            value=True,
        )

        # Sección BOM
        self._bom_components_container = ft.Column(
            controls=[],
            spacing=LayoutConstants.SPACING_SM,
        )

        self._add_component_button = ft.ElevatedButton(
            text=t("nomenclatures.form.add_component"),
            icon=ft.Icons.ADD,
            on_click=self._on_add_component,
        )

        # Botones de acción
        self._save_button = ft.ElevatedButton(
            text=t("common.save"),
            icon=ft.Icons.SAVE,
            on_click=self._on_save_click,
        )

        self._cancel_button = ft.TextButton(
            text=t("common.cancel"),
            on_click=self._on_cancel_click,
        )

    def _build_layout(self) -> list[ft.Control]:
        """Construye el layout de la vista."""
        is_edit = self.nomenclature_id is not None
        title_key = "nomenclatures.edit_title" if is_edit else "nomenclatures.create_title"

        # Título
        title = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.EDIT if is_edit else ft.Icons.ADD_BOX,
                        size=32,
                    ),
                    ft.Text(
                        t(title_key),
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
        logger.info("NomenclatureFormView mounted, loading form data")

        # Cargar datos del formulario
        if self.page:
            self.page.run_task(self._load_form_data)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        logger.info("NomenclatureFormView unmounting")
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    def _show_loading(self) -> None:
        """Muestra el indicador de carga."""
        self.form_container.controls = [
            ft.Container(
                content=LoadingSpinner(message=t("common.loading")),
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
            title=t("nomenclatures.form.basic_info"),
            icon=ft.Icons.INFO_OUTLINED,
            content=ft.Column(
                controls=[
                    self._code_field,
                    self._name_field,
                    self._description_field,
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Sección clasificación
        classification_section = BaseCard(
            title=t("nomenclatures.form.classification"),
            icon=ft.Icons.CATEGORY,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(content=self._unit_field, expand=True),
                            ft.Container(content=self._family_type_field, expand=True),
                        ],
                        spacing=LayoutConstants.SPACING_MD,
                    ),
                    self._matter_field,
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Sección precios
        pricing_section = BaseCard(
            title=t("nomenclatures.form.pricing"),
            icon=ft.Icons.MONETIZATION_ON,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(content=self._cost_price_field, expand=True),
                            ft.Container(content=self._sale_price_field, expand=True),
                        ],
                        spacing=LayoutConstants.SPACING_MD,
                    ),
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Sección BOM (Bill of Materials)
        bom_section = BaseCard(
            title=t("nomenclatures.form.bom_section"),
            icon=ft.Icons.LIST_ALT,
            content=ft.Column(
                controls=[
                    self._bom_components_container,
                    self._add_component_button,
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Estado activo
        status_section = ft.Container(
            content=self._is_active_switch,
            padding=ft.padding.only(left=LayoutConstants.PADDING_MD),
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
            classification_section,
            pricing_section,
            bom_section,
            status_section,
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

            # Si es edición, cargar datos de la nomenclatura
            if self.nomenclature_id:
                await self._load_nomenclature_data()

            self._is_loading = False
            self._error_message = ""

            # Construir el formulario
            self._build_form()

            # Poblar los campos si es edición
            if self.nomenclature_id and self._nomenclature_data:
                self._populate_form()

        except Exception as e:
            logger.exception(f"Error loading form data: {e}")
            self._error_message = f"Error al cargar datos: {str(e)}"
            self._is_loading = False
            self._show_error()

    async def _load_lookups(self) -> None:
        """Carga los datos de lookups."""
        logger.debug("Loading lookups for nomenclature form")

        try:
            from src.frontend.services.api import LookupAPI

            lookup_api = LookupAPI()

            # Cargar unidades
            self._units = await lookup_api.get_lookup("units")
            unit_options = [
                {"label": u.get("name", u.get("code", "")), "value": str(u["id"])}
                for u in self._units
            ]
            self._unit_field.set_options(unit_options)

            # Cargar familias de producto
            try:
                self._family_types = await lookup_api.get_lookup("family_types")
                family_options = [
                    {"label": f.get("name", ""), "value": str(f["id"])}
                    for f in self._family_types
                ]
                self._family_type_field.set_options(family_options)
            except Exception as e:
                logger.warning(f"Could not load family_types: {e}")
                self._family_types = []

            # Cargar materias
            try:
                self._matters = await lookup_api.get_lookup("matters")
                matter_options = [
                    {"label": m.get("name", ""), "value": str(m["id"])}
                    for m in self._matters
                ]
                self._matter_field.set_options(matter_options)
            except Exception as e:
                logger.warning(f"Could not load matters: {e}")
                self._matters = []

            logger.success(
                f"Lookups loaded: {len(self._units)} units, "
                f"{len(self._family_types)} families, {len(self._matters)} matters"
            )

        except Exception as e:
            logger.exception(f"Error loading lookups: {e}")
            raise

    async def _load_nomenclature_data(self) -> None:
        """Carga los datos de la nomenclatura a editar."""
        logger.info(f"Loading nomenclature data: ID={self.nomenclature_id}")

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            self._nomenclature_data = await product_api.get_by_id(self.nomenclature_id)

            # Cargar componentes BOM
            try:
                bom_components = await product_api.get_bom_components(self.nomenclature_id)
                self._bom_components = bom_components or []
            except Exception as e:
                logger.warning(f"Could not load BOM components: {e}")
                self._bom_components = []

            logger.success(f"Nomenclature data loaded: {self._nomenclature_data.get('reference')}")

        except Exception as e:
            logger.exception(f"Error loading nomenclature data: {e}")
            raise

    def _populate_form(self) -> None:
        """Rellena los campos del formulario con los datos de la nomenclatura."""
        if not self._nomenclature_data:
            return

        logger.debug("Populating form fields with nomenclature data")

        # Campos básicos
        self._code_field.set_value(self._nomenclature_data.get("reference", ""))
        self._name_field.set_value(self._nomenclature_data.get("designation_es", ""))
        self._description_field.set_value(self._nomenclature_data.get("short_designation", ""))

        # Clasificación
        family_type_id = self._nomenclature_data.get("family_type_id")
        if family_type_id:
            self._family_type_field.set_value(str(family_type_id))

        matter_id = self._nomenclature_data.get("matter_id")
        if matter_id:
            self._matter_field.set_value(str(matter_id))

        # Precios
        cost_price = self._nomenclature_data.get("cost_price")
        if cost_price is not None:
            self._cost_price_field.set_value(str(cost_price))

        sale_price = self._nomenclature_data.get("sale_price")
        if sale_price is not None:
            self._sale_price_field.set_value(str(sale_price))

        # Estado
        self._is_active_switch.value = self._nomenclature_data.get("is_active", True)

        # Poblar componentes BOM
        for index, comp in enumerate(self._bom_components):
            self._add_component_row(comp, index)

        logger.success("Form fields populated successfully")

        # Actualizar la UI después de poblar los campos
        if self.page:
            self.update()

    def _on_add_component(self, e: ft.ControlEvent) -> None:
        """Callback para agregar componente a BOM."""
        logger.info("Add component clicked")

        # TODO: Implementar ArticleSelectorDialog
        if self.page:
            snackbar = ft.SnackBar(
                content=ft.Text("La funcionalidad de agregar componentes está en desarrollo"),
                bgcolor=ft.Colors.ORANGE,
                duration=3000,
            )
            self.page.overlay.append(snackbar)
            snackbar.open = True
            self.page.update()

    def _on_article_selected(
        self,
        article_id: int,
        article_code: str,
        article_name: str,
        quantity: float,
    ) -> None:
        """Callback cuando se selecciona un artículo en el diálogo."""
        logger.info(
            f"Article selected: id={article_id}, code={article_code}, quantity={quantity}"
        )

        # Agregar componente a la lista
        component_data = {
            "id": article_id,
            "code": article_code,
            "name": article_name,
            "quantity": quantity,
        }
        self._bom_components.append(component_data)

        # Crear fila de componente
        self._add_component_row(component_data, len(self._bom_components) - 1)

        logger.success(f"Component added to BOM: {article_code}")

    def _add_component_row(self, component_data: dict, index: int) -> None:
        """Agrega una fila de componente a la UI."""
        row = BOMComponentRow(
            component_data=component_data,
            on_quantity_change=self._on_component_quantity_change,
            on_remove=self._on_component_remove,
            index=index,
        )

        self._bom_rows.append(row)
        self._bom_components_container.controls.append(row)

        if self.page:
            self._bom_components_container.update()

    def _on_component_quantity_change(self, index: int, quantity: float) -> None:
        """Callback cuando cambia la cantidad de un componente."""
        if 0 <= index < len(self._bom_components):
            self._bom_components[index]["quantity"] = quantity
            logger.debug(f"Component quantity updated: index={index}, quantity={quantity}")

    def _on_component_remove(self, index: int) -> None:
        """Callback cuando se elimina un componente."""
        logger.info(f"Removing component at index={index}")

        if 0 <= index < len(self._bom_components):
            # Eliminar de la lista de datos
            removed = self._bom_components.pop(index)

            # Eliminar de la lista de filas
            if index < len(self._bom_rows):
                self._bom_rows.pop(index)

            # Reconstruir la UI
            self._rebuild_bom_components()

            logger.success(f"Component removed: {removed.get('code')}")

    def _rebuild_bom_components(self) -> None:
        """Reconstruye la lista de componentes en la UI."""
        self._bom_components_container.controls.clear()
        self._bom_rows.clear()

        for index, component_data in enumerate(self._bom_components):
            self._add_component_row(component_data, index)

        if self.page:
            self._bom_components_container.update()

    def _validate_form(self) -> bool:
        """Valida todos los campos del formulario."""
        logger.debug("Validating nomenclature form")

        is_valid = True

        # Validar campos requeridos
        if not self._code_field.validate():
            is_valid = False

        if not self._name_field.validate():
            is_valid = False

        # Validar campos numéricos opcionales
        if self._cost_price_field.get_value():
            if not self._cost_price_field.validate():
                is_valid = False

        if self._sale_price_field.get_value():
            if not self._sale_price_field.validate():
                is_valid = False

        logger.debug(f"Form validation result: {is_valid}")
        return is_valid

    def _get_form_data(self) -> dict:
        """Obtiene los datos del formulario mapeados para el API."""
        # Obtener valores de campos
        reference = self._code_field.get_value()
        designation_es = self._name_field.get_value()
        short_designation = self._description_field.get_value()

        # Obtener IDs de lookups
        family_value = self._family_type_field.get_value()
        family_type_id = int(family_value) if family_value else None

        matter_value = self._matter_field.get_value()
        matter_id = int(matter_value) if matter_value else None

        # Obtener precios
        cost_price_str = self._cost_price_field.get_value()
        cost_price = float(cost_price_str) if cost_price_str else None

        sale_price_str = self._sale_price_field.get_value()
        sale_price = float(sale_price_str) if sale_price_str else None

        # Construir datos - usar nombres del schema ProductCreate
        data = {
            "reference": reference,
            "designation_es": designation_es,
            "product_type": "nomenclature",  # Siempre nomenclatura en esta vista
            "is_active": self._is_active_switch.value,
        }

        # Agregar campos opcionales solo si tienen valor
        if short_designation:
            data["short_designation"] = short_designation

        if cost_price is not None:
            data["cost_price"] = cost_price

        if sale_price is not None:
            data["sale_price"] = sale_price

        if family_type_id:
            data["family_type_id"] = family_type_id

        if matter_id:
            data["matter_id"] = matter_id

        # Agregar componentes BOM
        if self._bom_components:
            data["components"] = [
                {
                    "component_id": comp.get("id") or comp.get("component_id"),
                    "quantity": comp["quantity"],
                }
                for comp in self._bom_components
            ]

        return data

    def _on_save_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en guardar."""
        logger.info("Save button clicked")

        if self.page:
            self.page.run_task(self.handle_save)

    async def handle_save(self) -> None:
        """Maneja el guardado de la nomenclatura."""
        logger.info("Handling nomenclature save")

        # Validar formulario
        if not self._validate_form():
            logger.warning("Form validation failed")
            return

        self._is_saving = True

        # Deshabilitar botones
        self._save_button.disabled = True
        self._save_button.text = t("common.saving")
        self._cancel_button.disabled = True

        if self.page:
            self.update()

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            form_data = self._get_form_data()

            # Extraer componentes del form_data para manejarlos por separado
            components_data = form_data.pop("components", [])

            if self.nomenclature_id:
                # Actualizar nomenclatura existente
                logger.debug(f"Updating nomenclature ID={self.nomenclature_id}")
                updated_nomenclature = await product_api.update(self.nomenclature_id, form_data)
                logger.success(f"Nomenclature updated: {updated_nomenclature.get('reference')}")

                # TODO: Actualizar componentes (requiere lógica adicional)

                message = t("nomenclatures.messages.updated").format(
                    name=updated_nomenclature.get("designation_es", updated_nomenclature.get("reference", ""))
                )
            else:
                # Crear nueva nomenclatura
                logger.debug("Creating new nomenclature")
                new_nomenclature = await product_api.create(form_data)
                logger.success(f"Nomenclature created: {new_nomenclature.get('reference')}")
                updated_nomenclature = new_nomenclature

                # Agregar componentes
                if components_data:
                    product_id = updated_nomenclature.get("id")
                    logger.info(f"Adding {len(components_data)} components to nomenclature {product_id}")

                    for comp_data in components_data:
                        try:
                            await product_api.add_component(
                                product_id,
                                {
                                    "parent_id": product_id,
                                    "component_id": comp_data["component_id"],
                                    "quantity": comp_data["quantity"],
                                }
                            )
                        except Exception as e:
                            logger.error(f"Error adding component: {e}")

                    logger.success(f"Components added to nomenclature {product_id}")

                message = t("nomenclatures.messages.created").format(
                    name=new_nomenclature.get("designation_es", new_nomenclature.get("reference", ""))
                )

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
                self.on_save_callback(updated_nomenclature)

        except Exception as e:
            logger.exception(f"Error saving nomenclature: {e}")

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

    def _on_cancel_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en cancelar."""
        logger.info("Cancel button clicked")

        if self.on_cancel_callback:
            self.on_cancel_callback()

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        logger.debug("NomenclatureFormView state changed, rebuilding content")
        # Reconstruir los componentes del formulario con nuevas traducciones
        self._build_components()
        # Reconstruir el contenido del formulario
        self._build_form()
        # Reconstruir el layout principal
        self.controls = self._build_layout()
        if self.page:
            self.update()
