"""
Vista de detalle de empresa.

Muestra información completa de una empresa con opciones de editar/eliminar.
"""
from typing import Callable
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.color_constants import ColorConstants
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

        logger.info(f"CompanyDetailView initialized: company_id={company_id}")

    def build(self) -> ft.Control:
        """
        Construye el componente de detalle de empresa.

        Returns:
            Control de Flet con la vista completa
        """
        is_dark = app_state.theme.is_dark_mode

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

        # Header con nombre y acciones
        status_badge = ft.Container(
            content=ft.Text(
                "Activa" if self._company.get("is_active") else "Inactiva",
                size=LayoutConstants.FONT_SIZE_SM,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.Colors.WHITE,
            ),
            bgcolor=(
                ColorConstants.SUCCESS
                if self._company.get("is_active")
                else ColorConstants.ERROR
            ),
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_SM,
                vertical=LayoutConstants.PADDING_XS,
            ),
            border_radius=LayoutConstants.RADIUS_SM,
        )

        header = ft.Row(
            controls=[
                ft.Icon(
                    name=ft.Icons.BUSINESS,
                    color=ColorConstants.PRIMARY,
                    size=LayoutConstants.ICON_SIZE_XL,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            self._company.get("name", ""),
                            size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                            weight=LayoutConstants.FONT_WEIGHT_BOLD,
                            color=ColorConstants.get_color_for_theme("ON_SURFACE", is_dark),
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f"Trigrama: {self._company.get('trigram', '')}",
                                    size=LayoutConstants.FONT_SIZE_MD,
                                    color=ColorConstants.get_color_for_theme(
                                        "ON_SURFACE_VARIANT", is_dark
                                    ),
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
                            tooltip="Editar",
                            on_click=self._on_edit_click,
                            bgcolor=ColorConstants.PRIMARY,
                            icon_color=ft.Colors.WHITE,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            tooltip="Eliminar",
                            on_click=self._on_delete_click,
                            bgcolor=ColorConstants.ERROR,
                            icon_color=ft.Colors.WHITE,
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_SM,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Tarjeta con información completa
        info_content = ft.Column(
            controls=[
                self._create_info_row("Tipo", self._format_company_type(
                    self._company.get("company_type", "")
                )),
                ft.Divider(),
                self._create_info_row("Teléfono", self._company.get("phone", "-")),
                self._create_info_row("Email", self._company.get("email", "-")),
                self._create_info_row("Sitio Web", self._company.get("website", "-")),
                ft.Divider(),
                self._create_info_row("País", self._company.get("country_name", "-")),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        info_card = BaseCard(
            title="Información de la Empresa",
            icon=ft.Icons.INFO_OUTLINED,
            content=info_content,
        )

        # Botón volver
        back_button = ft.TextButton(
            text="Volver",
            icon=ft.Icons.ARROW_BACK,
            on_click=self._on_back_click,
        )

        # Contenido principal
        content = ft.Column(
            controls=[
                back_button,
                header,
                info_card,
            ],
            spacing=LayoutConstants.SPACING_LG,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        return content

    def _create_info_row(self, label: str, value: str) -> ft.Row:
        """
        Crea una fila de información.

        Args:
            label: Etiqueta del campo
            value: Valor del campo

        Returns:
            Row con label y value
        """
        is_dark = app_state.theme.is_dark_mode

        return ft.Row(
            controls=[
                ft.Text(
                    f"{label}:",
                    size=LayoutConstants.FONT_SIZE_MD,
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    color=ColorConstants.get_color_for_theme("ON_SURFACE", is_dark),
                    width=150,
                ),
                ft.Text(
                    value,
                    size=LayoutConstants.FONT_SIZE_MD,
                    color=ColorConstants.get_color_for_theme(
                        "ON_SURFACE_VARIANT", is_dark
                    ),
                    expand=True,
                ),
            ],
        )

    def _format_company_type(self, type_code: str) -> str:
        """Formatea el tipo de empresa."""
        type_map = {
            "CLIENT": "Cliente",
            "SUPPLIER": "Proveedor",
            "BOTH": "Cliente/Proveedor",
        }
        return type_map.get(type_code, type_code)

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
