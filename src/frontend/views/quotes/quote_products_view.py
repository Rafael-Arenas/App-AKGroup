"""
Vista para agregar productos (artículos y nomenclaturas) a una cotización.

Permite seleccionar entre artículos y nomenclaturas, buscar productos y agregarlos a la cotización.
Versión simplificada que evita problemas con actualizaciones dinámicas de DataTable.
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

        # Estado
        self._is_loading: bool = False
        self._error_message: str = ""
        self._articles: list[dict] = []
        self._nomenclatures: list[dict] = []
        self._selected_product: dict | None = None
        self._search_query: str = ""
        self._selected_products: list[dict] = []  # Lista de productos para agregar
        self._active_type: str = "article"  # "article" o "nomenclature"

        # Configurar propiedades de la columna
        self.expand = True
        self.spacing = LayoutConstants.SPACING_LG
        self.scroll = ft.ScrollMode.AUTO

        logger.info(f"QuoteProductsView initialized: quote_id={quote_id}")

    def did_mount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.info("QuoteProductsView mounted")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)

        # Configurar breadcrumb
        app_state.navigation.set_breadcrumb([
            {"label": "clients.title", "route": "/companies/clients"},
            {"label": "dashboard.title", "route": f"/companies/dashboard/{self.company_id}/{self.company_type}"},
            {"label": "quotes.title", "route": f"/companies/dashboard/{self.company_id}/{self.company_type}/quotes"},
            {"label": "quotes.detail", "route": f"/companies/dashboard/{self.company_id}/{self.company_type}/quotes/{self.quote_id}"},
            {"label": "quotes.add_products", "route": None},
        ])

        # Cargar productos
        if self.page:
            self.page.run_task(self._load_all_products)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def _load_all_products(self) -> None:
        """Carga todos los productos (artículos y nomenclaturas)."""
        logger.info("Loading all products...")
        self._is_loading = True
        self._error_message = ""
        self._rebuild_ui()

        try:
            from src.frontend.services.api import product_api

            # Cargar artículos
            articles_result = await product_api.get_by_type(
                product_type="article",
                skip=0,
                limit=100,
            )
            self._articles = articles_result if isinstance(articles_result, list) else []
            logger.success(f"Loaded {len(self._articles)} articles")

            # Cargar nomenclaturas
            nomenclatures_result = await product_api.get_by_type(
                product_type="nomenclature",
                skip=0,
                limit=100,
            )
            self._nomenclatures = nomenclatures_result if isinstance(nomenclatures_result, list) else []
            logger.success(f"Loaded {len(self._nomenclatures)} nomenclatures")

        except Exception as e:
            logger.exception(f"Error loading products: {e}")
            self._error_message = f"Error al cargar productos: {str(e)}"

        finally:
            self._is_loading = False
            self._rebuild_ui()

    def _rebuild_ui(self) -> None:
        """Reconstruye toda la UI."""
        self.controls.clear()

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

        # Contenido principal
        if self._is_loading:
            content = ft.Container(
                content=LoadingSpinner(message="Cargando productos..."),
                expand=True,
                alignment=ft.Alignment(0, 0),  # center
            )
        elif self._error_message:
            content = ErrorDisplay(message=self._error_message)
        else:
            content = self._build_main_content()

        self.controls.extend([
            ft.Container(
                content=ft.Column(
                    controls=[header, content],
                    spacing=LayoutConstants.SPACING_LG,
                    expand=True,
                ),
                padding=LayoutConstants.PADDING_LG,
                expand=True,
            )
        ])

        if self.page:
            self.update()

    def _build_main_content(self) -> ft.Control:
        """Construye el contenido principal con selector de tipo."""
        # Botones de selección de tipo
        is_article = self._active_type == "article"
        
        type_selector = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.INVENTORY_2, color=ft.Colors.WHITE if is_article else None, size=20),
                            ft.Text(
                                f"{t('articles.types.article')} ({len(self._articles)})",
                                color=ft.Colors.WHITE if is_article else None,
                                weight=ft.FontWeight.BOLD if is_article else None,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    bgcolor=ft.Colors.PRIMARY if is_article else ft.Colors.SURFACE_CONTAINER,
                    border_radius=8,
                    on_click=lambda e: self._switch_type("article"),
                    ink=True,
                ),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LIST_ALT, color=ft.Colors.WHITE if not is_article else None, size=20),
                            ft.Text(
                                f"{t('articles.types.nomenclature')} ({len(self._nomenclatures)})",
                                color=ft.Colors.WHITE if not is_article else None,
                                weight=ft.FontWeight.BOLD if not is_article else None,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    bgcolor=ft.Colors.PRIMARY if not is_article else ft.Colors.SURFACE_CONTAINER,
                    border_radius=8,
                    on_click=lambda e: self._switch_type("nomenclature"),
                    ink=True,
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        # Lista de productos según el tipo seleccionado
        if self._active_type == "article":
            products_list = self._build_products_list(self._articles, "article")
        else:
            products_list = self._build_products_list(self._nomenclatures, "nomenclature")

        # Panel izquierdo con selector y lista
        left_panel = ft.Column(
            controls=[
                type_selector,
                ft.Divider(),
                ft.Container(content=products_list, expand=True),
            ],
            spacing=LayoutConstants.SPACING_MD,
            expand=True,
        )

        # Panel de productos seleccionados (lado derecho)
        selected_panel = self._build_selected_panel()

        # Layout principal
        return ft.Row(
            controls=[
                ft.Container(content=left_panel, expand=3),
                ft.VerticalDivider(width=1),
                ft.Container(content=selected_panel, expand=2),
            ],
            expand=True,
            spacing=LayoutConstants.SPACING_MD,
        )

    def _switch_type(self, product_type: str) -> None:
        """Cambia el tipo de producto activo."""
        if self._active_type != product_type:
            self._active_type = product_type
            logger.info(f"Switched to product type: {product_type}")
            self._rebuild_ui()

    def _build_products_list(self, products: list[dict], product_type: str) -> ft.Control:
        """Construye la lista de productos como cards."""
        if not products:
            return ft.Container(
                content=EmptyState(
                    icon=ft.Icons.INVENTORY_2,
                    title="Sin productos",
                    message=f"No hay {product_type}s disponibles",
                ),
                expand=True,
                padding=LayoutConstants.PADDING_LG,
            )

        # Crear lista de cards
        product_cards = []
        for p in products:
            card = self._build_product_card(p)
            product_cards.append(card)

        return ft.Container(
            content=ft.Column(
                controls=product_cards,
                spacing=LayoutConstants.SPACING_SM,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=LayoutConstants.PADDING_MD,
            expand=True,
        )

    def _build_product_card(self, product: dict) -> ft.Control:
        """Construye una card para un producto."""
        reference = product.get("reference", "")
        name = product.get("designation_es") or product.get("designation_en") or product.get("short_designation", "-")
        family = product.get("family_type", {}).get("name", "-") if isinstance(product.get("family_type"), dict) else "-"
        price = product.get("sale_price", "0")

        # Verificar si ya está seleccionado
        is_selected = any(sp.get("product_id") == product.get("id") for sp in self._selected_products)

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(reference, weight=ft.FontWeight.BOLD, size=LayoutConstants.FONT_SIZE_MD),
                            ft.Text(name, size=LayoutConstants.FONT_SIZE_SM, color=ft.Colors.ON_SURFACE_VARIANT),
                            ft.Text(f"Familia: {family}", size=LayoutConstants.FONT_SIZE_XS, color=ft.Colors.ON_SURFACE_VARIANT),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(f"${float(price):,.2f}", weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                            ft.IconButton(
                                icon=ft.Icons.CHECK_CIRCLE if is_selected else ft.Icons.ADD_CIRCLE_OUTLINE,
                                icon_color=ft.Colors.GREEN if is_selected else ft.Colors.PRIMARY,
                                tooltip="Ya agregado" if is_selected else "Agregar",
                                on_click=lambda e, p=product: self._on_add_product(p),
                                disabled=is_selected,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=LayoutConstants.PADDING_MD,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=LayoutConstants.RADIUS_SM,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST if is_selected else ft.Colors.SURFACE,
            on_hover=lambda e: setattr(e.control, 'bgcolor', ft.Colors.SURFACE_CONTAINER if e.data == "true" else ft.Colors.SURFACE),
        )

    def _build_selected_panel(self) -> ft.Control:
        """Construye el panel de productos seleccionados."""
        header = ft.Row(
            controls=[
                ft.Icon(ft.Icons.SHOPPING_CART, size=LayoutConstants.ICON_SIZE_MD),
                ft.Text(
                    f"Productos a agregar ({len(self._selected_products)})",
                    size=LayoutConstants.FONT_SIZE_LG,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        if not self._selected_products:
            content = EmptyState(
                icon=ft.Icons.SHOPPING_CART_OUTLINED,
                title="Sin productos",
                message="Haz clic en + para agregar productos",
            )
            footer = ft.Container()
        else:
            # Lista de productos seleccionados
            selected_cards = []
            for i, item in enumerate(self._selected_products):
                card = self._build_selected_item_card(item, i)
                selected_cards.append(card)

            content = ft.Column(
                controls=selected_cards,
                spacing=LayoutConstants.SPACING_SM,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )

            # Total y botón guardar
            total_amount = sum(
                float(item.get("quantity", 0)) * float(item.get("unit_price", 0))
                for item in self._selected_products
            )

            footer = ft.Column(
                controls=[
                    ft.Divider(),
                    ft.Row(
                        controls=[
                            ft.Text("Total estimado:", weight=ft.FontWeight.BOLD),
                            ft.Text(f"${total_amount:,.2f}", weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.ElevatedButton(
                        content=ft.Text(t("common.save")),
                        icon=ft.Icons.SAVE,
                        on_click=self._on_save_click,
                        bgcolor=ft.Colors.PRIMARY,
                        color=ft.Colors.ON_PRIMARY,
                    ),
                ],
                spacing=LayoutConstants.SPACING_SM,
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    header,
                    ft.Divider(),
                    ft.Container(content=content, expand=True),
                    footer,
                ],
                spacing=LayoutConstants.SPACING_SM,
                expand=True,
            ),
            padding=LayoutConstants.PADDING_MD,
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=LayoutConstants.RADIUS_MD,
            expand=True,
        )

    def _build_selected_item_card(self, item: dict, index: int) -> ft.Control:
        """Construye una card para un producto seleccionado."""
        subtotal = float(item.get("quantity", 0)) * float(item.get("unit_price", 0))

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(item.get("reference", ""), weight=ft.FontWeight.BOLD),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_color=ft.Colors.ERROR,
                                tooltip="Eliminar",
                                on_click=lambda e, idx=index: self._on_remove_product(idx),
                                icon_size=18,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(item.get("designation", ""), size=LayoutConstants.FONT_SIZE_SM),
                    ft.Row(
                        controls=[
                            ft.Text(f"Cant: {item.get('quantity', 0)}", size=LayoutConstants.FONT_SIZE_XS),
                            ft.Text(f"P.U: ${float(item.get('unit_price', 0)):,.2f}", size=LayoutConstants.FONT_SIZE_XS),
                            ft.Text(f"= ${subtotal:,.2f}", size=LayoutConstants.FONT_SIZE_XS, weight=ft.FontWeight.BOLD),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                spacing=2,
            ),
            padding=LayoutConstants.PADDING_SM,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=LayoutConstants.RADIUS_SM,
            bgcolor=ft.Colors.SURFACE_CONTAINER_LOWEST,
        )

    def _on_add_product(self, product: dict) -> None:
        """Muestra diálogo para agregar un producto."""
        product_name = product.get("designation_es") or product.get("designation_en") or product.get("reference", "")
        sale_price = product.get("sale_price", "0")

        # Campos del formulario
        quantity_field = ft.TextField(
            label="Cantidad",
            value="1",
            keyboard_type=ft.KeyboardType.NUMBER,
            autofocus=True,
        )
        
        price_field = ft.TextField(
            label="Precio Unitario",
            value=str(sale_price),
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        discount_field = ft.TextField(
            label="Descuento (%)",
            value="0",
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        notes_field = ft.TextField(
            label="Notas",
            multiline=True,
            min_lines=2,
            max_lines=3,
        )

        def handle_add(e):
            try:
                qty = Decimal(quantity_field.value or "1")
                price = Decimal(price_field.value or "0")
                discount = Decimal(discount_field.value or "0")

                if qty <= 0:
                    quantity_field.error_text = "Debe ser mayor a 0"
                    quantity_field.update()
                    return

                if price <= 0:
                    price_field.error_text = "Debe ser mayor a 0"
                    price_field.update()
                    return

                # Agregar a la lista
                self._selected_products.append({
                    "product_id": product.get("id"),
                    "reference": product.get("reference", ""),
                    "designation": product_name,
                    "quantity": float(qty),
                    "unit_price": float(price),
                    "discount_percentage": float(discount),
                    "notes": notes_field.value or None,
                    "sequence": len(self._selected_products) + 1,
                })

                logger.info(f"Product added to selection: {product.get('reference')}")

                # Cerrar diálogo y actualizar UI
                dlg.open = False
                self.page.update()
                self._rebuild_ui()

            except Exception as ex:
                logger.error(f"Error adding product: {ex}")
                quantity_field.error_text = "Valor inválido"
                quantity_field.update()

        def handle_cancel(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Agregar: {product_name[:40]}..."),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        quantity_field,
                        price_field,
                        discount_field,
                        notes_field,
                    ],
                    spacing=LayoutConstants.SPACING_MD,
                    tight=True,
                ),
                width=400,
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancelar"), on_click=handle_cancel),
                ft.ElevatedButton(content=ft.Text("Agregar"), on_click=handle_add),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def _on_remove_product(self, index: int) -> None:
        """Elimina un producto de la selección."""
        if 0 <= index < len(self._selected_products):
            removed = self._selected_products.pop(index)
            logger.info(f"Product removed from selection: {removed.get('reference')}")
            self._rebuild_ui()

    def _on_save_click(self, e: ft.ControlEvent) -> None:
        """Guarda todos los productos seleccionados."""
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

                except Exception as ex:
                    error_count += 1
                    logger.error(f"Error saving product {item['reference']}: {ex}")

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
            self._rebuild_ui()

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
        logger.debug("QuoteProductsView state changed")
        if self.page and not self._is_loading:
            self._rebuild_ui()
