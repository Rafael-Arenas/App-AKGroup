"""
Vista de formulario para crear/editar artículos.

Permite crear nuevos artículos o editar existentes.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import BaseCard, LoadingSpinner, ErrorDisplay
from src.frontend.components.forms import ValidatedTextField, DropdownField
from src.frontend.i18n.translation_manager import t


class ArticleFormView(ft.Column):
    """
    Vista de formulario para crear/editar artículos.

    Args:
        article_id: ID del artículo a editar (None para crear nuevo)
        on_save: Callback cuando se guarda exitosamente
        on_cancel: Callback cuando se cancela

    Example:
        >>> form = ArticleFormView(article_id=123, on_save=handle_save)
        >>> page.add(form)
    """

    def __init__(
        self,
        article_id: int | None = None,
        on_save: Callable[[dict], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
    ):
        """Inicializa el formulario de artículo."""
        super().__init__()
        self.article_id = article_id
        self.on_save_callback = on_save
        self.on_cancel_callback = on_cancel

        # Estado
        self._is_loading: bool = True
        self._is_saving: bool = False
        self._error_message: str = ""
        self._article_data: dict | None = None

        # Lookups
        self._units: list[dict] = []
        self._family_types: list[dict] = []
        self._matters: list[dict] = []
        self._sales_types: list[dict] = []
        self._companies: list[dict] = []

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

        logger.info(f"ArticleFormView initialized: article_id={article_id}")

    def _build_components(self) -> None:
        """Crea los componentes del formulario."""
        # Campos de información básica
        self._code_field = ValidatedTextField(
            label="Referencia *",
            hint_text="Referencia del artículo",
            required=True,
            prefix_icon=ft.Icons.TAG,
            max_length=50,
        )

        self._name_field = ValidatedTextField(
            label="Designación (ES) *",
            hint_text="Nombre del artículo en español",
            required=True,
            prefix_icon=ft.Icons.INVENTORY_2,
            max_length=200,
        )

        self._description_field = ValidatedTextField(
            label=t("articles.form.description"),
            hint_text=t("articles.form.description_hint"),
            multiline=True,
            max_length=1000,
        )

        # Campo de unidad
        self._unit_field = DropdownField(
            label=t("articles.form.unit"),
            options=[],
            required=False,
        )

        # Campos de clasificación (opcionales)
        self._family_type_field = DropdownField(
            label=t("articles.form.family_type"),
            options=[],
        )

        self._matter_field = DropdownField(
            label=t("articles.form.matter"),
            options=[],
        )

        # Campos de precios
        self._cost_price_field = ValidatedTextField(
            label=t("articles.form.cost_price"),
            hint_text="0.00",
            prefix_icon=ft.Icons.ATTACH_MONEY,
            validators=["numeric"],
        )

        self._sale_price_field = ValidatedTextField(
            label=t("articles.form.sale_price"),
            hint_text="0.00",
            prefix_icon=ft.Icons.SELL,
            validators=["numeric"],
        )

        # Campos de stock
        self._stock_quantity_field = ValidatedTextField(
            label=t("articles.form.stock_quantity"),
            hint_text="0.000",
            prefix_icon=ft.Icons.INVENTORY,
            validators=["numeric"],
        )

        self._min_stock_field = ValidatedTextField(
            label=t("articles.form.min_stock"),
            hint_text="0.000",
            prefix_icon=ft.Icons.TRENDING_DOWN,
            validators=["numeric"],
        )

        # Campos adicionales de precios
        self._purchase_price_field = ValidatedTextField(
            label="Precio de compra",
            hint_text="0.00",
            prefix_icon=ft.Icons.SHOPPING_CART,
            validators=["numeric"],
        )

        self._sale_price_eur_field = ValidatedTextField(
            label="Precio en euros",
            hint_text="0.00",
            prefix_icon=ft.Icons.EURO,
            validators=["numeric"],
        )

        # Campos de stock adicionales
        self._stock_location_field = ValidatedTextField(
            label="Ubicación en almacén",
            hint_text="Ej: A-01-03",
            prefix_icon=ft.Icons.LOCATION_ON,
            max_length=100,
        )

        # Campos de dimensiones y peso
        self._net_weight_field = ValidatedTextField(
            label="Peso neto (kg)",
            hint_text="0.000",
            prefix_icon=ft.Icons.FITNESS_CENTER,
            validators=["numeric"],
        )

        self._gross_weight_field = ValidatedTextField(
            label="Peso bruto (kg)",
            hint_text="0.000",
            prefix_icon=ft.Icons.MONITOR_WEIGHT,
            validators=["numeric"],
        )

        self._length_field = ValidatedTextField(
            label="Longitud (mm)",
            hint_text="0.000",
            prefix_icon=ft.Icons.STRAIGHTEN,
            validators=["numeric"],
        )

        self._width_field = ValidatedTextField(
            label="Ancho (mm)",
            hint_text="0.000",
            prefix_icon=ft.Icons.SQUARE_FOOT,
            validators=["numeric"],
        )

        self._height_field = ValidatedTextField(
            label="Altura (mm)",
            hint_text="0.000",
            prefix_icon=ft.Icons.VERTICAL_ALIGN_TOP,
            validators=["numeric"],
        )

        self._volume_field = ValidatedTextField(
            label="Volumen (m³)",
            hint_text="0.000000",
            prefix_icon=ft.Icons.VIEW_IN_AR,
            validators=["numeric"],
        )

        # Campos de logística y aduanas

        self._country_of_origin_field = DropdownField(
            label="País de origen",
            options=[],
        )

        # Campos de proveedor
        self._supplier_reference_field = ValidatedTextField(
            label="Referencia del proveedor",
            hint_text="Referencia interna del proveedor",
            prefix_icon=ft.Icons.NUMBERS,
            max_length=100,
        )

        self._customs_number_field = ValidatedTextField(
            label="Número de aduana",
            hint_text="Número de identificación de aduanas",
            prefix_icon=ft.Icons.LOCAL_SHIPPING,
            max_length=50,
        )

        # Campos adicionales
        self._sales_type_field = DropdownField(
            label="Tipo de venta",
            options=[],
        )

        self._company_field = DropdownField(
            label="Proveedor",
            options=[],
        )

        self._designation_fr_field = ValidatedTextField(
            label="Nombre en francés",
            hint_text="Designation en français",
            prefix_icon=ft.Icons.TRANSLATE,
            max_length=200,
        )

        self._designation_en_field = ValidatedTextField(
            label="Nombre en inglés",
            hint_text="Designation in English",
            prefix_icon=ft.Icons.TRANSLATE,
            max_length=200,
        )

        self._revision_field = ValidatedTextField(
            label="Revisión",
            hint_text="Ej: A, B, 1.0",
            prefix_icon=ft.Icons.UPDATE,
            max_length=20,
        )

        self._notes_field = ValidatedTextField(
            label="Notas adicionales",
            hint_text="Notas o comentarios importantes",
            multiline=True,
            max_length=2000,
        )

        self._is_active_switch = ft.Switch(
            label=t("articles.form.is_active"),
            value=True,
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
        is_edit = self.article_id is not None
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
        logger.info("ArticleFormView mounted, loading form data")

        # Cargar datos del formulario
        if self.page:
            self.page.run_task(self._load_form_data)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        logger.info("ArticleFormView unmounting")
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
            title=t("articles.form.basic_info"),
            icon=ft.Icons.INFO_OUTLINED,
            content=ft.Column(
                controls=[
                    self._code_field,
                    self._supplier_reference_field,
                    self._revision_field,
                    self._name_field,
                    self._description_field,
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Sección clasificación
        classification_section = BaseCard(
            title=t("articles.form.classification"),
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
            title=t("articles.form.pricing"),
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
                    ft.Row(
                        controls=[
                            ft.Container(content=self._purchase_price_field, expand=True),
                            ft.Container(content=self._sale_price_eur_field, expand=True),
                        ],
                        spacing=LayoutConstants.SPACING_MD,
                    ),
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Sección stock
        stock_section = BaseCard(
            title=t("articles.form.stock_section"),
            icon=ft.Icons.WAREHOUSE,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(content=self._stock_quantity_field, expand=True),
                            ft.Container(content=self._min_stock_field, expand=True),
                        ],
                        spacing=LayoutConstants.SPACING_MD,
                    ),
                    self._stock_location_field,
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Sección dimensiones y peso
        dimensions_section = BaseCard(
            title="Dimensiones y Peso",
            icon=ft.Icons.SCALE,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(content=self._net_weight_field, expand=True),
                            ft.Container(content=self._gross_weight_field, expand=True),
                        ],
                        spacing=LayoutConstants.SPACING_MD,
                    ),
                    ft.Row(
                        controls=[
                            ft.Container(content=self._length_field, expand=True),
                            ft.Container(content=self._width_field, expand=True),
                            ft.Container(content=self._height_field, expand=True),
                        ],
                        spacing=LayoutConstants.SPACING_MD,
                    ),
                    self._volume_field,
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Sección logística y aduanas
        logistics_section = BaseCard(
            title="Logística y Aduanas",
            icon=ft.Icons.LOCAL_SHIPPING,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(content=self._country_of_origin_field, expand=True),
                            ft.Container(content=self._customs_number_field, expand=True),
                        ],
                        spacing=LayoutConstants.SPACING_MD,
                    ),
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Sección adicional
        additional_section = BaseCard(
            title="Información Adicional",
            icon=ft.Icons.INFO,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(content=self._sales_type_field, expand=True),
                            ft.Container(content=self._company_field, expand=True),
                        ],
                        spacing=LayoutConstants.SPACING_MD,
                    ),
                    ft.Row(
                        controls=[
                            ft.Container(content=self._designation_fr_field, expand=True),
                            ft.Container(content=self._designation_en_field, expand=True),
                        ],
                        spacing=LayoutConstants.SPACING_MD,
                    ),
                    self._notes_field,
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
            stock_section,
            dimensions_section,
            logistics_section,
            additional_section,
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

            # Si es edición, cargar datos del artículo
            if self.article_id:
                await self._load_article_data()

            self._is_loading = False
            self._error_message = ""

            # Construir el formulario
            self._build_form()

            # Poblar los campos si es edición
            if self.article_id and self._article_data:
                self._populate_form()

        except Exception as e:
            logger.exception(f"Error loading form data: {e}")
            self._error_message = f"Error al cargar datos: {str(e)}"
            self._is_loading = False
            self._show_error()

    async def _load_lookups(self) -> None:
        """Carga los datos de lookups."""
        logger.debug("Loading lookups for article form")

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

            # Cargar tipos de venta
            try:
                self._sales_types = await lookup_api.get_lookup("sales_types")
                sales_type_options = [
                    {"label": st.get("name", ""), "value": str(st["id"])}
                    for st in self._sales_types
                ]
                self._sales_type_field.set_options(sales_type_options)
            except Exception as e:
                logger.warning(f"Could not load sales_types: {e}")
                self._sales_types = []

            # Cargar empresas (proveedores)
            try:
                # Primero obtener los tipos de empresa para encontrar el ID de "Proveedor"
                company_types = await lookup_api.get_lookup("company_types")
                supplier_type_id = None
                for ct in company_types:
                    if "prove" in ct.get("name", "").lower() or "supplier" in ct.get("name", "").lower():
                        supplier_type_id = ct["id"]
                        break
                
                # Cargar solo empresas proveedoras y activas
                if supplier_type_id:
                    self._companies = await lookup_api.get_companies(
                        company_type_id=supplier_type_id, 
                        is_active=True
                    )
                else:
                    # Si no se encuentra el tipo, cargar todas las activas
                    self._companies = await lookup_api.get_companies(is_active=True)
                    logger.warning("No se encontró el tipo de empresa 'Proveedor', cargando todas las empresas activas")
                
                company_options = [
                    {"label": c.get("name", ""), "value": str(c["id"])}
                    for c in self._companies
                ]
                self._company_field.set_options(company_options)
            except Exception as e:
                logger.warning(f"Could not load companies: {e}")
                self._companies = []

            # Cargar países
            try:
                countries = await lookup_api.get_lookup("countries")
                country_options = [
                    {"label": c.get("name", ""), "value": c.get("code", "")}
                    for c in countries
                ]
                self._country_of_origin_field.set_options(country_options)
            except Exception as e:
                logger.warning(f"Could not load countries: {e}")

            logger.success(
                f"Lookups loaded: {len(self._units)} units, "
                f"{len(self._family_types)} families, {len(self._matters)} matters, "
                f"{len(self._sales_types)} sales types, {len(self._companies)} companies"
            )

        except Exception as e:
            logger.exception(f"Error loading lookups: {e}")
            raise

    async def _load_article_data(self) -> None:
        """Carga los datos del artículo a editar."""
        logger.info(f"Loading article data: ID={self.article_id}")

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            self._article_data = await product_api.get_by_id(self.article_id)

            logger.success(f"Article data loaded: {self._article_data.get('reference')}")

        except Exception as e:
            logger.exception(f"Error loading article data: {e}")
            raise

    def _populate_form(self) -> None:
        """Rellena los campos del formulario con los datos del artículo."""
        if not self._article_data:
            return

        logger.debug("Populating form fields with article data")

        # Campos básicos
        self._code_field.set_value(self._article_data.get("reference", ""))
        self._name_field.set_value(self._article_data.get("designation_es", ""))
        self._description_field.set_value(self._article_data.get("short_designation", ""))

        # Clasificación
        family_type_id = self._article_data.get("family_type_id")
        if family_type_id:
            self._family_type_field.set_value(str(family_type_id))

        matter_id = self._article_data.get("matter_id")
        if matter_id:
            self._matter_field.set_value(str(matter_id))

        # Precios
        cost_price = self._article_data.get("cost_price")
        if cost_price is not None:
            self._cost_price_field.set_value(str(cost_price))

        sale_price = self._article_data.get("sale_price")
        if sale_price is not None:
            self._sale_price_field.set_value(str(sale_price))

        # Stock
        stock_quantity = self._article_data.get("stock_quantity")
        if stock_quantity is not None:
            self._stock_quantity_field.set_value(str(stock_quantity))

        minimum_stock = self._article_data.get("minimum_stock")
        if minimum_stock is not None:
            self._min_stock_field.set_value(str(minimum_stock))

        # Estado
        self._is_active_switch.value = self._article_data.get("is_active", True)

        # Campos adicionales de precios
        purchase_price = self._article_data.get("purchase_price")
        if purchase_price is not None:
            self._purchase_price_field.set_value(str(purchase_price))

        sale_price_eur = self._article_data.get("sale_price_eur")
        if sale_price_eur is not None:
            self._sale_price_eur_field.set_value(str(sale_price_eur))

        # Campos de stock adicionales
        self._stock_location_field.set_value(self._article_data.get("stock_location", ""))

        # Campos de dimensiones y peso
        net_weight = self._article_data.get("net_weight")
        if net_weight is not None:
            self._net_weight_field.set_value(str(net_weight))

        gross_weight = self._article_data.get("gross_weight")
        if gross_weight is not None:
            self._gross_weight_field.set_value(str(gross_weight))

        length = self._article_data.get("length")
        if length is not None:
            self._length_field.set_value(str(length))

        width = self._article_data.get("width")
        if width is not None:
            self._width_field.set_value(str(width))

        height = self._article_data.get("height")
        if height is not None:
            self._height_field.set_value(str(height))

        volume = self._article_data.get("volume")
        if volume is not None:
            self._volume_field.set_value(str(volume))

        # Campos de logística y aduanas
        self._country_of_origin_field.set_value(self._article_data.get("country_of_origin", ""))
        self._supplier_reference_field.set_value(self._article_data.get("supplier_reference", ""))
        self._customs_number_field.set_value(self._article_data.get("customs_number", ""))

        # Campos adicionales
        sales_type_id = self._article_data.get("sales_type_id")
        if sales_type_id:
            self._sales_type_field.set_value(str(sales_type_id))

        company_id = self._article_data.get("company_id")
        if company_id:
            self._company_field.set_value(str(company_id))

        self._designation_fr_field.set_value(self._article_data.get("designation_fr", ""))
        self._designation_en_field.set_value(self._article_data.get("designation_en", ""))
        self._revision_field.set_value(self._article_data.get("revision", ""))
        self._notes_field.set_value(self._article_data.get("notes", ""))

        logger.success("Form fields populated successfully")

        # Actualizar la UI después de poblar los campos
        if self.page:
            self.update()

    def _validate_form(self) -> bool:
        """Valida todos los campos del formulario."""
        logger.debug("Validating article form")

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

        # Obtener stock
        stock_str = self._stock_quantity_field.get_value()
        stock_quantity = float(stock_str) if stock_str else 0

        min_str = self._min_stock_field.get_value()
        minimum_stock = float(min_str) if min_str else None

        # Construir datos - usar nombres del schema ProductCreate
        data = {
            "reference": reference,
            "designation_es": designation_es,
            "product_type": "article",  # Siempre artículo en esta vista
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

        # Campos adicionales de precios
        purchase_price_str = self._purchase_price_field.get_value()
        if purchase_price_str:
            data["purchase_price"] = float(purchase_price_str)

        sale_price_eur_str = self._sale_price_eur_field.get_value()
        if sale_price_eur_str:
            data["sale_price_eur"] = float(sale_price_eur_str)

        # Campos de stock adicionales
        stock_location = self._stock_location_field.get_value()
        if stock_location:
            data["stock_location"] = stock_location

        # Campos de dimensiones y peso
        net_weight_str = self._net_weight_field.get_value()
        if net_weight_str:
            data["net_weight"] = float(net_weight_str)

        gross_weight_str = self._gross_weight_field.get_value()
        if gross_weight_str:
            data["gross_weight"] = float(gross_weight_str)

        length_str = self._length_field.get_value()
        if length_str:
            data["length"] = float(length_str)

        width_str = self._width_field.get_value()
        if width_str:
            data["width"] = float(width_str)

        height_str = self._height_field.get_value()
        if height_str:
            data["height"] = float(height_str)

        volume_str = self._volume_field.get_value()
        if volume_str:
            data["volume"] = float(volume_str)

        # Campos de logística y aduanas
        country_of_origin = self._country_of_origin_field.get_value()
        if country_of_origin:
            data["country_of_origin"] = country_of_origin

        supplier_reference = self._supplier_reference_field.get_value()
        if supplier_reference:
            data["supplier_reference"] = supplier_reference

        customs_number = self._customs_number_field.get_value()
        if customs_number:
            data["customs_number"] = customs_number

        # Campos adicionales
        sales_type_value = self._sales_type_field.get_value()
        if sales_type_value:
            data["sales_type_id"] = int(sales_type_value)

        company_value = self._company_field.get_value()
        if company_value:
            data["company_id"] = int(company_value)

        designation_fr = self._designation_fr_field.get_value()
        if designation_fr:
            data["designation_fr"] = designation_fr

        designation_en = self._designation_en_field.get_value()
        if designation_en:
            data["designation_en"] = designation_en

        revision = self._revision_field.get_value()
        if revision:
            data["revision"] = revision

        notes = self._notes_field.get_value()
        if notes:
            data["notes"] = notes

        return data

    def _on_save_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en guardar."""
        logger.info("Save button clicked")

        if self.page:
            self.page.run_task(self.handle_save)

    async def handle_save(self) -> None:
        """Maneja el guardado del artículo."""
        logger.info("Handling article save")

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

            if self.article_id:
                # Actualizar artículo existente
                logger.debug(f"Updating article ID={self.article_id}")
                updated_article = await product_api.update(self.article_id, form_data)
                logger.success(f"Article updated: {updated_article.get('reference')}")

                message = t("articles.messages.updated").format(
                    name=updated_article.get("designation_es", updated_article.get("reference", ""))
                )
            else:
                # Crear nuevo artículo
                logger.debug("Creating new article")
                new_article = await product_api.create(form_data)
                logger.success(f"Article created: {new_article.get('reference')}")
                updated_article = new_article

                message = t("articles.messages.created").format(
                    name=new_article.get("designation_es", new_article.get("reference", ""))
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
                self.on_save_callback(updated_article)

        except Exception as e:
            logger.exception(f"Error saving article: {e}")

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
        logger.debug("ArticleFormView state changed, rebuilding content")
        # Reconstruir los componentes del formulario con nuevas traducciones
        self._build_components()
        # Reconstruir el contenido del formulario
        self._build_form()
        # Reconstruir el layout principal
        self.controls = self._build_layout()
        if self.page:
            self.update()
