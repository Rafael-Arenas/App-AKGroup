"""
Vista para agregar productos (artículos y nomenclaturas) a una cotización.

Permite seleccionar entre artículos y nomenclaturas, buscar productos y agregarlos a la cotización.
"""
from typing import Callable
from decimal import Decimal
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t
from src.frontend.components.common import (
    BaseCard,
    LoadingSpinner,
    ErrorDisplay,
    DataTable,
    EmptyState,
)
from src.frontend.components.forms import ValidatedTextField


class QuoteProductsView(ft.Column):
    """
    Vista para agregar productos a una cotización.

    Args:
        quote_id: ID de la cotización
        company_id: ID de la empresa (para navegación)
        company_type: Tipo de empresa (para navegación)
        on_back: Callback para volver atrás
        on_product_added: Callback cuando se agrega un producto

    Example:
        >>> view = QuoteProductsView(quote_id=123, company_id=1, on_back=handle_back)
        >>> page.add(view)
    """

    def __init__(
        self,
        quote_id: int,
        company_id: int,
        company_type: str,
        on_back: Callable[[], None] | None = None,
        on_product_added: Callable[[], None] | None = None,
    ):
        """Inicializa la vista de productos de cotización."""
        super().__init__()
        
        self.quote_id = quote_id
        self.company_id = company_id
        self.company_type = company_type
        self.on_back = on_back
        self.on_product_added = on_product_added

        self._is_loading: bool = False
        self._error_message: str = ""
        self._product_type: str = "article"  # "article" o "nomenclature"
        self._products: list[dict] = []
        self._selected_product: dict | None = None
        self._search_query: str = ""
        self._selected_products: list[dict] = []  # Lista de productos seleccionados para agregar

        # Componentes de formulario
        self._search_field: ft.TextField | None = None
        self._products_table: DataTable | None = None
        self._selected_products_table: DataTable | None = None
        self._details_form: ft.Column | None = None
        self._quantity_field: ValidatedTextField | None = None
        self._unit_price_field: ValidatedTextField | None = None
        self._discount_field: ValidatedTextField | None = None
        self._notes_field: ft.TextField | None = None
        self._article_button: ft.Button | None = None
        self._nomenclature_button: ft.Button | None = None

        # Configurar propiedades de la columna
        self.expand = True
        self.spacing = LayoutConstants.SPACING_LG
        self.scroll = ft.ScrollMode.AUTO

        # Construir contenido inicial
        self.controls = [self.build()]

        logger.info(f"QuoteProductsView initialized: quote_id={quote_id}")

    def build(self) -> ft.Container:
        """Construye el componente de vista de productos."""
        # Contenedores para actualización dinámica con estado inicial
        self._products_container = ft.Column(
            controls=[LoadingSpinner(message="Cargando productos...")],
            expand=True
        )
        self._details_container = ft.Column()
        self._selected_container = ft.Column(
            controls=[
                EmptyState(
                    icon=ft.Icons.SHOPPING_CART_OUTLINED,
                    title="Sin productos",
                    message="Selecciona productos para agregarlos",
                )
            ],
            expand=True
        )

        # Header
        header = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip=t("common.back"),
                    on_click=self._on_back_click,
                ),
                ft.Icon(ft.Icons.ADD_SHOPPING_CART, size=LayoutConstants.ICON_SIZE_XL),
                ft.Text(
                    t("quotes.add_products"),
                    size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        # Selector de tipo de producto
        self._article_button = ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.INVENTORY_2, color=ft.Colors.WHITE if self._product_type == "article" else None),
                    ft.Text(t("articles.types.article"), color=ft.Colors.WHITE if self._product_type == "article" else None),
                ],
                spacing=8,
            ),
            on_click=lambda e: self._on_product_type_click("article"),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY if self._product_type == "article" else ft.Colors.GREY_300,
            ),
        )
        
        self._nomenclature_button = ft.Button(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.LIST_ALT, color=ft.Colors.WHITE if self._product_type == "nomenclature" else None),
                    ft.Text(t("articles.types.nomenclature"), color=ft.Colors.WHITE if self._product_type == "nomenclature" else None),
                ],
                spacing=8,
            ),
            on_click=lambda e: self._on_product_type_click("nomenclature"),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.PRIMARY if self._product_type == "nomenclature" else ft.Colors.GREY_300,
            ),
        )
        
        product_type_selector = ft.Row(
            controls=[
                ft.Text(
                    f"{t('articles.form.type')}:",
                    size=LayoutConstants.FONT_SIZE_LG,
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                ),
                ft.Container(width=20),
                self._article_button,
                self._nomenclature_button,
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        # Buscador
        self._search_field = ft.TextField(
            label=t("common.search"),
            hint_text=t("articles.search_placeholder"),
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search_change,
            on_submit=self._on_search_submit,
            expand=True,
        )

        search_row = ft.Row(
            controls=[
                self._search_field,
                ft.Button(
                    content=ft.Text(t("common.search")),
                    icon=ft.Icons.SEARCH,
                    on_click=self._on_search_click,
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        # Tabla de productos
        self._products_table = DataTable(
            columns=[
                {"key": "reference", "label": "articles.columns.code", "sortable": True},
                {"key": "designation", "label": "articles.columns.name", "sortable": True},
                {"key": "family", "label": "articles.form.family_type", "sortable": True},
                {"key": "actions", "label": "common.actions", "sortable": False},
            ],
            page_size=10,
            on_row_click=self._on_product_select,
        )

        # Formulario de detalles
        self._quantity_field = ValidatedTextField(
            label=t("articles.form.quantity"),
            hint_text=t("articles.form.quantity"),
            required=True,
        )

        self._unit_price_field = ValidatedTextField(
            label=t("quotes.products_table.unit_price"),
            hint_text="0.00",
            required=True,
        )

        self._discount_field = ValidatedTextField(
            label=t("quotes.products_table.discount"),
            hint_text="0",
            required=False,
        )

        self._notes_field = ft.TextField(
            label=t("quotes.fields.notes"),
            hint_text=t("quotes.fields.notes"),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )

        self._details_form = ft.Column(
            controls=[
                ft.Text(
                    t("quotes.products_table.product"),
                    size=LayoutConstants.FONT_SIZE_LG,
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                ),
                ft.Divider(),
                self._quantity_field,
                self._unit_price_field,
                self._discount_field,
                self._notes_field,
                ft.Row(
                    controls=[
                        ft.Button(
                            content=ft.Text(t("common.cancel")),
                            on_click=self._on_cancel_click,
                        ),
                        ft.Button(
                            content=ft.Text(t("common.add")),
                            icon=ft.Icons.ADD,
                            on_click=self._on_add_product_click,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                    spacing=LayoutConstants.SPACING_SM,
                ),
            ],
            spacing=LayoutConstants.SPACING_MD,
            visible=False,
        )

        # Tabla de seleccionados
        self._selected_products_table = DataTable(
            columns=[
                {"key": "reference", "label": "articles.columns.code", "sortable": False},
                {"key": "designation", "label": "articles.columns.name", "sortable": False},
                {"key": "quantity", "label": "articles.form.quantity", "sortable": False},
                {"key": "unit_price", "label": "quotes.products_table.unit_price", "sortable": False},
                {"key": "actions", "label": "common.actions", "sortable": False},
            ],
            page_size=10,
            on_row_click=self._on_remove_selected_product,
        )

        # Cards
        products_card = BaseCard(
            title=t("articles.title"),
            icon=ft.Icons.INVENTORY_2,
            content=ft.Column(
                controls=[
                    search_row,
                    ft.Divider(),
                    self._products_container,
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        details_card = BaseCard(
            title=t("common.edit"),
            icon=ft.Icons.EDIT,
            content=self._details_container,
        )
        self._details_container.controls = [self._details_form]

        selected_card = BaseCard(
            title=t("quotes.sections.products"),
            icon=ft.Icons.SHOPPING_CART,
            content=self._selected_container,
        )

        # Layout principal (envuelto en Container para padding)
        content = ft.Container(
            content=ft.Column(
                controls=[
                    header,
                    product_type_selector,
                    ft.Row(
                        controls=[
                            ft.Container(content=products_card, expand=2),
                            ft.Container(content=details_card, expand=1),
                            ft.Container(content=selected_card, expand=2),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                        expand=True,
                        spacing=LayoutConstants.SPACING_LG,
                    ),
                ],
                spacing=LayoutConstants.SPACING_LG,
                expand=True,
            ),
            padding=LayoutConstants.PADDING_LG,
            expand=True,
        )

        return content

    def _update_products_ui(self) -> None:
        """Actualiza la sección de productos disponibles."""
        if not hasattr(self, "_products_container"):
            return

        self._products_container.controls.clear()

        if self._is_loading:
            self._products_container.controls.append(
                LoadingSpinner(message="Cargando productos...")
            )
        elif self._error_message:
            self._products_container.controls.append(
                ErrorDisplay(message=self._error_message)
            )
        elif not self._products:
            self._products_container.controls.append(
                EmptyState(
                    icon=ft.Icons.INVENTORY_2,
                    title="Sin productos",
                    message=f"No hay {self._product_type}s disponibles",
                )
            )
        else:
            formatted_products = []
            for p in self._products:
                formatted_products.append({
                    "id": p.get("id"),
                    "reference": p.get("reference", ""),
                    "designation": p.get("designation_es") or p.get("name") or p.get("short_designation", "-"),
                    "family": p.get("family_type", {}).get("name", "-") if isinstance(p.get("family_type"), dict) else "-",
                    "actions": t("common.select"),
                    "_raw": p,
                })
            
            # Actualizar datos de la tabla
            self._products_table.set_data(formatted_products, total=len(formatted_products))
            
            # ASEGURAR que la tabla esté en los controles del contenedor
            self._products_container.controls.append(self._products_table)

    def _update_selected_ui(self) -> None:
        """Actualiza la sección de productos seleccionados."""
        if not hasattr(self, "_selected_container"):
            return

        self._selected_container.controls.clear()

        if not self._selected_products:
            self._selected_container.controls.append(
                EmptyState(
                    icon=ft.Icons.SHOPPING_CART_OUTLINED,
                    title="Sin productos",
                    message="Selecciona productos para agregarlos",
                )
            )
        else:
            formatted_selected = []
            for item in self._selected_products:
                formatted_selected.append({
                    "id": item["product_id"],
                    "reference": item["reference"],
                    "designation": item["designation"],
                    "quantity": f"{item['quantity']:.2f}",
                    "unit_price": f"${item['unit_price']:,.2f}",
                    "actions": t("common.remove"),
                    "_original": item,
                })
            self._selected_products_table.set_data(formatted_selected, total=len(formatted_selected))
            
            self._selected_container.controls.extend([
                self._selected_products_table,
                ft.Divider(),
                ft.Row(
                    controls=[
                        ft.Text(
                            f"Total: {len(self._selected_products)} {t('quotes.sections.products').lower()}",
                            size=LayoutConstants.FONT_SIZE_MD,
                            weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                        ),
                        ft.Button(
                            content=ft.Text(t("common.save")),
                            icon=ft.Icons.SAVE,
                            on_click=self._on_save_selection_click,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ])

    def did_mount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.info("QuoteProductsView mounted")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        
        # Cargar productos - esto inicializará la UI automáticamente
        if self.page:
            self.page.run_task(self.load_products)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_products(self) -> None:
        """Carga los productos desde la API según el tipo seleccionado."""
        logger.info(f"Loading products: type={self._product_type}")
        self._is_loading = True
        self._error_message = ""
        self._products = []

        # Actualizar UI para mostrar carga
        self._update_products_ui()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import product_api

            # Los tipos válidos en el API son "article" y "nomenclature" (minúsculas)
            product_type_api = self._product_type.lower()
            logger.debug(f"Requesting products with type: {product_type_api}")

            # Obtener productos por tipo
            result = await product_api.get_by_type(
                product_type=product_type_api,
                skip=0,
                limit=100,
            )

            # El backend devuelve una lista directamente para /type/{TYPE}
            self._products = result if isinstance(result, list) else []
            logger.info(f"Received {len(self._products)} products from API")

            # Depuración: Loguear el primer producto para ver qué campos trae
            if self._products:
                logger.debug(f"Sample product keys: {list(self._products[0].keys())}")
                logger.debug(f"Sample product: {self._products[0]}")

            logger.success(f"Products loaded successfully: {len(self._products)} items")

        except Exception as e:
            logger.exception(f"Error loading products: {e}")
            self._error_message = f"Error al cargar productos: {str(e)}"
            self._products = []

        finally:
            self._is_loading = False
            # Actualizar UI con resultados
            self._update_products_ui()
            if self.page:
                self.update()
                # Pequeña pausa y re-actualización para asegurar que Flet renderice
                import asyncio
                await asyncio.sleep(0.1)
                self.update()

    def _on_product_type_click(self, product_type: str) -> None:
        """Callback cuando se hace click en un tipo de producto."""
        if self._product_type == product_type:
            return  # Ya está seleccionado
            
        self._product_type = product_type
        logger.info(f"Product type changed: {self._product_type}")
        
        # Actualizar visualmente los botones inmediatamente
        if self._article_button:
            self._article_button.style.bgcolor = ft.Colors.PRIMARY if self._product_type == "article" else ft.Colors.GREY_300
            # Actualizar colores de texto/icono si es necesario (Flet v0.80+)
            for ctrl in self._article_button.content.controls:
                if isinstance(ctrl, (ft.Icon, ft.Text)):
                    ctrl.color = ft.Colors.WHITE if self._product_type == "article" else None
        
        if self._nomenclature_button:
            self._nomenclature_button.style.bgcolor = ft.Colors.PRIMARY if self._product_type == "nomenclature" else ft.Colors.GREY_300
            for ctrl in self._nomenclature_button.content.controls:
                if isinstance(ctrl, (ft.Icon, ft.Text)):
                    ctrl.color = ft.Colors.WHITE if self._product_type == "nomenclature" else None

        # Limpiar selección actual del producto
        self._selected_product = None
        self._search_query = ""
        if self._search_field:
            self._search_field.value = ""
        
        # Recargar productos
        if self.page:
            self.update() # Actualizar estado visual de botones
            self.page.run_task(self.load_products)

    def _on_search_change(self, e: ft.ControlEvent) -> None:
        """Callback cuando cambia el texto de búsqueda."""
        self._search_query = e.control.value

    def _on_search_submit(self, e: ft.ControlEvent) -> None:
        """Callback cuando se envía la búsqueda."""
        self._perform_search()

    def _on_search_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace click en buscar."""
        self._perform_search()

    def _perform_search(self) -> None:
        """Realiza la búsqueda de productos."""
        if not self._search_query.strip():
            if self.page:
                self.page.run_task(self.load_products)
            return

        logger.info(f"Searching products: query={self._search_query}")
        if self.page:
            self.page.run_task(self._search_products)

    async def _search_products(self) -> None:
        """Busca productos por query."""
        self._is_loading = True
        self._error_message = ""
        self._products = []
        
        # Actualizar UI para mostrar carga
        self._update_products_ui()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import product_api

            result = await product_api.search(
                query=self._search_query,
                page=1,
                page_size=100,
            )

            # El backend devuelve una lista directamente para /search o un dict con 'items'
            if isinstance(result, dict):
                all_products = result.get("items", [])
            else:
                all_products = result if isinstance(result, list) else []
            
            # Filtrar por tipo (comparar en mayúsculas para consistencia)
            product_type_upper = self._product_type.upper()
            self._products = [
                p for p in all_products 
                if p.get("product_type", "").upper() == product_type_upper
            ]

            logger.success(f"Search completed: {len(self._products)} results")

        except Exception as e:
            logger.exception(f"Error searching products: {e}")
            self._error_message = f"Error al buscar productos: {str(e)}"
            self._products = []

        finally:
            self._is_loading = False
            # Actualizar UI con resultados
            self._update_products_ui()
            if self.page:
                self.update()

    def _on_product_select(self, row_data: dict) -> None:
        """Callback cuando se selecciona un producto."""
        self._selected_product = row_data.get("_raw")
        logger.info(f"Product selected: {self._selected_product.get('reference')}")
        
        # Mostrar formulario de detalles
        self._show_details_form()

    def _show_details_form(self) -> None:
        """Muestra el formulario de detalles del producto."""
        if not self._selected_product or not self._details_form:
            return

        # Mostrar formulario
        self._details_form.visible = True

        # Limpiar campos
        self._quantity_field.set_value("")
        self._unit_price_field.set_value("")
        self._discount_field.set_value("0")
        self._notes_field.value = ""

        if self.page:
            self.update()

    def _hide_details_form(self) -> None:
        """Oculta el formulario de detalles del producto."""
        if self._details_form:
            self._details_form.visible = False

        if self.page:
            self.update()

    def _on_cancel_click(self, e: ft.ControlEvent) -> None:
        """Callback para cancelar la selección."""
        self._selected_product = None
        self._hide_details_form()

    def _on_add_product_click(self, e: ft.ControlEvent) -> None:
        """Callback para agregar el producto a la lista de seleccionados."""
        if not self._selected_product:
            return

        # Validar campos
        if not self._quantity_field.validate():
            return
        if not self._unit_price_field.validate():
            return

        # Preparar datos
        try:
            quantity = Decimal(self._quantity_field.get_value())
            unit_price = Decimal(self._unit_price_field.get_value())
            discount = Decimal(self._discount_field.get_value() or "0")
        except Exception as e:
            logger.error(f"Error parsing values: {e}")
            if self.page:
                snackbar = ft.SnackBar(content=ft.Text("Error: Valores numéricos inválidos"))
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()
            return

        # Agregar a la lista de seleccionados
        selected_item = {
            "product_id": self._selected_product.get("id"),
            "reference": self._selected_product.get("reference", ""),
            "designation": self._selected_product.get("designation_es") or self._selected_product.get("name") or self._selected_product.get("short_designation", "-"),
            "quantity": float(quantity),
            "unit_price": float(unit_price),
            "discount_percentage": float(discount),
            "notes": self._notes_field.value or None,
            "sequence": len(self._selected_products) + 1,
            "_raw": self._selected_product,
        }

        self._selected_products.append(selected_item)
        logger.info(f"Product added to selection: {selected_item['reference']}")

        # Actualizar tabla de seleccionados
        self._update_selected_products_table()

        # Limpiar selección y ocultar formulario
        self._selected_product = None
        self._hide_details_form()

        # Mostrar mensaje
        if self.page:
            snackbar = ft.SnackBar(
                content=ft.Text("Producto agregado a la selección"),
                bgcolor=ft.Colors.GREEN,
            )
            self.page.overlay.append(snackbar)
            snackbar.open = True
            self.page.update()

    def _update_selected_products_table(self) -> None:
        """Actualiza la tabla de productos seleccionados."""
        self._update_selected_ui()
        if self.page:
            self.update()

    def _on_remove_selected_product(self, row_data: dict) -> None:
        """Callback para eliminar un producto de la selección."""
        original = row_data.get("_original")
        if original in self._selected_products:
            self._selected_products.remove(original)
            logger.info(f"Product removed from selection: {original['reference']}")
            self._update_selected_products_table()

    def _on_save_selection_click(self, e: ft.ControlEvent) -> None:
        """Callback para guardar todos los productos seleccionados."""
        if not self._selected_products:
            return

        logger.info(f"Saving {len(self._selected_products)} products to quote")
        
        if self.page:
            self.page.run_task(self._save_all_products)

    async def _save_all_products(self) -> None:
        """Guarda todos los productos seleccionados a la cotización."""
        try:
            from src.frontend.services.api import quote_api

            success_count = 0
            error_count = 0

            for item in self._selected_products:
                try:
                    product_data = {
                        "product_id": item["product_id"],
                        "quantity": item["quantity"],
                        "unit_price": item["unit_price"],
                        "discount_percentage": item["discount_percentage"],
                        "notes": item["notes"],
                        "sequence": item["sequence"],
                    }

                    await quote_api.add_product(self.quote_id, product_data)
                    success_count += 1
                    logger.success(f"Product saved: {item['reference']}")

                except Exception as e:
                    error_count += 1
                    logger.error(f"Error saving product {item['reference']}: {e}")

            # Mostrar resultado
            if self.page:
                if error_count == 0:
                    snackbar = ft.SnackBar(
                        content=ft.Text(f"✓ {success_count} producto(s) guardado(s) exitosamente"),
                        bgcolor=ft.Colors.GREEN,
                    )
                else:
                    snackbar = ft.SnackBar(
                        content=ft.Text(f"⚠ {success_count} guardados, {error_count} con errores"),
                        bgcolor=ft.Colors.ORANGE,
                    )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()

            # Limpiar selección
            self._selected_products.clear()
            self._update_selected_products_table()

            # Notificar al padre
            if self.on_product_added:
                self.on_product_added()

        except Exception as e:
            logger.exception(f"Error saving products: {e}")
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(f"Error al guardar productos: {str(e)}"),
                    bgcolor=ft.Colors.RED,
                )
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.page.update()

    def _on_back_click(self, e: ft.ControlEvent) -> None:
        """Callback para volver atrás."""
        if self.on_back:
            self.on_back()

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        logger.debug("QuoteProductsView state changed, updating view")
        # Solo actualizar la vista existente, no reconstruir
        # Reconstruir crearía nuevos contenedores y rompería las referencias
        if self.page and not self._is_loading:
            self.update()
