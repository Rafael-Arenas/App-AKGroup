"""
Vista de detalle de nomenclatura.

Muestra información completa de una nomenclatura incluyendo el árbol de componentes (BOM).
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t
from src.frontend.components.common import BaseCard, LoadingSpinner, ErrorDisplay, ConfirmDialog


class NomenclatureDetailView(ft.Container):
    """
    Vista de detalle de nomenclatura con BOM.

    Args:
        nomenclature_id: ID de la nomenclatura a mostrar
        on_edit: Callback cuando se edita la nomenclatura
        on_delete: Callback cuando se elimina la nomenclatura
        on_back: Callback para volver atrás

    Example:
        >>> detail = NomenclatureDetailView(nomenclature_id=123, on_edit=handle_edit)
        >>> page.add(detail)
    """

    def __init__(
        self,
        nomenclature_id: int,
        on_edit: Callable[[int], None] | None = None,
        on_delete: Callable[[int], None] | None = None,
        on_back: Callable[[], None] | None = None,
    ):
        """Inicializa la vista de detalle de nomenclatura."""
        super().__init__()
        self.nomenclature_id = nomenclature_id
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_back = on_back

        self._is_loading: bool = True
        self._error_message: str = ""
        self._nomenclature: dict | None = None
        self._bom_components: list[dict] = []

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = LayoutConstants.PADDING_LG

        # Construir contenido inicial (loading)
        self.content = self.build()

        logger.info(f"NomenclatureDetailView initialized: nomenclature_id={nomenclature_id}")

    def build(self) -> ft.Control:
        """Construye el componente de detalle de nomenclatura."""
        if self._is_loading:
            return ft.Container(
                content=LoadingSpinner(message=t("common.loading")),
                expand=True,
                alignment=ft.alignment.center,
            )
        elif self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_nomenclature,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )

        # Badge de estado
        status_badge = ft.Container(
            content=ft.Text(
                t("common.active") if self._nomenclature.get("is_active") else t("common.inactive"),
                size=LayoutConstants.FONT_SIZE_SM,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.Colors.WHITE,
            ),
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_SM,
                vertical=LayoutConstants.PADDING_XS,
            ),
            border_radius=LayoutConstants.RADIUS_SM,
            bgcolor=ft.Colors.GREEN if self._nomenclature.get("is_active") else ft.Colors.RED,
        )

        # Header
        header = ft.Row(
            controls=[
                ft.Icon(
                    name=ft.Icons.LIST_ALT,
                    size=LayoutConstants.ICON_SIZE_XL,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            self._nomenclature.get("designation_es", ""),
                            size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                            weight=LayoutConstants.FONT_WEIGHT_BOLD,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f"Código: {self._nomenclature.get('reference', '')}",
                                    size=LayoutConstants.FONT_SIZE_MD,
                                ),
                                status_badge,
                            ],
                            spacing=LayoutConstants.SPACING_SM,
                        ),
                    ],
                    expand=True,
                    spacing=LayoutConstants.SPACING_XS,
                ),
                ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            tooltip=t("common.edit"),
                            on_click=self._on_edit_click,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip=t("common.delete"),
                            on_click=self._on_delete_click,
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_SM,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Información general
        general_info = ft.Column(
            controls=[
                self._create_info_row(t("product_detail.revision"), self._nomenclature.get("revision", "-") or "-"),
                self._create_info_row(t("nomenclatures.form.reference"), self._nomenclature.get("reference", "-") or "-"),
                self._create_info_row(t("nomenclatures.form.sales_type"), self._nomenclature.get("sales_type", {}).get("name", "-") if self._nomenclature.get("sales_type") else "-"),
                self._create_info_row(t("nomenclatures.form.unit"), self._nomenclature.get("unit", "-") or "-"),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        general_card = BaseCard(
            title=t("nomenclatures.form.basic_info"),
            icon=ft.Icons.INFO_OUTLINED,
            content=general_info,
        )

        # Designaciones en múltiples idiomas
        designations_info = ft.Column(
            controls=[
                self._create_info_row(t("nomenclatures.form.designation_es"), self._nomenclature.get("designation_es", "-") or "-"),
                self._create_info_row(t("nomenclatures.form.designation_en"), self._nomenclature.get("designation_en", "-") or "-"),
                self._create_info_row(t("nomenclatures.form.designation_fr"), self._nomenclature.get("designation_fr", "-") or "-"),
                self._create_info_row(t("nomenclatures.form.short_designation"), self._nomenclature.get("short_designation", "-") or "-"),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        designations_card = BaseCard(
            title=t("nomenclatures.form.designations"),
            icon=ft.Icons.TRANSLATE,
            content=designations_info,
        )

        # Dimensiones y peso
        dimensions_info = ft.Column(
            controls=[
                self._create_info_row(t("nomenclatures.form.length"), f"{float(self._nomenclature.get('length', 0) or 0):.3f} mm"),
                self._create_info_row(t("nomenclatures.form.width"), f"{float(self._nomenclature.get('width', 0) or 0):.3f} mm"),
                self._create_info_row(t("nomenclatures.form.height"), f"{float(self._nomenclature.get('height', 0) or 0):.3f} mm"),
                self._create_info_row(t("nomenclatures.form.volume"), f"{float(self._nomenclature.get('volume', 0) or 0):.6f} m³"),
                self._create_info_row(t("nomenclatures.form.net_weight"), f"{float(self._nomenclature.get('net_weight', 0) or 0):.3f} kg"),
                self._create_info_row(t("nomenclatures.form.gross_weight"), f"{float(self._nomenclature.get('gross_weight', 0) or 0):.3f} kg"),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        dimensions_card = BaseCard(
            title=t("nomenclatures.form.dimensions_and_weight"),
            icon=ft.Icons.STRAIGHTEN,
            content=dimensions_info,
        )

        # Información de precios
        pricing_info = ft.Column(
            controls=[
                self._create_info_row(
                    t("product_detail.purchase_price"), f"${float(self._nomenclature.get('purchase_price', 0) or 0):.2f}"
                ),
                self._create_info_row(
                    t("nomenclatures.form.cost_price"), f"${float(self._nomenclature.get('cost_price', 0) or 0):.2f}"
                ),
                self._create_info_row(
                    t("nomenclatures.form.sale_price"), f"${float(self._nomenclature.get('sale_price', 0) or 0):.2f}"
                ),
                self._create_info_row(
                    t("product_detail.sale_price_eur"), f"€{float(self._nomenclature.get('sale_price_eur', 0) or 0):.2f}"
                ),
                self._create_info_row(
                    t("product_detail.margin_percentage"), f"{float(self._nomenclature.get('margin_percentage', 0) or 0):.1f}%"
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        pricing_card = BaseCard(
            title=t("nomenclatures.form.pricing"),
            icon=ft.Icons.ATTACH_MONEY,
            content=pricing_info,
        )

        # Información de stock
        stock_info = ft.Column(
            controls=[
                self._create_info_row(
                    t("nomenclatures.form.stock_quantity"), f"{float(self._nomenclature.get('stock_quantity', 0) or 0):.3f}"
                ),
                self._create_info_row(
                    t("nomenclatures.form.minimum_stock"), f"{float(self._nomenclature.get('minimum_stock', 0) or 0):.3f}"
                ),
                self._create_info_row(
                    t("product_detail.stock_location"), self._nomenclature.get("stock_location", "-") or "-"
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        stock_card = BaseCard(
            title=t("nomenclatures.form.stock_section"),
            icon=ft.Icons.INVENTORY,
            content=stock_info,
        )

        # URLs
        urls_info = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            f"{t('nomenclatures.form.image_url')}:",
                            size=LayoutConstants.FONT_SIZE_MD,
                            weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                            width=150,
                        ),
                        ft.TextButton(
                            text=self._nomenclature.get("image_url", "-") or "-",
                            url=self._nomenclature.get("image_url", "#"),
                            disabled=not self._nomenclature.get("image_url")
                        ) if self._nomenclature.get("image_url") else ft.Text("-", size=LayoutConstants.FONT_SIZE_MD),
                    ],
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            f"{t('nomenclatures.form.plan_url')}:",
                            size=LayoutConstants.FONT_SIZE_MD,
                            weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                            width=150,
                        ),
                        ft.TextButton(
                            text=self._nomenclature.get("plan_url", "-") or "-",
                            url=self._nomenclature.get("plan_url", "#"),
                            disabled=not self._nomenclature.get("plan_url")
                        ) if self._nomenclature.get("plan_url") else ft.Text("-", size=LayoutConstants.FONT_SIZE_MD),
                    ],
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        urls_card = BaseCard(
            title=t("nomenclatures.form.urls"),
            icon=ft.Icons.LINK,
            content=urls_info,
        )
        # Sección BOM (Bill of Materials)
        bom_content = self._create_bom_tree()
        total_cost = self._calculate_total_cost()

        bom_section = BaseCard(
            title=t("nomenclatures.bom"),
            icon=ft.Icons.LIST_ALT,
            content=ft.Column(
                controls=[
                    bom_content,
                    ft.Divider(),
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"{t('product_detail.total_cost')}:",
                                size=LayoutConstants.FONT_SIZE_LG,
                                weight=LayoutConstants.FONT_WEIGHT_BOLD,
                            ),
                            ft.Text(
                                f"${total_cost:.2f}",
                                size=LayoutConstants.FONT_SIZE_LG,
                                weight=LayoutConstants.FONT_WEIGHT_BOLD,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
        )

        # Contenido
        controls = [
            header, 
            general_card, 
            designations_card,
            dimensions_card,
            stock_card,
            pricing_card,
            urls_card,
            bom_section
        ]

        content = ft.Column(
            controls=controls,
            spacing=LayoutConstants.SPACING_LG,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        return content

    def _create_info_row(self, label: str, value: str) -> ft.Row:
        """Crea una fila de información."""
        return ft.Row(
            controls=[
                ft.Text(
                    f"{label}:",
                    size=LayoutConstants.FONT_SIZE_MD,
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    width=150,
                ),
                ft.Text(
                    value,
                    size=LayoutConstants.FONT_SIZE_MD,
                    expand=True,
                ),
            ],
        )

    def _create_bom_tree(self) -> ft.Control:
        """Crea el árbol de componentes BOM."""
        if not self._bom_components:
            return ft.Container(
                content=ft.Text(
                    t("nomenclatures.no_components"),
                    size=LayoutConstants.FONT_SIZE_MD,
                    italic=True,
                ),
                padding=LayoutConstants.PADDING_MD,
            )

        # Crear tabla de componentes
        rows = []
        for comp in self._bom_components:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(comp.get("component_code", ""))),
                        ft.DataCell(ft.Text(comp.get("component_name", ""))),
                        ft.DataCell(ft.Text(str(comp.get("quantity", 0)))),
                        ft.DataCell(
                            ft.Text(f"${comp.get('unit_cost', 0):.2f}")
                        ),
                        ft.DataCell(
                            ft.Text(
                                f"${comp.get('quantity', 0) * comp.get('unit_cost', 0):.2f}"
                            )
                        ),
                    ],
                )
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(t("nomenclatures.columns.code"))),
                ft.DataColumn(ft.Text(t("nomenclatures.columns.name"))),
                ft.DataColumn(ft.Text(t("nomenclatures.columns.quantity"))),
                ft.DataColumn(ft.Text(t("nomenclatures.columns.unit_cost"))),
                ft.DataColumn(ft.Text(t("nomenclatures.columns.total_cost"))),
            ],
            rows=rows,
        )

        return ft.Container(
            content=table,
            border_radius=LayoutConstants.RADIUS_SM,
            padding=LayoutConstants.PADDING_SM,
        )

    def _calculate_total_cost(self) -> float:
        """Calcula el costo total del BOM."""
        total = 0.0
        for comp in self._bom_components:
            total += comp.get("quantity", 0) * comp.get("unit_cost", 0)
        return total

    def did_mount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.info("NomenclatureDetailView mounted")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        if self.page:
            self.page.run_task(self.load_nomenclature)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_nomenclature(self) -> None:
        """Carga los datos de la nomenclatura desde la API."""
        logger.info(f"Loading nomenclature ID={self.nomenclature_id}")
        self._is_loading = True
        self._error_message = ""

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            self._nomenclature = await product_api.get_by_id(self.nomenclature_id)

            # Cargar componentes BOM
            try:
                self._bom_components = await product_api.get_bom_components(
                    self.nomenclature_id
                )
            except Exception as e:
                logger.warning(f"Could not load BOM components: {e}")
                self._bom_components = []

            logger.success(f"Nomenclature loaded: {self._nomenclature.get('designation_es')}")
            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading nomenclature: {e}")
            self._error_message = f"Error al cargar nomenclatura: {str(e)}"
            self._is_loading = False

        # Reconstruir contenido con los datos cargados
        self.content = self.build()
        if self.page:
            self.update()

    def _on_edit_click(self, e: ft.ControlEvent) -> None:
        """Callback para editar la nomenclatura."""
        if self.on_edit:
            self.on_edit(self.nomenclature_id)

    def _on_delete_click(self, e: ft.ControlEvent) -> None:
        """Callback para eliminar la nomenclatura."""
        if self.page:
            confirm_dialog = ConfirmDialog(
                title=t("common.confirm_delete"),
                message=t("nomenclatures.messages.confirm_delete_message"),
                confirm_text=t("common.delete"),
                cancel_text=t("common.cancel"),
                on_confirm=self._on_confirm_delete,
                on_cancel=lambda: None,
                variant="danger",
            )
            confirm_dialog.show(self.page)

    def _on_confirm_delete(self) -> None:
        """Callback cuando se confirma la eliminación."""
        if self.on_delete:
            self.on_delete(self.nomenclature_id)

    def _on_back_click(self, e: ft.ControlEvent) -> None:
        """Callback para volver atrás."""
        if self.on_back:
            self.on_back()

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        logger.debug("NomenclatureDetailView state changed, rebuilding content")
        # Reconstruir el contenido con las nuevas traducciones
        self.content = self.build()
        if self.page:
            self.update()
