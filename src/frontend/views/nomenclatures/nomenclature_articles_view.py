"""
Vista para agregar artículos a una nomenclatura.

Permite buscar artículos y agregarlos como componentes de la nomenclatura.
Similar a la vista de agregar productos en cotización.
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


class NomenclatureArticlesView(ft.Column):
    """
    Vista para agregar artículos a una nomenclatura.

    Args:
        nomenclature_id: ID de la nomenclatura
        on_back: Callback para volver atrás
        on_article_added: Callback cuando se agregan artículos

    Example:
        >>> view = NomenclatureArticlesView(nomenclature_id=123, on_back=handle_back)
        >>> page.add(view)
    """

    def __init__(
        self,
        nomenclature_id: int,
        on_back: Callable[[], None] | None = None,
        on_article_added: Callable[[], None] | None = None,
    ):
        """Inicializa la vista de artículos de nomenclatura."""
        super().__init__()

        self.nomenclature_id = nomenclature_id
        self.on_back = on_back
        self.on_article_added = on_article_added

        # Estado
        self._is_loading: bool = False
        self._error_message: str = ""
        self._articles: list[dict] = []
        self._search_query: str = ""
        self._selected_articles: list[dict] = []  # Lista de artículos pendientes de agregar
        self._existing_components: list[dict] = []  # Componentes ya guardados en la nomenclatura
        self._nomenclature_data: dict | None = None

        # Configurar propiedades de la columna
        self.expand = True
        self.spacing = LayoutConstants.SPACING_LG
        self.scroll = ft.ScrollMode.AUTO

        logger.info(f"NomenclatureArticlesView initialized: nomenclature_id={nomenclature_id}")

    def did_mount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.info("NomenclatureArticlesView mounted")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)

        # Configurar breadcrumb
        app_state.navigation.set_breadcrumb([
            {"label": "nomenclatures.title", "route": "/nomenclatures"},
            {"label": "nomenclatures.edit", "route": f"/nomenclatures/{self.nomenclature_id}/edit"},
            {"label": "nomenclatures.add_articles", "route": None},
        ])

        # Cargar artículos
        if self.page:
            self.page.run_task(self._load_all_data)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def _load_all_data(self) -> None:
        """Carga todos los artículos y los componentes existentes en la nomenclatura."""
        logger.info("Loading all data...")
        self._is_loading = True
        self._error_message = ""
        self._rebuild_ui()

        try:
            from src.frontend.services.api import product_api

            # Cargar datos de la nomenclatura
            try:
                self._nomenclature_data = await product_api.get_by_id(self.nomenclature_id)
                logger.success(f"Nomenclature data loaded: {self._nomenclature_data.get('reference')}")
            except Exception as e:
                logger.warning(f"Could not load nomenclature data: {e}")
                self._nomenclature_data = None

            # Cargar componentes existentes de la nomenclatura
            try:
                bom_components = await product_api.get_bom_components(self.nomenclature_id)
                self._existing_components = []
                for comp in (bom_components or []):
                    component_product = comp.get("component", {}) or {}
                    self._existing_components.append({
                        "bom_id": comp.get("id"),  # ID del registro BOM
                        "component_id": comp.get("component_id"),
                        "reference": component_product.get("reference", ""),
                        "designation": component_product.get("designation_es") or component_product.get("designation_en") or "-",
                        "quantity": float(comp.get("quantity", 0)),
                    })
                logger.success(f"Loaded {len(self._existing_components)} existing components from nomenclature")
            except Exception as e:
                logger.warning(f"Could not load existing components: {e}")
                self._existing_components = []

            # Cargar todos los artículos
            articles_result = await product_api.get_by_type(
                product_type="article",
                skip=0,
                limit=200,
            )
            self._articles = articles_result if isinstance(articles_result, list) else []
            logger.success(f"Loaded {len(self._articles)} articles")

        except Exception as e:
            logger.exception(f"Error loading data: {e}")
            self._error_message = f"Error al cargar datos: {str(e)}"

        finally:
            self._is_loading = False
            self._rebuild_ui()

    def _rebuild_ui(self) -> None:
        """Reconstruye toda la UI."""
        self.controls.clear()

        # Título de la nomenclatura
        nomenclature_name = ""
        if self._nomenclature_data:
            nomenclature_name = f" - {self._nomenclature_data.get('reference', '')}"

        # Header
        header = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip=t("common.back"),
                    on_click=self._on_back_click,
                ),
                ft.Icon(ft.Icons.ADD_CIRCLE, size=LayoutConstants.ICON_SIZE_XL),
                ft.Text(
                    f"{t('nomenclatures.add_articles')}{nomenclature_name}",
                    size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                    weight=LayoutConstants.FONT_WEIGHT_BOLD,
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        # Contenido principal
        if self._is_loading:
            content = ft.Container(
                content=LoadingSpinner(message="Cargando artículos..."),
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
        """Construye el contenido principal."""
        # Búsqueda
        search_field = ft.TextField(
            label=t("common.search"),
            prefix_icon=ft.Icons.SEARCH,
            hint_text="Buscar por referencia o nombre...",
            on_change=self._on_search_change,
            value=self._search_query,
        )

        # Filtrar artículos según búsqueda
        filtered_articles = self._filter_articles()

        # Lista de artículos
        articles_list = self._build_articles_list(filtered_articles)

        # Panel izquierdo con búsqueda y lista
        left_panel = ft.Column(
            controls=[
                search_field,
                ft.Container(
                    content=ft.Text(
                        f"Artículos disponibles ({len(filtered_articles)})",
                        size=LayoutConstants.FONT_SIZE_MD,
                        weight=ft.FontWeight.BOLD,
                    ),
                    padding=ft.padding.only(top=8),
                ),
                ft.Divider(),
                ft.Container(content=articles_list, expand=True),
            ],
            spacing=LayoutConstants.SPACING_MD,
            expand=True,
        )

        # Panel de componentes seleccionados (lado derecho)
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

    def _filter_articles(self) -> list[dict]:
        """Filtra los artículos según la búsqueda."""
        if not self._search_query:
            return self._articles

        query = self._search_query.lower()
        filtered = []
        for article in self._articles:
            reference = (article.get("reference") or "").lower()
            designation_es = (article.get("designation_es") or "").lower()
            designation_en = (article.get("designation_en") or "").lower()
            if query in reference or query in designation_es or query in designation_en:
                filtered.append(article)
        return filtered

    def _on_search_change(self, e: ft.ControlEvent) -> None:
        """Callback cuando cambia el texto de búsqueda."""
        self._search_query = e.control.value or ""
        self._rebuild_ui()

    def _build_articles_list(self, articles: list[dict]) -> ft.Control:
        """Construye la lista de artículos como cards."""
        if not articles:
            return ft.Container(
                content=EmptyState(
                    icon=ft.Icons.INVENTORY_2,
                    title="Sin artículos",
                    message="No hay artículos disponibles" if not self._search_query else "No se encontraron artículos",
                ),
                expand=True,
                padding=LayoutConstants.PADDING_LG,
            )

        # Crear lista de cards
        article_cards = []
        for article in articles:
            card = self._build_article_card(article)
            article_cards.append(card)

        return ft.Container(
            content=ft.Column(
                controls=article_cards,
                spacing=LayoutConstants.SPACING_SM,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=LayoutConstants.PADDING_MD,
            expand=True,
        )

    def _build_article_card(self, article: dict) -> ft.Control:
        """Construye una card para un artículo."""
        reference = article.get("reference", "")
        name = article.get("designation_es") or article.get("designation_en") or article.get("short_designation", "-")
        family = article.get("family_type", {}).get("name", "-") if isinstance(article.get("family_type"), dict) else "-"
        raw_price = article.get("sale_price")
        price = float(raw_price) if raw_price is not None else 0.0

        # Verificar si ya está seleccionado (pendiente) o guardado (existente)
        is_pending = any(sa.get("component_id") == article.get("id") for sa in self._selected_articles)
        is_saved = any(ec.get("component_id") == article.get("id") for ec in self._existing_components)
        is_added = is_pending or is_saved

        # Handler para agregar el artículo
        def handle_add_click(e, art=article):
            if not is_added:
                logger.debug(f"Card clicked for article: {art.get('reference')}")
                self._on_add_article(art)

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(reference, weight=ft.FontWeight.BOLD, size=LayoutConstants.FONT_SIZE_MD),
                            ft.Text(name, size=LayoutConstants.FONT_SIZE_SM, color=ft.Colors.GREY_600),
                            ft.Text(f"Familia: {family}", size=LayoutConstants.FONT_SIZE_XS, color=ft.Colors.GREY_600),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(f"${price:,.2f}", weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                            ft.IconButton(
                                icon=ft.Icons.CHECK_CIRCLE if is_added else ft.Icons.ADD_CIRCLE_OUTLINE,
                                icon_color=ft.Colors.GREEN if is_saved else (ft.Colors.ORANGE if is_pending else ft.Colors.BLUE),
                                tooltip="Ya guardado" if is_saved else ("Pendiente" if is_pending else "Agregar"),
                                on_click=handle_add_click,
                                disabled=is_added,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.END,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=LayoutConstants.PADDING_MD,
            border=ft.border.all(1, ft.Colors.GREEN if is_saved else (ft.Colors.ORANGE if is_pending else ft.Colors.GREY_300)),
            border_radius=LayoutConstants.RADIUS_SM,
            bgcolor=ft.Colors.GREY_800 if is_saved else (ft.Colors.GREY_700 if is_pending else ft.Colors.GREY_900),
            on_click=handle_add_click if not is_added else None,
            ink=not is_added,
        )

    def _build_selected_panel(self) -> ft.Control:
        """Construye el panel de componentes seleccionados y existentes."""
        total_components = len(self._existing_components) + len(self._selected_articles)
        
        # Header principal
        header = ft.Row(
            controls=[
                ft.Icon(ft.Icons.LIST_ALT, size=LayoutConstants.ICON_SIZE_MD),
                ft.Text(
                    f"Componentes ({total_components})",
                    size=LayoutConstants.FONT_SIZE_LG,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        sections = []

        # Sección de componentes pendientes (por guardar) - PRIMERO
        if self._selected_articles:
            pending_header = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.PENDING, color=ft.Colors.ORANGE, size=16),
                        ft.Text(
                            f"Pendientes ({len(self._selected_articles)})",
                            size=LayoutConstants.FONT_SIZE_SM,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ORANGE,
                        ),
                    ],
                    spacing=4,
                ),
                padding=ft.padding.only(top=8, bottom=4),
            )
            
            pending_cards = []
            for i, item in enumerate(self._selected_articles):
                card = self._build_selected_item_card(item, i)
                pending_cards.append(card)
            
            sections.append(pending_header)
            sections.extend(pending_cards)

        # Sección de componentes existentes (ya guardados)
        if self._existing_components:
            existing_header = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=16),
                        ft.Text(
                            f"Guardados ({len(self._existing_components)})",
                            size=LayoutConstants.FONT_SIZE_SM,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREEN,
                        ),
                    ],
                    spacing=4,
                ),
                padding=ft.padding.only(top=8, bottom=4),
            )
            
            existing_cards = []
            for item in self._existing_components:
                card = self._build_existing_item_card(item)
                existing_cards.append(card)

            sections.append(existing_header)
            sections.extend(existing_cards)

        # Contenido vacío si no hay componentes
        if not sections:
            content = EmptyState(
                icon=ft.Icons.VIEW_LIST,
                title="Sin componentes",
                message="Haz clic en + para agregar artículos",
            )
            footer = ft.Container()
        else:
            content = ft.Column(
                controls=sections,
                spacing=LayoutConstants.SPACING_SM,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )

            # Botón guardar (solo si hay pendientes)
            if self._selected_articles:
                footer = ft.Column(
                    controls=[
                        ft.Divider(),
                        ft.Text(
                            f"{len(self._selected_articles)} artículo(s) por guardar",
                            size=LayoutConstants.FONT_SIZE_SM,
                            color=ft.Colors.ORANGE,
                        ),
                        ft.ElevatedButton(
                            content=ft.Text(t("common.save")),
                            icon=ft.Icons.SAVE,
                            on_click=self._on_save_click,
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.ON_PRIMARY,
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_SM,
                )
            else:
                footer = ft.Container()

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
            border=ft.border.all(1, ft.Colors.GREY_300),
            border_radius=LayoutConstants.RADIUS_MD,
            expand=True,
        )

    def _build_existing_item_card(self, item: dict) -> ft.Control:
        """Construye una card para un componente ya guardado en la nomenclatura."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(item.get("reference", ""), weight=ft.FontWeight.BOLD),
                            ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN, size=16),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(item.get("designation", ""), size=LayoutConstants.FONT_SIZE_SM),
                    ft.Text(
                        f"Cantidad: {item.get('quantity', 0)}",
                        size=LayoutConstants.FONT_SIZE_XS,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                spacing=2,
            ),
            padding=LayoutConstants.PADDING_SM,
            border=ft.border.all(1, ft.Colors.GREEN),
            border_radius=LayoutConstants.RADIUS_SM,
            bgcolor=ft.Colors.GREY_800,
        )

    def _build_selected_item_card(self, item: dict, index: int) -> ft.Control:
        """Construye una card para un componente seleccionado."""
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
                                on_click=lambda e, idx=index: self._on_remove_article(idx),
                                icon_size=18,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(item.get("designation", ""), size=LayoutConstants.FONT_SIZE_SM),
                    ft.Text(
                        f"Cantidad: {item.get('quantity', 0)}",
                        size=LayoutConstants.FONT_SIZE_XS,
                        color=ft.Colors.GREY_600,
                    ),
                ],
                spacing=2,
            ),
            padding=LayoutConstants.PADDING_SM,
            border=ft.border.all(1, ft.Colors.ORANGE),
            border_radius=LayoutConstants.RADIUS_SM,
            bgcolor=ft.Colors.GREY_700,
        )

    def _on_add_article(self, article: dict) -> None:
        """Muestra diálogo para agregar un artículo."""
        logger.info(f"_on_add_article called for article: {article.get('reference', 'unknown')}")
        
        article_name = article.get("designation_es") or article.get("designation_en") or article.get("reference", "")
        
        logger.debug(f"Article details: name={article_name}")

        # Campo de cantidad
        quantity_field = ft.TextField(
            label="Cantidad",
            value="1",
            keyboard_type=ft.KeyboardType.NUMBER,
            autofocus=True,
        )

        def handle_add(e):
            try:
                qty = Decimal(quantity_field.value or "1")

                if qty <= 0:
                    quantity_field.error_text = "Debe ser mayor a 0"
                    quantity_field.update()
                    return

                # Agregar al principio de la lista
                self._selected_articles.insert(0, {
                    "component_id": article.get("id"),
                    "reference": article.get("reference", ""),
                    "designation": article_name,
                    "quantity": float(qty),
                })

                logger.info(f"Article added to selection: {article.get('reference')}")

                # Cerrar diálogo y actualizar UI
                dlg.open = False
                self.page.update()
                self._rebuild_ui()

            except Exception as ex:
                logger.error(f"Error adding article: {ex}")
                quantity_field.error_text = "Valor inválido"
                quantity_field.update()

        def handle_cancel(e):
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Agregar: {article_name[:40]}..."),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(f"Referencia: {article.get('reference', '')}"),
                        quantity_field,
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

    def _on_remove_article(self, index: int) -> None:
        """Elimina un artículo de la selección."""
        if 0 <= index < len(self._selected_articles):
            removed = self._selected_articles.pop(index)
            logger.info(f"Article removed from selection: {removed.get('reference')}")
            self._rebuild_ui()

    def _on_save_click(self, e: ft.ControlEvent) -> None:
        """Guarda todos los artículos seleccionados."""
        if not self._selected_articles:
            return

        logger.info(f"Saving {len(self._selected_articles)} articles to nomenclature")
        if self.page:
            self.page.run_task(self._save_all_articles)

    async def _save_all_articles(self) -> None:
        """Guarda todos los artículos seleccionados a la nomenclatura."""
        try:
            from src.frontend.services.api import product_api

            success_count = 0
            error_count = 0

            for item in self._selected_articles:
                try:
                    component_data = {
                        "parent_id": self.nomenclature_id,
                        "component_id": item["component_id"],
                        "quantity": item["quantity"],
                    }

                    await product_api.add_component(self.nomenclature_id, component_data)
                    success_count += 1
                    logger.success(f"Component saved: {item['reference']}")

                except Exception as ex:
                    error_count += 1
                    logger.error(f"Error saving component {item['reference']}: {ex}")

            # Mostrar resultado
            if self.page:
                if error_count == 0:
                    snackbar = ft.SnackBar(
                        content=ft.Text(f"✓ {success_count} componente(s) agregado(s) exitosamente"),
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

            # Limpiar selección y recargar datos
            self._selected_articles.clear()
            
            # Recargar los componentes existentes
            await self._load_all_data()

            # Notificar al padre
            if self.on_article_added:
                self.on_article_added()

        except Exception as e:
            logger.exception(f"Error saving articles: {e}")
            if self.page:
                snackbar = ft.SnackBar(
                    content=ft.Text(f"Error al guardar componentes: {str(e)}"),
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
        logger.debug("NomenclatureArticlesView state changed")
        if self.page and not self._is_loading:
            self._rebuild_ui()
