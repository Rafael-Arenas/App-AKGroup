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
from src.frontend.i18n.translation_manager import t
from src.frontend.views.products.components import BOMComponentRow  # ArticleSelectorDialog
from src.frontend.utils.fake_data_generator import FakeDataGenerator


class ProductFormView(ft.Column):
    """
    Vista de formulario para crear/editar productos.

    Args:
        product_id: ID del producto a editar (None para crear nuevo)
        on_save: Callback cuando se guarda exitosamente
        on_cancel: Callback cuando se cancela
        view_mode: Modo de vista ("articles" o "nomenclatures")

    Example:
        >>> form = ProductFormView(product_id=123, on_save=handle_save)
        >>> page.add(form)
    """

    def __init__(
        self,
        product_id: int | None = None,
        on_save: Callable[[dict], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
        view_mode: str = "articles",
    ):
        """Inicializa el formulario de producto."""
        super().__init__()
        self.product_id = product_id
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel
        self._view_mode = view_mode
        self._is_nomenclatures = view_mode == "nomenclatures"

        # Estado
        self._is_loading: bool = True
        self._is_saving: bool = False
        self._error_message: str = ""
        self._product_data: dict | None = None

        # Lookups
        self._units: list[dict] = []
        self._family_types: list[dict] = []
        self._matters: list[dict] = []
        
        # BOM components state
        self._bom_components: list[dict] = []  # Lista de componentes agregados
        self._bom_rows: list[BOMComponentRow] = []  # Filas de componentes en UI

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

    def _get_translation_prefix(self) -> str:
        """Obtiene el prefijo de traducción según el modo de vista."""
        return "nomenclatures" if self._is_nomenclatures else "articles"

    def _build_components(self) -> None:
        """Crea los componentes del formulario."""
        # Obtener prefijo de traducción
        prefix = self._get_translation_prefix()
        
        # Campos de información básica
        self._code_field = ValidatedTextField(
            label=t(f"{prefix}.form.code") + " *",
            hint_text=t(f"{prefix}.form.code_hint"),
            required=True,
            prefix_icon=ft.Icons.TAG,
            max_length=50,
        )

        self._name_field = ValidatedTextField(
            label=t(f"{prefix}.form.name") + " *",
            hint_text=t(f"{prefix}.form.name_hint"),
            required=True,
            prefix_icon=ft.Icons.INVENTORY_2,
            max_length=200,
        )

        self._description_field = ValidatedTextField(
            label=t(f"{prefix}.form.description"),
            hint_text=t(f"{prefix}.form.description_hint"),
            multiline=True,
            max_length=1000,
        )

        self._type_field = DropdownField(
            label=t(f"{prefix}.form.type") + " *",
            options=[
                {"label": t("articles.types.article"), "value": "article"},
                {"label": t("articles.types.nomenclature"), "value": "nomenclature"},
            ],
            required=True,
            on_change=self._on_type_change,
        )
        
        # Campo de tipo como texto estático (para modo edición)
        self._type_text = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        t(f"{prefix}.form.type"),
                        size=12,
                        color=ft.Colors.with_opacity(0.6, ft.Colors.ON_SURFACE),
                    ),
                    ft.Text(
                        "",  # Se llenará dinámicamente
                        size=16,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                spacing=4,
            ),
            padding=ft.padding.only(left=12, top=8, bottom=8),
            visible=False,  # Oculto por defecto
        )

        # Campo de unidad (opcional - no está en el modelo actual)
        self._unit_field = DropdownField(
            label=t(f"{prefix}.form.unit"),
            options=[],
            required=False,
        )

        # Campos de clasificación (opcionales)
        self._family_type_field = DropdownField(
            label=t(f"{prefix}.form.family_type"),
            options=[],
        )

        self._matter_field = DropdownField(
            label=t(f"{prefix}.form.matter"),
            options=[],
        )

        # Campos de precios
        self._cost_price_field = ValidatedTextField(
            label=t(f"{prefix}.form.cost_price"),
            hint_text="0.00",
            prefix_icon=ft.Icons.ATTACH_MONEY,
            validators=["numeric"],
        )

        self._sale_price_field = ValidatedTextField(
            label=t(f"{prefix}.form.sale_price"),
            hint_text="0.00",
            prefix_icon=ft.Icons.SELL,
            validators=["numeric"],
        )

        # Campos de stock (solo para ARTICLE)
        self._stock_quantity_field = ValidatedTextField(
            label=t(f"{prefix}.form.stock_quantity"),
            hint_text="0.000",
            prefix_icon=ft.Icons.INVENTORY,
            validators=["numeric"],
        )

        self._min_stock_field = ValidatedTextField(
            label=t(f"{prefix}.form.min_stock"),
            hint_text="0.000",
            prefix_icon=ft.Icons.TRENDING_DOWN,
            validators=["numeric"],
        )

        # Contenedor de campos de stock (se oculta/muestra según el tipo)
        self._stock_section = ft.Container(
            content=BaseCard(
                title=t(f"{prefix}.form.stock_section"),
                icon=ft.Icons.WAREHOUSE,
                content=ft.Column(
                    controls=[
                        self._stock_quantity_field,
                        self._min_stock_field,
                    ],
                    spacing=LayoutConstants.SPACING_MD,
                ),
            ),
            visible=True,  # Por defecto visible para ARTICLE
        )

        self._is_active_switch = ft.Switch(
            label=t(f"{prefix}.form.is_active"),
            value=True,
        )

        # Sección BOM (se muestra solo si es nomenclatura)
        # Contenedor para las filas de componentes
        self._bom_components_container = ft.Column(
            controls=[],
            spacing=LayoutConstants.SPACING_SM,
        )
        
        # Botón para agregar componentes
        self._add_component_button = ft.ElevatedButton(
            text=t(f"{prefix}.form.add_component"),
            icon=ft.Icons.ADD,
            on_click=self._on_add_component,
        )
        
        self._bom_section = ft.Container(
            content=BaseCard(
                title=t(f"{prefix}.form.bom_section"),
                icon=ft.Icons.LIST_ALT,
                content=ft.Column(
                    controls=[
                        self._bom_components_container,
                        self._add_component_button,
                    ],
                    spacing=LayoutConstants.SPACING_MD,
                ),
            ),
            visible=False,
        )

        # Botón de datos ficticios (solo en modo creación)
        self._fake_data_button = ft.IconButton(
            icon=ft.Icons.CASINO,
            tooltip="Generar datos ficticios",
            on_click=self._on_generate_fake_data,
            visible=self.product_id is None,  # Solo visible en creación
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
        is_edit = self.product_id is not None

        # Determinar claves de traducción según el modo
        if self._is_nomenclatures:
            title_key = "nomenclatures.edit_title" if is_edit else "nomenclatures.create_title"
        else:
            title_key = "articles.edit_title" if is_edit else "articles.create_title"

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
                    ft.Container(expand=True),  # Espaciador
                    self._fake_data_button,  # Botón de datos ficticios
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
        # Obtener prefijo de traducción
        prefix = self._get_translation_prefix()
        
        # Determinar si es modo edición
        is_edit = self.product_id is not None
        
        # Determinar qué campo de tipo mostrar
        type_control = self._type_text if is_edit else self._type_field
        
        # Sección información básica
        basic_section = BaseCard(
            title=t(f"{prefix}.form.basic_info"),
            icon=ft.Icons.INFO_OUTLINED,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(content=self._code_field, expand=True),
                            ft.Container(content=type_control, expand=True),
                        ],
                        spacing=LayoutConstants.SPACING_MD,
                    ),
                    self._name_field,
                    self._description_field,
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Sección clasificación
        classification_section = BaseCard(
            title=t(f"{prefix}.form.classification"),
            icon=ft.Icons.CATEGORY,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(content=self._family_type_field, expand=True),
                            ft.Container(content=self._matter_field, expand=True),
                        ],
                        spacing=LayoutConstants.SPACING_MD,
                    ),
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Sección precios
        pricing_section = BaseCard(
            title=t(f"{prefix}.form.pricing"),
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
            self._stock_section,
            self._bom_section,
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
            else:
                # Establecer tipo por defecto para creación
                self._type_field.set_value("article")
                self._update_visibility_for_type("article")

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

    async def _load_product_data(self) -> None:
        """Carga los datos del producto a editar."""
        if not self.product_id:
            return

        logger.debug(f"Loading product data for ID={self.product_id}")

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            self._product_data = await product_api.get_by_id(self.product_id)

            logger.success(f"Product data loaded: {self._product_data.get('reference')}")

        except Exception as e:
            logger.exception(f"Error loading product data: {e}")
            raise

    def _populate_form(self) -> None:
        """Pobla los campos del formulario con los datos cargados."""
        if not self._product_data:
            return

        logger.debug("Populating form fields with product data")

        # Campos básicos - mapear desde el API
        self._code_field.set_value(self._product_data.get("reference", ""))
        self._name_field.set_value(self._product_data.get("designation_es", ""))
        self._description_field.set_value(self._product_data.get("short_designation", ""))

        # Tipo de producto
        product_type = self._product_data.get("product_type", "ARTICLE")
        self._type_field.set_value(product_type)
        
        # Actualizar el texto estático del tipo (para modo edición)
        type_label = t("articles.types.article") if product_type == "article" else t("articles.types.nomenclature")
        if self._type_text.content and len(self._type_text.content.controls) > 1:
            self._type_text.content.controls[1].value = type_label
        
        self._update_visibility_for_type(product_type)

        # Clasificación
        family_type_id = self._product_data.get("family_type_id")
        if family_type_id:
            self._family_type_field.set_value(str(family_type_id))

        matter_id = self._product_data.get("matter_id")
        if matter_id:
            self._matter_field.set_value(str(matter_id))

        # Precios
        cost_price = self._product_data.get("cost_price")
        if cost_price is not None:
            self._cost_price_field.set_value(str(cost_price))

        sale_price = self._product_data.get("sale_price")
        if sale_price is not None:
            self._sale_price_field.set_value(str(sale_price))

        # Stock
        stock_quantity = self._product_data.get("stock_quantity")
        if stock_quantity is not None:
            self._stock_quantity_field.set_value(str(stock_quantity))

        minimum_stock = self._product_data.get("minimum_stock")
        if minimum_stock is not None:
            self._min_stock_field.set_value(str(minimum_stock))

        # Estado
        self._is_active_switch.value = self._product_data.get("is_active", True)

        logger.success("Form fields populated successfully")

        # Actualizar la UI después de poblar los campos
        if self.page:
            self.update()

    def _on_type_change(self, value: str) -> None:
        """Callback cuando cambia el tipo de producto."""
        self._update_visibility_for_type(value)

    def _update_visibility_for_type(self, product_type: str) -> None:
        """Actualiza la visibilidad de secciones según el tipo."""
        is_nomenclature = product_type == "nomenclature"

        # Stock solo para article
        if self._stock_section:
            self._stock_section.visible = not is_nomenclature

        # BOM solo para nomenclature
        if self._bom_section:
            self._bom_section.visible = is_nomenclature

        if self.page:
            self.update()

    def _on_add_component(self, e: ft.ControlEvent) -> None:
        """Callback para agregar componente a BOM."""
        logger.info("Add component clicked")
        
        # TODO: Implementar ArticleSelectorDialog
        # Por ahora mostramos un mensaje al usuario
        if self.page:
            snackbar = ft.SnackBar(
                content=ft.Text("La funcionalidad de agregar componentes está en desarrollo"),
                bgcolor=ft.Colors.ORANGE,
                duration=3000,
            )
            self.page.overlay.append(snackbar)
            snackbar.open = True
            self.page.update()
        
        # # Obtener IDs de artículos ya agregados
        # excluded_ids = [comp.get("id") for comp in self._bom_components]
        # 
        # # Crear y mostrar diálogo de selección
        # dialog = ArticleSelectorDialog(
        #     on_select=self._on_article_selected,
        #     excluded_ids=excluded_ids,
        # )
        # 
        # if self.page:
        #     self.page.overlay.append(dialog)
        #     dialog.open = True
        #     self.page.update()
        #     
        #     # Cargar artículos
        #     self.page.run_task(dialog.load_articles)
    
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
        logger.debug("Validating product form")

        is_valid = True

        # Validar campos requeridos
        if not self._code_field.validate():
            is_valid = False

        if not self._name_field.validate():
            is_valid = False

        if not self._type_field.validate():
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
        product_type = self._type_field.get_value()

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

        # Obtener stock (solo para article)
        stock_quantity = None
        minimum_stock = None

        if product_type == "article":
            stock_str = self._stock_quantity_field.get_value()
            stock_quantity = float(stock_str) if stock_str else 0

            min_str = self._min_stock_field.get_value()
            minimum_stock = float(min_str) if min_str else None

        # Construir datos - usar nombres del schema ProductCreate
        data = {
            "reference": reference,
            "designation_es": designation_es,
            "product_type": product_type,
            "is_active": self._is_active_switch.value,
        }

        # Agregar campos opcionales solo si tienen valor
        if short_designation:
            data["short_designation"] = short_designation

        if cost_price is not None:
            data["cost_price"] = cost_price

        if sale_price is not None:
            data["sale_price"] = sale_price

        if stock_quantity is not None:
            data["stock_quantity"] = stock_quantity

        if minimum_stock is not None:
            data["minimum_stock"] = minimum_stock

        if family_type_id:
            data["family_type_id"] = family_type_id

        if matter_id:
            data["matter_id"] = matter_id
        
        # Agregar componentes si es nomenclatura
        if product_type == "nomenclature" and self._bom_components:
            data["components"] = [
                {
                    "component_id": comp["id"],
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
        """Maneja el guardado del producto."""
        logger.info("Handling product save")
        
        # Obtener prefijo de traducción
        prefix = self._get_translation_prefix()

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

            if self.product_id:
                # Actualizar producto existente
                logger.debug(f"Updating product ID={self.product_id}")
                updated_product = await product_api.update(self.product_id, form_data)
                logger.success(f"Product updated: {updated_product.get('reference')}")
                
                # TODO: Actualizar componentes (requiere lógica adicional para comparar y actualizar)
                
                message = t(f"{prefix}.messages.updated").format(
                    name=updated_product.get("designation_es", updated_product.get("reference", ""))
                )
            else:
                # Crear nuevo producto
                logger.debug("Creating new product")
                new_product = await product_api.create(form_data)
                logger.success(f"Product created: {new_product.get('reference')}")
                updated_product = new_product
                
                # Agregar componentes si es nomenclatura
                if components_data and updated_product.get("product_type") == "nomenclature":
                    product_id = updated_product.get("id")
                    logger.info(f"Adding {len(components_data)} components to product {product_id}")
                    
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
                            # Continuar con los demás componentes
                    
                    logger.success(f"Components added to product {product_id}")
                
                message = t(f"{prefix}.messages.created").format(
                    name=new_product.get("designation_es", new_product.get("reference", ""))
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

    def _on_generate_fake_data(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en generar datos ficticios."""
        logger.info("Generate fake data clicked")
        
        try:
            # Determinar qué tipo de datos generar según el tipo actual del formulario
            current_type = self._type_field.get_value() if hasattr(self, '_type_field') else "article"
            
            if current_type == "nomenclature":
                # Usar el generador de nomenclatura
                FakeDataGenerator.populate_nomenclature_form(self)
            else:
                # Usar el generador de artículo
                FakeDataGenerator.populate_article_form(self)
            
            # Mostrar mensaje de éxito
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text("Datos ficticios generados exitosamente"),
                    bgcolor=ft.Colors.GREEN,
                    duration=2000,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()
                
        except Exception as ex:
            logger.exception(f"Error generating fake data: {ex}")
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(f"Error al generar datos: {str(ex)}"),
                    bgcolor=ft.Colors.RED,
                    duration=3000,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        logger.debug("State changed, updating ProductFormView")
        if self.page:
            self.update()
