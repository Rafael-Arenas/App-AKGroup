"""
Vista de detalle de personal (Staff).

Muestra información completa de un usuario del sistema con opciones de editar/eliminar.
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
from src.frontend.i18n.translation_manager import t


class StaffDetailView(ft.Container):
    """
    Vista de detalle de personal.

    Args:
        staff_id: ID del personal a mostrar
        on_edit: Callback cuando se edita el personal
        on_delete: Callback cuando se elimina el personal
        on_back: Callback para volver atrás

    Example:
        >>> detail = StaffDetailView(
        ...     staff_id=123,
        ...     on_edit=handle_edit,
        ...     on_delete=handle_delete,
        ... )
        >>> page.add(detail)
    """

    def __init__(
        self,
        staff_id: int,
        on_edit: Callable[[int], None] | None = None,
        on_delete: Callable[[int], None] | None = None,
        on_back: Callable[[], None] | None = None,
    ):
        """Inicializa la vista de detalle de personal."""
        super().__init__()
        self.staff_id = staff_id
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_back = on_back

        # Estado
        self._is_loading: bool = True
        self._error_message: str = ""
        self._staff: dict | None = None
        self._confirm_dialog: ConfirmDialog | None = None

        # Configurar propiedades del contenedor
        self.expand = True
        self.padding = LayoutConstants.PADDING_LG

        # Construir contenido inicial (loading)
        self.content = self.build()

        logger.info(f"StaffDetailView initialized: staff_id={staff_id}")

    def build(self) -> ft.Control:
        """
        Construye el componente de detalle de personal.

        Returns:
            Control de Flet con la vista completa
        """
        if self._is_loading:
            return ft.Container(
                content=LoadingSpinner(message=t("staff.messages.loading")),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )
        elif self._error_message:
            return ft.Container(
                content=ErrorDisplay(
                    message=self._error_message,
                    on_retry=self.load_staff,
                ),
                expand=True,
                alignment=ft.Alignment(0, 0),
            )

        # Badges de estado y rol
        status_badge = ft.Container(
            content=ft.Text(
                t("common.active") if self._staff.get("is_active") else t("common.inactive"),
                size=LayoutConstants.FONT_SIZE_XS,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.Colors.WHITE,
            ),
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_SM,
                vertical=LayoutConstants.PADDING_XS,
            ),
            border_radius=LayoutConstants.RADIUS_FULL,
            bgcolor=ft.Colors.GREEN if self._staff.get("is_active") else ft.Colors.RED_400,
        )

        role_badge = ft.Container(
            content=ft.Text(
                t("staff.role.admin") if self._staff.get("is_admin") else t("staff.role.user"),
                size=LayoutConstants.FONT_SIZE_XS,
                weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                color=ft.Colors.WHITE,
            ),
            padding=ft.padding.symmetric(
                horizontal=LayoutConstants.PADDING_SM,
                vertical=LayoutConstants.PADDING_XS,
            ),
            border_radius=LayoutConstants.RADIUS_FULL,
            bgcolor=ft.Colors.PURPLE if self._staff.get("is_admin") else ft.Colors.BLUE,
        )

        # Nombre completo
        full_name = f"{self._staff.get('first_name', '')} {self._staff.get('last_name', '')}".strip()

        # Header con iconos de acción
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.BADGE,
                        size=LayoutConstants.ICON_SIZE_LG,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(
                                full_name,
                                size=LayoutConstants.FONT_SIZE_XL,
                                weight=LayoutConstants.FONT_WEIGHT_BOLD,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        f"@{self._staff.get('username', '')}",
                                        size=LayoutConstants.FONT_SIZE_MD,
                                        color=ft.Colors.GREY_600,
                                    ),
                                    role_badge,
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
                                tooltip=t("staff.actions.edit"),
                                on_click=self._on_edit_click,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip=t("staff.actions.delete"),
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

        # Tarjeta de Información Personal
        personal_info = ft.Column(
            controls=[
                self._create_info_row(t("staff.fields.first_name"), self._staff.get("first_name", "-")),
                self._create_info_row(t("staff.fields.last_name"), self._staff.get("last_name", "-")),
                self._create_info_row(t("staff.fields.username"), self._staff.get("username", "-")),
                self._create_info_row(t("staff.fields.trigram"), self._staff.get("trigram") or "-"),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        personal_card = BaseCard(
            title=t("staff.sections.personal_info"),
            icon=ft.Icons.PERSON,
            content=personal_info,
        )

        # Tarjeta de Información de Contacto
        contact_info = ft.Column(
            controls=[
                self._create_info_row(t("staff.fields.email"), self._staff.get("email", "-")),
                self._create_info_row(t("staff.fields.phone"), self._staff.get("phone") or "-"),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        contact_card = BaseCard(
            title=t("staff.sections.contact_info"),
            icon=ft.Icons.CONTACT_MAIL,
            content=contact_info,
        )

        # Tarjeta de Información Laboral
        work_info = ft.Column(
            controls=[
                self._create_info_row(t("staff.fields.position"), self._staff.get("position") or "-"),
                self._create_info_row(
                    t("staff.fields.role"),
                    t("staff.role.admin") if self._staff.get("is_admin") else t("staff.role.user")
                ),
                self._create_info_row(
                    t("staff.fields.status"),
                    t("common.active") if self._staff.get("is_active") else t("common.inactive")
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        work_card = BaseCard(
            title=t("staff.sections.work_info"),
            icon=ft.Icons.WORK,
            content=work_info,
        )

        # Tarjeta de Auditoría
        audit_info = ft.Column(
            controls=[
                self._create_info_row(t("staff.fields.created_at"), self._format_date(self._staff.get("created_at"))),
                self._create_info_row(t("staff.fields.updated_at"), self._format_date(self._staff.get("updated_at"))),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        audit_card = BaseCard(
            title=t("staff.sections.audit_info"),
            icon=ft.Icons.HISTORY,
            content=audit_info,
            collapsible=True,
            initially_collapsed=True,
        )

        # Layout
        cards = [
            header,
            personal_card,
            contact_card,
            work_card,
            audit_card,
        ]

        # Contenido principal con scroll
        content = ft.Column(
            controls=cards,
            spacing=LayoutConstants.SPACING_LG,
            scroll=ft.ScrollMode.AUTO,
        )

        return content

    def _create_info_row(self, label: str, value: str) -> ft.Control:
        """
        Crea una fila de información label: value.

        Args:
            label: Etiqueta del campo
            value: Valor del campo

        Returns:
            Control de Flet con la fila
        """
        return ft.Row(
            controls=[
                ft.Text(
                    f"{label}:",
                    size=LayoutConstants.FONT_SIZE_SM,
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    width=150,
                ),
                ft.Text(
                    value,
                    size=LayoutConstants.FONT_SIZE_SM,
                    expand=True,
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

    def _format_date(self, date_str: str | None) -> str:
        """
        Formatea una fecha ISO a formato legible.

        Args:
            date_str: Fecha en formato ISO

        Returns:
            Fecha formateada o "-" si es None
        """
        if not date_str:
            return "-"
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%d/%m/%Y %H:%M")
        except Exception:
            return date_str

    def did_mount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.info(f"StaffDetailView mounted, loading staff {self.staff_id}")

        app_state.theme.add_observer(self._on_state_changed)
        app_state.i18n.add_observer(self._on_state_changed)

        if self.page:
            self.page.run_task(self.load_staff)

    def will_unmount(self) -> None:
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        logger.info("StaffDetailView unmounting")
        app_state.theme.remove_observer(self._on_state_changed)
        app_state.i18n.remove_observer(self._on_state_changed)

    async def load_staff(self) -> None:
        """Carga los datos del personal desde la API."""
        logger.info(f"Loading staff data for ID={self.staff_id}")

        self._is_loading = True
        self._error_message = ""

        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import StaffAPI

            staff_api = StaffAPI()
            self._staff = await staff_api.get_by_id(self.staff_id)

            logger.success(f"Staff loaded: {self._staff.get('username')}")

            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading staff: {e}")
            self._error_message = t("staff.messages.error_loading").replace("{error}", str(e))
            self._is_loading = False

        self.content = self.build()
        if self.page:
            self.update()

    def _on_edit_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace clic en editar."""
        logger.info(f"Edit staff clicked: ID={self.staff_id}")
        if self.on_edit:
            self.on_edit(self.staff_id)

    def _on_delete_click(self, e: ft.ControlEvent) -> None:
        """Callback cuando se hace clic en eliminar."""
        logger.info(f"Delete staff clicked: ID={self.staff_id}")

        staff_name = f"{self._staff.get('first_name', '')} {self._staff.get('last_name', '')}".strip()

        self._confirm_dialog = ConfirmDialog(
            title=t("staff.delete"),
            message=t("staff.messages.delete_confirm").replace("{name}", staff_name),
            on_confirm=lambda: self._confirm_delete(),
        )

        if self.page:
            self.page.dialog = self._confirm_dialog
            self._confirm_dialog.open = True
            self.page.update()

    async def _confirm_delete(self) -> None:
        """Confirma y ejecuta la eliminación."""
        logger.info(f"Confirming deletion of staff ID={self.staff_id}")

        try:
            from src.frontend.services.api import StaffAPI

            staff_api = StaffAPI()
            await staff_api.delete(self.staff_id)

            logger.success(f"Staff {self.staff_id} deleted successfully")

            if self.on_delete:
                self.on_delete(self.staff_id)

        except Exception as e:
            logger.exception(f"Error deleting staff: {e}")

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado de tema o idioma."""
        logger.debug("StaffDetailView state changed, rebuilding content")
        self.content = self.build()
        if self.page:
            self.update()
