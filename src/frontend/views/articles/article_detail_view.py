"""
Vista de detalle de artículo.

Muestra información completa de un artículo.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t
from src.frontend.components.common import BaseCard, LoadingSpinner, ErrorDisplay, ConfirmDialog


class ArticleDetailView(ft.Container):
    """
    Vista de detalle de artículo.

    Args:
        article_id: ID del artículo a mostrar
        on_edit: Callback cuando se edita el artículo
        on_delete: Callback cuando se elimina el artículo
        on_back: Callback para volver atrás

    Example:
        >>> detail = ArticleDetailView(article_id=123, on_edit=handle_edit)
        >>> page.add(detail)
    """

    def __init__(
        self,
        article_id: int,
        on_edit: Callable[[int], None] | None = None,
        on_delete: Callable[[int], None] | None = None,
        on_back: Callable[[], None] | None = None,
    ):
        """Inicializa la vista de detalle de artículo."""
        super().__init__()
        self.article_id = article_id
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_back = on_back

        self._is_loading: bool = True
        self._error_message: str = ""
        self._article: dict | None = None

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = LayoutConstants.PADDING_LG

        # Construir contenido inicial (loading)
        self.content = self.build()

        logger.info(f"ArticleDetailView initialized: article_id={article_id}")

    def build(self) -> ft.Control:
        """Construye el componente de detalle de artículo."""
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
                    on_retry=self.load_article,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )

        # Badge de estado
        status_badge = ft.Container(
            content=ft.Text(
                t("common.active") if self._article.get("is_active") else t("common.inactive"),
                size=LayoutConstants.FONT_SIZE_SM,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.Colors.WHITE,
            ),
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_SM,
                vertical=LayoutConstants.PADDING_XS,
            ),
            border_radius=LayoutConstants.RADIUS_SM,
            bgcolor=ft.Colors.GREEN if self._article.get("is_active") else ft.Colors.RED,
        )

        # Header
        header = ft.Row(
            controls=[
                ft.Icon(
                    name=ft.Icons.INVENTORY_2,
                    size=LayoutConstants.ICON_SIZE_XL,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            self._article.get("designation_es", ""),
                            size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                            weight=LayoutConstants.FONT_WEIGHT_BOLD,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f"Código: {self._article.get('reference', '')}",
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

        # Información general del artículo
        general_info = ft.Column(
            controls=[
                self._create_info_row(t("articles.form.reference"), self._article.get("reference", "-") or "-"),
                self._create_info_row(t("articles.form.supplier_reference"), self._article.get("supplier_reference", "-") or "-"),
                self._create_info_row(t("articles.form.revision"), self._article.get("revision", "-") or "-"),
                self._create_info_row(t("articles.form.designation_es"), self._article.get("designation_es", "-") or "-"),
                self._create_info_row(t("articles.form.description"), self._article.get("short_designation", "-") or "-"),
                self._create_info_row(t("articles.form.family_type"), self._article.get("family_type", {}).get("name", "-") if self._article.get("family_type") else "-"),
                self._create_info_row(t("articles.form.matter"), self._article.get("matter", {}).get("name", "-") if self._article.get("matter") else "-"),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        general_card = BaseCard(
            title=t("articles.form.basic_info"),
            icon=ft.Icons.INFO_OUTLINED,
            content=general_info,
        )

        # Designaciones en inglés y francés (adicional)
        designations_info = ft.Column(
            controls=[
                self._create_info_row(t("articles.form.designation_en"), self._article.get("designation_en", "-") or "-"),
                self._create_info_row(t("articles.form.designation_fr"), self._article.get("designation_fr", "-") or "-"),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        designations_card = BaseCard(
            title=t("nomenclatures.form.additional_designations"),
            icon=ft.Icons.TRANSLATE,
            content=designations_info,
        )

        # Dimensiones y peso
        dimensions_info = ft.Column(
            controls=[
                self._create_info_row(t("articles.form.length"), f"{float(self._article.get('length', 0) or 0):.3f} mm"),
                self._create_info_row(t("articles.form.width"), f"{float(self._article.get('width', 0) or 0):.3f} mm"),
                self._create_info_row(t("articles.form.height"), f"{float(self._article.get('height', 0) or 0):.3f} mm"),
                self._create_info_row(t("articles.form.volume"), f"{float(self._article.get('volume', 0) or 0):.6f} m³"),
                self._create_info_row(t("articles.form.net_weight"), f"{float(self._article.get('net_weight', 0) or 0):.3f} kg"),
                self._create_info_row(t("articles.form.gross_weight"), f"{float(self._article.get('gross_weight', 0) or 0):.3f} kg"),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        dimensions_card = BaseCard(
            title=t("articles.form.dimensions_section"),
            icon=ft.Icons.STRAIGHTEN,
            content=dimensions_info,
        )

        # Información de precios
        pricing_info = ft.Column(
            controls=[
                self._create_info_row(
                    t("product_detail.purchase_price"), f"${float(self._article.get('purchase_price', 0) or 0):.2f}"
                ),
                self._create_info_row(
                    t("articles.form.cost_price"), f"${float(self._article.get('cost_price', 0) or 0):.2f}"
                ),
                self._create_info_row(
                    t("articles.form.sale_price"), f"${float(self._article.get('sale_price', 0) or 0):.2f}"
                ),
                self._create_info_row(
                    t("product_detail.sale_price_eur"), f"€{float(self._article.get('sale_price_eur', 0) or 0):.2f}"
                ),
                self._create_info_row(
                    t("product_detail.margin_percentage"), f"{float(self._article.get('margin_percentage', 0) or 0):.1f}%"
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        pricing_card = BaseCard(
            title=t("articles.form.pricing"),
            icon=ft.Icons.ATTACH_MONEY,
            content=pricing_info,
        )

        # Información de stock
        stock_info = ft.Column(
            controls=[
                self._create_info_row(
                    t("articles.form.stock_quantity"), f"{float(self._article.get('stock_quantity', 0) or 0):.3f}"
                ),
                self._create_info_row(
                    t("articles.form.min_stock"), f"{float(self._article.get('minimum_stock', 0) or 0):.3f}"
                ),
                self._create_info_row(
                    t("articles.form.stock_location"), self._article.get("stock_location", "-") or "-"
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        stock_card = BaseCard(
            title=t("articles.form.stock_section"),
            icon=ft.Icons.INVENTORY,
            content=stock_info,
        )

        # Información logística y aduanas
        logistics_info = ft.Column(
            controls=[
                self._create_info_row(
                    t("articles.form.country_of_origin"),
                    self._get_country_name(self._article.get("country_of_origin")),
                ),
                self._create_info_row(
                    t("articles.form.customs_number"),
                    self._article.get("customs_number", "-") or "-",
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        logistics_card = BaseCard(
            title=t("articles.form.logistics_section"),
            icon=ft.Icons.LOCAL_SHIPPING,
            content=logistics_info,
        )

        # Recursos (URLs)
        resources_info = ft.Column(
            controls=[
                self._create_link_row(
                    t("articles.form.image_url"), self._article.get("image_url")
                ),
                self._create_link_row(
                    t("articles.form.plan_url"), self._article.get("plan_url")
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        resources_card = BaseCard(
            title=t("articles.form.resources_section"),
            icon=ft.Icons.LINK,
            content=resources_info,
        )

        # Información adicional
        additional_info = ft.Column(
            controls=[
                ft.Text(
                    self._article.get("notes", "-") or "-",
                    size=LayoutConstants.FONT_SIZE_MD,
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        additional_card = BaseCard(
            title=t("articles.form.additional_section"),
            icon=ft.Icons.NOTE,
            content=additional_info,
        )

        controls = [
            header,
            general_card,
            designations_card,
            dimensions_card,
            stock_card,
            pricing_card,
            logistics_card,
            resources_card,
            additional_card,
        ]

        content = ft.Column(
            controls=controls,
            spacing=LayoutConstants.SPACING_LG,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        return content

    def _create_link_row(self, label: str, url: str | None) -> ft.Row:
        """Crea una fila con un enlace."""
        if not url:
            return self._create_info_row(label, "-")
            
        return ft.Row(
            controls=[
                ft.Text(
                    f"{label}:",
                    size=LayoutConstants.FONT_SIZE_MD,
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    width=150,
                ),
                ft.Text(
                    url,
                    size=LayoutConstants.FONT_SIZE_MD,
                    color=ft.Colors.BLUE,
                    spans=[ft.TextSpan(url, url=url)],
                    overflow=ft.TextOverflow.ELLIPSIS,
                    expand=True,
                ),
                ft.IconButton(
                    icon=ft.Icons.OPEN_IN_NEW,
                    tooltip=t("common.open_link"),
                    url=url,
                    icon_size=20,
                )
            ],
        )

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

    def _get_country_name(self, country_code: str | None) -> str:
        """Convierte el código de país de 2 letras al nombre completo del país."""
        if not country_code or country_code == "None":
            return "-"
        
        # Mapeo de códigos de país a nombres completos
        code_to_name = {
            "CL": "Chile",
            "CN": "China",
            "DE": "Alemania",
            "ES": "España",
            "FR": "Francia",
            "GB": "Reino Unido",
            "IT": "Italia",
            "US": "Estados Unidos",
            "AR": "Argentina",
            "BR": "Brasil",
            "CO": "Colombia",
            "MX": "México",
            "PE": "Perú",
            "UY": "Uruguay",
            "VE": "Venezuela",
            "CA": "Canadá",
            "IN": "India",
            "JP": "Japón",
            "KR": "Corea del Sur",
            "TW": "Taiwán",
            "AU": "Australia",
            "NZ": "Nueva Zelanda",
            "ZA": "Sudáfrica",
            "EG": "Egipto",
            "MA": "Marruecos",
            "NG": "Nigeria",
            "RU": "Rusia",
            "TR": "Turquía",
            "AT": "Austria",
            "BE": "Bélgica",
            "DK": "Dinamarca",
            "FI": "Finlandia",
            "GR": "Grecia",
            "IE": "Irlanda",
            "NL": "Países Bajos",
            "NO": "Noruega",
            "PL": "Polonia",
            "PT": "Portugal",
            "SE": "Suecia",
            "CH": "Suiza",
            "CZ": "República Checa",
            "HU": "Hungría",
            "RO": "Rumanía",
            "SK": "Eslovaquia",
            "SI": "Eslovenia",
            "BG": "Bulgaria",
            "HR": "Croacia",
            "EE": "Estonia",
            "LV": "Letonia",
            "LT": "Lituania",
            "IS": "Islandia",
            "LU": "Luxemburgo",
            "MT": "Malta",
            "CY": "Chipre",
        }
        
        return code_to_name.get(country_code.upper(), country_code)

    def did_mount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.info("ArticleDetailView mounted")
        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)
        if self.page:
            self.page.run_task(self.load_article)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_article(self) -> None:
        """Carga los datos del artículo desde la API."""
        logger.info(f"Loading article ID={self.article_id}")
        self._is_loading = True
        self._error_message = ""

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import ProductAPI

            product_api = ProductAPI()
            self._article = await product_api.get_by_id(self.article_id)
            
            # Debug logging para verificar los datos del artículo
            logger.debug(f"Article data received: {self._article}")
            logger.debug(f"Country of origin value: '{self._article.get('country_of_origin')}'")

            logger.success(f"Article loaded: {self._article.get('designation_es')}")
            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading article: {e}")
            self._error_message = f"Error al cargar artículo: {str(e)}"
            self._is_loading = False

        # Reconstruir contenido con los datos cargados
        self.content = self.build()
        if self.page:
            self.update()

    def _on_edit_click(self, e: ft.ControlEvent) -> None:
        """Callback para editar el artículo."""
        if self.on_edit:
            self.on_edit(self.article_id)

    def _on_delete_click(self, e: ft.ControlEvent) -> None:
        """Callback para eliminar el artículo."""
        if self.page:
            confirm_dialog = ConfirmDialog(
                title=t("common.confirm_delete"),
                message=t("articles.messages.confirm_delete_message"),
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
            self.on_delete(self.article_id)

    def _on_back_click(self, e: ft.ControlEvent) -> None:
        """Callback para volver atrás."""
        if self.on_back:
            self.on_back()

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        logger.debug("ArticleDetailView state changed, rebuilding content")
        # Reconstruir el contenido con las nuevas traducciones
        self.content = self.build()
        if self.page:
            self.update()
