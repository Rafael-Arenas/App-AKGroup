"""
Vista de detalle de empresa.

Muestra información completa de una empresa con opciones de editar/eliminar.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import (
    BaseCard,
    LoadingSpinner,
    ErrorDisplay,
    ConfirmDialog,
)


class CompanyDetailView(ft.Container):
    """
    Vista de detalle de empresa.

    Args:
        company_id: ID de la empresa a mostrar
        on_edit: Callback cuando se edita la empresa
        on_delete: Callback cuando se elimina la empresa
        on_back: Callback para volver atrás

    Example:
        >>> detail = CompanyDetailView(
        ...     company_id=123,
        ...     on_edit=handle_edit,
        ...     on_delete=handle_delete,
        ... )
        >>> page.add(detail)
    """

    def __init__(
        self,
        company_id: int,
        on_edit: Callable[[int], None] | None = None,
        on_delete: Callable[[int], None] | None = None,
        on_back: Callable[[], None] | None = None,
    ):
        """Inicializa la vista de detalle de empresa."""
        super().__init__()
        self.company_id = company_id
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_back = on_back

        # Estado
        self._is_loading: bool = True
        self._error_message: str = ""
        self._company: dict | None = None
        self._confirm_dialog: ConfirmDialog | None = None

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = LayoutConstants.PADDING_LG

        # Construir contenido inicial (loading)
        self.content = self.build()

        logger.info(f"CompanyDetailView initialized: company_id={company_id}")

    def build(self) -> ft.Control:
        """
        Construye el componente de detalle de empresa.

        Returns:
            Control de Flet con la vista completa
        """
        if self._is_loading:
            return ft.Container(
                content=LoadingSpinner(message="Cargando empresa..."),
                expand=True,
                alignment=ft.alignment.center,
            )
        elif self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_company,
                ),
                expand=True,
                alignment=ft.alignment.center,
            )

        # Badges más pequeños
        status_badge = ft.Container(
            content=ft.Text(
                "Activa" if self._company.get("is_active") else "Inactiva",
                size=LayoutConstants.FONT_SIZE_XS,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.Colors.WHITE,
            ),
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_SM,
                vertical=LayoutConstants.PADDING_XS,
            ),
            border_radius=LayoutConstants.RADIUS_FULL,
            bgcolor=ft.Colors.GREEN if self._company.get("is_active") else ft.Colors.RED_400,
        )

        type_badge = ft.Container(
            content=ft.Text(
                self._format_company_type(self._company.get("company_type", "")),
                size=LayoutConstants.FONT_SIZE_XS,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.Colors.WHITE,
            ),
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_SM,
                vertical=LayoutConstants.PADDING_XS,
            ),
            border_radius=LayoutConstants.RADIUS_FULL,
            bgcolor=ft.Colors.BLUE,
        )

        # Header compacto con iconos de acción a la derecha
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        name=ft.Icons.BUSINESS,
                        size=LayoutConstants.ICON_SIZE_LG,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                self._company.get("name", ""),
                                size=LayoutConstants.FONT_SIZE_XL,
                                weight=LayoutConstants.FONT_WEIGHT_BOLD,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        self._company.get("trigram", ""),
                                        size=LayoutConstants.FONT_SIZE_MD,
                                    ),
                                    type_badge,
                                    status_badge,
                                ],
                                spacing=LayoutConstants.SPACING_SM,
                            ),
                        ],
                        spacing=LayoutConstants.SPACING_XS,
                        expand=True,
                    ),
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.EDIT_OUTLINED,
                                tooltip="Editar empresa",
                                on_click=self._on_edit_click,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Eliminar empresa",
                                on_click=self._on_delete_click,
                            ),
                        ],
                        spacing=LayoutConstants.SPACING_XS,
                    ),
                ],
                spacing=LayoutConstants.SPACING_MD,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=LayoutConstants.PADDING_MD,
            border=ft.border.all(1),
            border_radius=LayoutConstants.RADIUS_MD,
        )

        # Tarjeta de Información General
        general_info = ft.Column(
            controls=[
                self._create_info_row("Nombre Legal", self._company.get("name", "-")),
                self._create_info_row("Trigrama", self._company.get("trigram", "-")),
                self._create_info_row("Tipo", self._format_company_type(
                    self._company.get("company_type", "")
                )),
                self._create_info_row("Estado", "Activa" if self._company.get("is_active") else "Inactiva"),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        general_card = BaseCard(
            title="Información General",
            icon=ft.Icons.BUSINESS,
            content=general_info,
        )

        # Tarjeta de Información de Contacto
        contact_info = ft.Column(
            controls=[
                self._create_info_row("Teléfono", self._company.get("phone", "-")),
                self._create_info_row("Sitio Web", self._company.get("website", "-")),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        contact_card = BaseCard(
            title="Información de Contacto",
            icon=ft.Icons.CONTACT_PHONE,
            content=contact_info,
        )

        # Tarjeta de Ubicación
        location_info = ft.Column(
            controls=[
                self._create_info_row("País", self._company.get("country_name", "-")),
                self._create_info_row("Ciudad", self._company.get("city_name", "-")),
                self._create_info_row("Dirección Principal", self._company.get("main_address", "-")),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        location_card = BaseCard(
            title="Ubicación",
            icon=ft.Icons.LOCATION_ON,
            content=location_info,
        )

        # Tarjeta de Información Fiscal (si existe)
        fiscal_controls = []
        if self._company.get("intracommunity_number"):
            fiscal_controls.append(
                self._create_info_row("Número Intracomunitario", self._company.get("intracommunity_number"))
            )

        fiscal_card = None
        if fiscal_controls:
            fiscal_info = ft.Column(
                controls=fiscal_controls,
                spacing=LayoutConstants.SPACING_SM,
            )
            fiscal_card = BaseCard(
                title="Información Fiscal",
                icon=ft.Icons.RECEIPT_LONG,
                content=fiscal_info,
            )

        # Tarjeta de Metadatos
        created_by = self._company.get("created_by")
        updated_by = self._company.get("updated_by")

        metadata_info = ft.Column(
            controls=[
                self._create_info_row("Creada", self._format_datetime(self._company.get("created_at"))),
                self._create_info_row("Modificada", self._format_datetime(self._company.get("updated_at"))),
                self._create_info_row("Creada por (ID)", str(created_by) if created_by else "Sistema"),
                self._create_info_row("Modificada por (ID)", str(updated_by) if updated_by else "Sistema"),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        metadata_card = BaseCard(
            title="Información del Sistema",
            icon=ft.Icons.SCHEDULE,
            content=metadata_info,
            collapsible=True,
            initially_collapsed=True,
        )

        # Layout organizado
        cards = [
            header,
            general_card,
            contact_card,
            location_card,
        ]

        # Agregar tarjeta fiscal solo si existe
        if fiscal_card:
            cards.append(fiscal_card)

        cards.append(metadata_card)

        # Contenido principal con scroll
        content = ft.Column(
            controls=cards,
            spacing=LayoutConstants.SPACING_LG,
            scroll=ft.ScrollMode.AUTO,
        )

        return content

    def _create_info_row(self, label: str, value: str) -> ft.Container:
        """
        Crea una fila de información con mejor estilo.

        Args:
            label: Etiqueta del campo
            value: Valor del campo

        Returns:
            Container con label y value
        """
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(
                            label,
                            size=LayoutConstants.FONT_SIZE_MD,
                            weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                        ),
                        width=180,
                    ),
                    ft.Text(
                        value,
                        size=LayoutConstants.FONT_SIZE_MD,
                        selectable=True,
                    ),
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
            padding=ft.padding.symmetric(vertical=LayoutConstants.PADDING_XS),
        )

    def _format_company_type(self, type_code: str) -> str:
        """Formatea el tipo de empresa."""
        type_map = {
            "CLIENT": "Cliente",
            "SUPPLIER": "Proveedor",
            "BOTH": "Cliente/Proveedor",
        }
        return type_map.get(type_code, type_code)

    def _format_datetime(self, dt_str: str | None) -> str:
        """
        Formatea una fecha/hora para mostrar.

        Args:
            dt_str: String de fecha en formato ISO

        Returns:
            Fecha formateada o "-"
        """
        if not dt_str:
            return "-"

        try:
            from datetime import datetime
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            return dt_str

    def did_mount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.info("CompanyDetailView mounted, loading company")

        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)

        if self.page:
            self.page.run_task(self.load_company)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        logger.info("CompanyDetailView unmounting")
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_company(self) -> None:
        """Carga los datos de la empresa desde la API."""
        logger.info(f"Loading company ID={self.company_id}")
        self._is_loading = True
        self._error_message = ""

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import CompanyAPI

            company_api = CompanyAPI()
            self._company = await company_api.get_by_id(self.company_id)

            logger.success(f"Company loaded: {self._company.get('name')}")
            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading company: {e}")
            self._error_message = f"Error al cargar empresa: {str(e)}"
            self._is_loading = False

        # Reconstruir contenido con los datos cargados
        self.content = self.build()
        if self.page:
            self.update()

    def _on_edit_click(self, e: ft.ControlEvent) -> None:
        """Callback para editar la empresa."""
        logger.info(f"Edit clicked for company ID={self.company_id}")
        if self.on_edit:
            self.on_edit(self.company_id)

    def _on_delete_click(self, e: ft.ControlEvent) -> None:
        """Callback para eliminar la empresa."""
        logger.info(f"Delete clicked for company ID={self.company_id}")

        self._confirm_dialog = ConfirmDialog(
            title="Eliminar Empresa",
            message=f"¿Está seguro de que desea eliminar la empresa '{self._company.get('name')}'?",
            on_confirm=self._confirm_delete,
        )

        if self.page:
            self.page.dialog = self._confirm_dialog
            self._confirm_dialog.open = True
            self.page.update()

    async def _confirm_delete(self) -> None:
        """Confirma y ejecuta la eliminación."""
        try:
            from src.frontend.services.api import CompanyAPI

            company_api = CompanyAPI()
            await company_api.delete(self.company_id)

            logger.success(f"Company {self.company_id} deleted")

            if self.on_delete:
                self.on_delete(self.company_id)

        except Exception as e:
            logger.exception(f"Error deleting company: {e}")

    def _on_back_click(self, e: ft.ControlEvent) -> None:
        """Callback para volver atrás."""
        logger.info("Back button clicked")
        if self.on_back:
            self.on_back()

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        if self.page:
            self.update()
