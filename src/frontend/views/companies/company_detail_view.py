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
# Los diálogos de direcciones y contactos se crean inline usando controles nativos de Flet


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
        self._addresses: list[dict] = []
        self._contacts: list[dict] = []
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

        # Tarjetas de Direcciones y Contactos
        addresses_card = BaseCard(
            title="Direcciones",
            icon=ft.Icons.LOCATION_ON,
            content=self._create_addresses_section(),
            collapsible=True,
            initially_collapsed=False,
        )
        cards.append(addresses_card)

        contacts_card = BaseCard(
            title="Contactos",
            icon=ft.Icons.CONTACTS,
            content=self._create_contacts_section(),
            collapsible=True,
            initially_collapsed=False,
        )
        cards.append(contacts_card)

        # Contenido principal con scroll
        content = ft.Column(
            controls=cards,
            spacing=LayoutConstants.SPACING_LG,
            scroll=ft.ScrollMode.AUTO,
        )

        return content

    def _create_addresses_section(self) -> ft.Control:
        """
        Crea la sección de direcciones con lista de cards.

        Returns:
            Control con la lista de direcciones
        """
        if not self._addresses:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            name=ft.Icons.LOCATION_OFF,
                            size=LayoutConstants.ICON_SIZE_LG,
                            color=ft.Colors.GREY_400,
                        ),
                        ft.Text(
                            "No hay direcciones registradas",
                            size=LayoutConstants.FONT_SIZE_MD,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.ElevatedButton(
                            text="Agregar Primera Dirección",
                            icon=ft.Icons.ADD,
                            on_click=self._on_add_address,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=LayoutConstants.SPACING_SM,
                ),
                padding=LayoutConstants.PADDING_MD,
                alignment=ft.alignment.center,
            )

        # Lista de direcciones
        address_cards = []
        for addr in self._addresses:
            address_type_labels = {
                "delivery": "Entrega",
                "billing": "Facturación",
                "headquarters": "Sede Principal",
                "branch": "Sucursal",
            }
            type_label = address_type_labels.get(addr.get("address_type", ""), addr.get("address_type", ""))

            # Badge de tipo y default
            badges = [
                ft.Container(
                    content=ft.Text(
                        type_label,
                        size=LayoutConstants.FONT_SIZE_XS,
                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                        color=ft.Colors.WHITE,
                    ),
                    padding=ft.padding.symmetric(
                        horizontal=LayoutConstants.PADDING_SM,
                        vertical=2,
                    ),
                    border_radius=LayoutConstants.RADIUS_FULL,
                    bgcolor=ft.Colors.BLUE_700,
                )
            ]

            if addr.get("is_default"):
                badges.append(
                    ft.Container(
                        content=ft.Text(
                            "Principal",
                            size=LayoutConstants.FONT_SIZE_XS,
                            weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                            color=ft.Colors.WHITE,
                        ),
                        padding=ft.padding.symmetric(
                            horizontal=LayoutConstants.PADDING_SM,
                            vertical=2,
                        ),
                        border_radius=LayoutConstants.RADIUS_FULL,
                        bgcolor=ft.Colors.GREEN,
                    )
                )

            address_card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    name=ft.Icons.LOCATION_ON,
                                    size=LayoutConstants.ICON_SIZE_MD,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=badges,
                                            spacing=LayoutConstants.SPACING_XS,
                                        ),
                                        ft.Text(
                                            addr.get("address", "-"),
                                            size=LayoutConstants.FONT_SIZE_MD,
                                            weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                                        ),
                                        ft.Text(
                                            f"{addr.get('city', '')} {addr.get('postal_code', '')}".strip() or "-",
                                            size=LayoutConstants.FONT_SIZE_SM,
                                            color=ft.Colors.GREY_700,
                                        ),
                                        ft.Text(
                                            addr.get("country", "-"),
                                            size=LayoutConstants.FONT_SIZE_SM,
                                            color=ft.Colors.GREY_700,
                                        ),
                                    ],
                                    spacing=LayoutConstants.SPACING_XS,
                                    expand=True,
                                ),
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.Icons.EDIT_OUTLINED,
                                            icon_size=LayoutConstants.ICON_SIZE_SM,
                                            tooltip="Editar dirección",
                                            on_click=lambda e, a=addr: self._on_edit_address(e, a),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            icon_size=LayoutConstants.ICON_SIZE_SM,
                                            tooltip="Eliminar dirección",
                                            on_click=lambda e, a=addr: self._on_delete_address(e, a),
                                        ),
                                    ],
                                    spacing=0,
                                ),
                            ],
                            spacing=LayoutConstants.SPACING_SM,
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_XS,
                ),
                padding=LayoutConstants.PADDING_MD,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=LayoutConstants.RADIUS_SM,
            )
            address_cards.append(address_card)

        # Botón para agregar nueva dirección
        add_button = ft.ElevatedButton(
            text="Agregar Dirección",
            icon=ft.Icons.ADD,
            on_click=self._on_add_address,
        )

        return ft.Column(
            controls=[
                *address_cards,
                ft.Container(
                    content=add_button,
                    padding=ft.padding.only(top=LayoutConstants.PADDING_SM),
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

    def _create_contacts_section(self) -> ft.Control:
        """
        Crea la sección de contactos con mini tabla.

        Returns:
            Control con la tabla de contactos
        """
        if not self._contacts:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            name=ft.Icons.CONTACTS_OUTLINED,
                            size=LayoutConstants.ICON_SIZE_LG,
                            color=ft.Colors.GREY_400,
                        ),
                        ft.Text(
                            "No hay contactos registrados",
                            size=LayoutConstants.FONT_SIZE_MD,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.ElevatedButton(
                            text="Agregar Primer Contacto",
                            icon=ft.Icons.ADD,
                            on_click=self._on_add_contact,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=LayoutConstants.SPACING_SM,
                ),
                padding=LayoutConstants.PADDING_MD,
                alignment=ft.alignment.center,
            )

        # Tabla de contactos
        contact_rows = []
        for contact in self._contacts:
            # Badge de activo/inactivo
            status_badge = ft.Container(
                content=ft.Text(
                    "Activo" if contact.get("is_active") else "Inactivo",
                    size=LayoutConstants.FONT_SIZE_XS,
                    color=ft.Colors.WHITE,
                ),
                padding=ft.padding.symmetric(
                    horizontal=LayoutConstants.PADDING_SM,
                    vertical=2,
                ),
                border_radius=LayoutConstants.RADIUS_FULL,
                bgcolor=ft.Colors.GREEN if contact.get("is_active") else ft.Colors.RED_400,
            )

            contact_row = ft.Container(
                content=ft.Row(
                    controls=[
                        # Nombre
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        f"{contact.get('first_name', '')} {contact.get('last_name', '')}",
                                        size=LayoutConstants.FONT_SIZE_MD,
                                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                                    ),
                                    ft.Text(
                                        contact.get("position", "-"),
                                        size=LayoutConstants.FONT_SIZE_SM,
                                        color=ft.Colors.GREY_700,
                                    ),
                                ],
                                spacing=2,
                            ),
                            width=200,
                        ),
                        # Email y teléfono
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.EMAIL, size=14, color=ft.Colors.GREY_600),
                                            ft.Text(
                                                contact.get("email", "-"),
                                                size=LayoutConstants.FONT_SIZE_SM,
                                            ),
                                        ],
                                        spacing=LayoutConstants.SPACING_XS,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.PHONE, size=14, color=ft.Colors.GREY_600),
                                            ft.Text(
                                                contact.get("phone") or contact.get("mobile", "-"),
                                                size=LayoutConstants.FONT_SIZE_SM,
                                            ),
                                        ],
                                        spacing=LayoutConstants.SPACING_XS,
                                    ),
                                ],
                                spacing=2,
                            ),
                            expand=True,
                        ),
                        # Status y acciones
                        ft.Row(
                            controls=[
                                status_badge,
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_size=LayoutConstants.ICON_SIZE_SM,
                                    tooltip="Editar contacto",
                                    on_click=lambda e, c=contact: self._on_edit_contact(e, c),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=LayoutConstants.ICON_SIZE_SM,
                                    tooltip="Eliminar contacto",
                                    on_click=lambda e, c=contact: self._on_delete_contact(e, c),
                                ),
                            ],
                            spacing=LayoutConstants.SPACING_XS,
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_MD,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                padding=LayoutConstants.PADDING_SM,
                border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
            )
            contact_rows.append(contact_row)

        # Botón para agregar nuevo contacto
        add_button = ft.ElevatedButton(
            text="Agregar Contacto",
            icon=ft.Icons.ADD,
            on_click=self._on_add_contact,
        )

        return ft.Column(
            controls=[
                *contact_rows,
                ft.Container(
                    content=add_button,
                    padding=ft.padding.only(top=LayoutConstants.PADDING_SM),
                ),
            ],
            spacing=0,
        )

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
        """Carga los datos de la empresa, direcciones y contactos desde la API."""
        logger.info(f"Loading company ID={self.company_id}")
        self._is_loading = True
        self._error_message = ""

        # Reconstruir contenido para mostrar loading
        self.content = self.build()
        if self.page:
            self.update()

        try:
            from src.frontend.services.api import CompanyAPI
            import httpx

            company_api = CompanyAPI()

            # Cargar empresa
            self._company = await company_api.get_by_id(self.company_id)
            logger.success(f"Company loaded: {self._company.get('name')}")

            # Cargar direcciones y contactos en paralelo usando httpx directamente
            async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                try:
                    # Cargar direcciones
                    addr_response = await client.get(f"/api/v1/addresses/company/{self.company_id}")
                    if addr_response.status_code == 200:
                        self._addresses = addr_response.json()
                        logger.success(f"Loaded {len(self._addresses)} addresses")
                    else:
                        logger.warning(f"Error loading addresses: {addr_response.status_code}")
                        self._addresses = []
                except Exception as e:
                    logger.warning(f"Error loading addresses: {e}")
                    self._addresses = []

                try:
                    # Cargar contactos
                    contact_response = await client.get(f"/api/v1/contacts/company/{self.company_id}")
                    if contact_response.status_code == 200:
                        self._contacts = contact_response.json()
                        logger.success(f"Loaded {len(self._contacts)} contacts")
                    else:
                        logger.warning(f"Error loading contacts: {contact_response.status_code}")
                        self._contacts = []
                except Exception as e:
                    logger.warning(f"Error loading contacts: {e}")
                    self._contacts = []

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
            self._confirm_dialog.show(self.page)

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

    # ========================================================================
    # MÉTODOS PARA ADDRESSES
    # ========================================================================

    def _on_add_address(self, e: ft.ControlEvent) -> None:
        """Abre el diálogo para agregar una nueva dirección."""
        logger.info(f"Add address clicked for company ID={self.company_id}")

        # Crear campos del formulario
        address_field = ft.TextField(
            label="Dirección *",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        city_field = ft.TextField(label="Ciudad")
        postal_code_field = ft.TextField(label="Código Postal", max_length=20)
        country_field = ft.TextField(label="País")
        type_dropdown = ft.Dropdown(
            label="Tipo de Dirección *",
            options=[
                ft.dropdown.Option("delivery", "Entrega"),
                ft.dropdown.Option("billing", "Facturación"),
                ft.dropdown.Option("headquarters", "Sede Principal"),
                ft.dropdown.Option("branch", "Sucursal"),
            ],
            value="delivery",
        )
        is_default_checkbox = ft.Checkbox(label="Dirección principal", value=False)

        def close_dialog():
            self.page.dialog.open = False
            self.page.update()

        async def save_address():
            # Validación simple
            if not address_field.value or not type_dropdown.value:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Por favor complete los campos obligatorios"),
                        bgcolor=ft.Colors.RED_400,
                    )
                )
                return

            try:
                import httpx
                data = {
                    "address": address_field.value,
                    "city": city_field.value or None,
                    "postal_code": postal_code_field.value or None,
                    "country": country_field.value or None,
                    "is_default": is_default_checkbox.value,
                    "address_type": type_dropdown.value,
                    "company_id": self.company_id,
                }

                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    response = await client.post("/api/v1/addresses", json=data)
                    if response.status_code == 201:
                        close_dialog()
                        await self._on_address_saved()
                    else:
                        error_detail = response.json().get("detail", "Error desconocido")
                        self.page.show_snack_bar(
                            ft.SnackBar(
                                content=ft.Text(f"Error: {error_detail}"),
                                bgcolor=ft.Colors.RED_400,
                            )
                        )
            except Exception as ex:
                logger.exception(f"Error saving address: {ex}")
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Error de conexión: {str(ex)}"),
                        bgcolor=ft.Colors.RED_400,
                    )
                )

        # Crear el dialog directamente (como en schedule_grid_view.py)
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Agregar Dirección", size=20),
            content=ft.Column(
                controls=[
                    address_field,
                    ft.Row(
                        controls=[
                            ft.Container(content=city_field, expand=2),
                            ft.Container(content=postal_code_field, expand=1),
                        ],
                        spacing=10,
                    ),
                    country_field,
                    type_dropdown,
                    is_default_checkbox,
                ],
                spacing=10,
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dialog()),
                ft.ElevatedButton(
                    "Guardar",
                    icon=ft.Icons.SAVE,
                    on_click=lambda _: self.page.run_task(save_address),
                ),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _on_edit_address(self, e: ft.ControlEvent, address: dict) -> None:
        """Abre el diálogo para editar una dirección."""
        logger.info(f"Edit address clicked: ID={address.get('id')}")

        address_id = address.get("id")

        # Crear campos del formulario con datos iniciales
        address_field = ft.TextField(
            label="Dirección *",
            value=address.get("address", ""),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        city_field = ft.TextField(label="Ciudad", value=address.get("city", ""))
        postal_code_field = ft.TextField(
            label="Código Postal",
            value=address.get("postal_code", ""),
            max_length=20,
        )
        country_field = ft.TextField(label="País", value=address.get("country", ""))
        type_dropdown = ft.Dropdown(
            label="Tipo de Dirección *",
            value=address.get("address_type", "delivery"),
            options=[
                ft.dropdown.Option("delivery", "Entrega"),
                ft.dropdown.Option("billing", "Facturación"),
                ft.dropdown.Option("headquarters", "Sede Principal"),
                ft.dropdown.Option("branch", "Sucursal"),
            ],
        )
        is_default_checkbox = ft.Checkbox(
            label="Dirección principal",
            value=address.get("is_default", False),
        )

        def close_dialog():
            self.page.dialog.open = False
            self.page.update()

        async def save_address():
            # Validación simple
            if not address_field.value or not type_dropdown.value:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Por favor complete los campos obligatorios"),
                        bgcolor=ft.Colors.RED_400,
                    )
                )
                return

            try:
                import httpx
                data = {
                    "address": address_field.value,
                    "city": city_field.value or None,
                    "postal_code": postal_code_field.value or None,
                    "country": country_field.value or None,
                    "is_default": is_default_checkbox.value,
                    "address_type": type_dropdown.value,
                }

                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    response = await client.put(
                        f"/api/v1/addresses/{address_id}", json=data
                    )
                    if response.status_code == 200:
                        close_dialog()
                        await self._on_address_saved()
                    else:
                        error_detail = response.json().get("detail", "Error desconocido")
                        self.page.show_snack_bar(
                            ft.SnackBar(
                                content=ft.Text(f"Error: {error_detail}"),
                                bgcolor=ft.Colors.RED_400,
                            )
                        )
            except Exception as ex:
                logger.exception(f"Error saving address: {ex}")
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Error de conexión: {str(ex)}"),
                        bgcolor=ft.Colors.RED_400,
                    )
                )

        # Crear el dialog directamente
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Dirección", size=20),
            content=ft.Column(
                controls=[
                    address_field,
                    ft.Row(
                        controls=[
                            ft.Container(content=city_field, expand=2),
                            ft.Container(content=postal_code_field, expand=1),
                        ],
                        spacing=10,
                    ),
                    country_field,
                    type_dropdown,
                    is_default_checkbox,
                ],
                spacing=10,
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dialog()),
                ft.ElevatedButton(
                    "Guardar",
                    icon=ft.Icons.SAVE,
                    on_click=lambda _: self.page.run_task(save_address),
                ),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _on_delete_address(self, e: ft.ControlEvent, address: dict) -> None:
        """Muestra confirmación para eliminar una dirección."""
        logger.info(f"Delete address clicked: ID={address.get('id')}")

        confirm_dialog = ConfirmDialog(
            title="Eliminar Dirección",
            message=f"¿Está seguro de que desea eliminar la dirección '{address.get('address')}'?",
            on_confirm=lambda: self.page.run_task(self._confirm_delete_address, address.get("id")),
        )

        if self.page:
            confirm_dialog.show(self.page)

    async def _confirm_delete_address(self, address_id: int) -> None:
        """Ejecuta la eliminación de una dirección."""
        logger.info(f"Confirming deletion of address ID={address_id}")

        try:
            import httpx

            async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                response = await client.delete(f"/api/v1/addresses/{address_id}")

                if response.status_code == 200:
                    logger.success(f"Address {address_id} deleted successfully")
                    await self._on_address_saved()
                    self._show_snackbar("Dirección eliminada exitosamente", ft.Colors.GREEN)
                else:
                    error_detail = response.json().get("detail", "Error desconocido")
                    logger.error(f"Error deleting address: {response.status_code} - {error_detail}")
                    self._show_snackbar(f"Error al eliminar: {error_detail}", ft.Colors.RED_400)

        except Exception as e:
            logger.exception(f"Error deleting address: {e}")
            self._show_snackbar(f"Error de conexión: {str(e)}", ft.Colors.RED_400)

    async def _on_address_saved(self) -> None:
        """Callback después de guardar/eliminar una dirección."""
        logger.info("Address saved, reloading addresses")
        await self._reload_addresses()
        self._show_snackbar("Cambios guardados exitosamente", ft.Colors.GREEN)

    async def _reload_addresses(self) -> None:
        """Recarga solo las direcciones desde la API."""
        try:
            import httpx

            async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                response = await client.get(f"/api/v1/addresses/company/{self.company_id}")
                if response.status_code == 200:
                    self._addresses = response.json()
                    logger.success(f"Reloaded {len(self._addresses)} addresses")
                else:
                    logger.warning(f"Error reloading addresses: {response.status_code}")
                    self._addresses = []

        except Exception as e:
            logger.exception(f"Error reloading addresses: {e}")
            self._addresses = []

        # Reconstruir solo el contenido
        self.content = self.build()
        if self.page:
            self.update()

    # ========================================================================
    # MÉTODOS PARA CONTACTS
    # ========================================================================

    def _on_add_contact(self, e: ft.ControlEvent) -> None:
        """Abre el diálogo para agregar un nuevo contacto."""
        logger.info(f"Add contact clicked for company ID={self.company_id}")

        # Crear campos del formulario
        first_name_field = ft.TextField(label="Nombre *")
        last_name_field = ft.TextField(label="Apellido *")
        email_field = ft.TextField(label="Email", keyboard_type=ft.KeyboardType.EMAIL)
        phone_field = ft.TextField(label="Teléfono", max_length=20)
        mobile_field = ft.TextField(label="Móvil", max_length=20)
        position_field = ft.TextField(label="Cargo")

        def close_dialog():
            self.page.dialog.open = False
            self.page.update()

        async def save_contact():
            # Validación simple
            if not first_name_field.value or not last_name_field.value:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Por favor complete los campos obligatorios"),
                        bgcolor=ft.Colors.RED_400,
                    )
                )
                return

            try:
                import httpx
                data = {
                    "first_name": first_name_field.value,
                    "last_name": last_name_field.value,
                    "email": email_field.value or None,
                    "phone": phone_field.value or None,
                    "mobile": mobile_field.value or None,
                    "position": position_field.value or None,
                    "company_id": self.company_id,
                }

                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    response = await client.post("/api/v1/contacts", json=data)
                    if response.status_code == 201:
                        close_dialog()
                        await self._on_contact_saved()
                    else:
                        error_detail = response.json().get("detail", "Error desconocido")
                        self.page.show_snack_bar(
                            ft.SnackBar(
                                content=ft.Text(f"Error: {error_detail}"),
                                bgcolor=ft.Colors.RED_400,
                            )
                        )
            except Exception as ex:
                logger.exception(f"Error saving contact: {ex}")
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Error de conexión: {str(ex)}"),
                        bgcolor=ft.Colors.RED_400,
                    )
                )

        # Crear el dialog directamente
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Agregar Contacto", size=20),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(content=first_name_field, expand=1),
                            ft.Container(content=last_name_field, expand=1),
                        ],
                        spacing=10,
                    ),
                    email_field,
                    ft.Row(
                        controls=[
                            ft.Container(content=phone_field, expand=1),
                            ft.Container(content=mobile_field, expand=1),
                        ],
                        spacing=10,
                    ),
                    position_field,
                ],
                spacing=10,
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dialog()),
                ft.ElevatedButton(
                    "Guardar",
                    icon=ft.Icons.SAVE,
                    on_click=lambda _: self.page.run_task(save_contact),
                ),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _on_edit_contact(self, e: ft.ControlEvent, contact: dict) -> None:
        """Abre el diálogo para editar un contacto."""
        logger.info(f"Edit contact clicked: ID={contact.get('id')}")

        contact_id = contact.get("id")

        # Crear campos del formulario con datos iniciales
        first_name_field = ft.TextField(
            label="Nombre *", value=contact.get("first_name", "")
        )
        last_name_field = ft.TextField(
            label="Apellido *", value=contact.get("last_name", "")
        )
        email_field = ft.TextField(
            label="Email",
            value=contact.get("email", ""),
            keyboard_type=ft.KeyboardType.EMAIL,
        )
        phone_field = ft.TextField(
            label="Teléfono", value=contact.get("phone", ""), max_length=20
        )
        mobile_field = ft.TextField(
            label="Móvil", value=contact.get("mobile", ""), max_length=20
        )
        position_field = ft.TextField(
            label="Cargo", value=contact.get("position", "")
        )

        def close_dialog():
            self.page.dialog.open = False
            self.page.update()

        async def save_contact():
            # Validación simple
            if not first_name_field.value or not last_name_field.value:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("Por favor complete los campos obligatorios"),
                        bgcolor=ft.Colors.RED_400,
                    )
                )
                return

            try:
                import httpx
                data = {
                    "first_name": first_name_field.value,
                    "last_name": last_name_field.value,
                    "email": email_field.value or None,
                    "phone": phone_field.value or None,
                    "mobile": mobile_field.value or None,
                    "position": position_field.value or None,
                }

                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    response = await client.put(
                        f"/api/v1/contacts/{contact_id}", json=data
                    )
                    if response.status_code == 200:
                        close_dialog()
                        await self._on_contact_saved()
                    else:
                        error_detail = response.json().get("detail", "Error desconocido")
                        self.page.show_snack_bar(
                            ft.SnackBar(
                                content=ft.Text(f"Error: {error_detail}"),
                                bgcolor=ft.Colors.RED_400,
                            )
                        )
            except Exception as ex:
                logger.exception(f"Error saving contact: {ex}")
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Error de conexión: {str(ex)}"),
                        bgcolor=ft.Colors.RED_400,
                    )
                )

        # Crear el dialog directamente
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Editar Contacto", size=20),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Container(content=first_name_field, expand=1),
                            ft.Container(content=last_name_field, expand=1),
                        ],
                        spacing=10,
                    ),
                    email_field,
                    ft.Row(
                        controls=[
                            ft.Container(content=phone_field, expand=1),
                            ft.Container(content=mobile_field, expand=1),
                        ],
                        spacing=10,
                    ),
                    position_field,
                ],
                spacing=10,
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: close_dialog()),
                ft.ElevatedButton(
                    "Guardar",
                    icon=ft.Icons.SAVE,
                    on_click=lambda _: self.page.run_task(save_contact),
                ),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def _on_delete_contact(self, e: ft.ControlEvent, contact: dict) -> None:
        """Muestra confirmación para eliminar un contacto."""
        logger.info(f"Delete contact clicked: ID={contact.get('id')}")

        full_name = f"{contact.get('first_name')} {contact.get('last_name')}"
        confirm_dialog = ConfirmDialog(
            title="Eliminar Contacto",
            message=f"¿Está seguro de que desea eliminar el contacto '{full_name}'?",
            on_confirm=lambda: self.page.run_task(self._confirm_delete_contact, contact.get("id")),
        )

        if self.page:
            confirm_dialog.show(self.page)

    async def _confirm_delete_contact(self, contact_id: int) -> None:
        """Ejecuta la eliminación de un contacto."""
        logger.info(f"Confirming deletion of contact ID={contact_id}")

        try:
            import httpx

            async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                response = await client.delete(f"/api/v1/contacts/{contact_id}")

                if response.status_code == 200:
                    logger.success(f"Contact {contact_id} deleted successfully")
                    await self._on_contact_saved()
                    self._show_snackbar("Contacto eliminado exitosamente", ft.Colors.GREEN)
                else:
                    error_detail = response.json().get("detail", "Error desconocido")
                    logger.error(f"Error deleting contact: {response.status_code} - {error_detail}")
                    self._show_snackbar(f"Error al eliminar: {error_detail}", ft.Colors.RED_400)

        except Exception as e:
            logger.exception(f"Error deleting contact: {e}")
            self._show_snackbar(f"Error de conexión: {str(e)}", ft.Colors.RED_400)

    async def _on_contact_saved(self) -> None:
        """Callback después de guardar/eliminar un contacto."""
        logger.info("Contact saved, reloading contacts")
        await self._reload_contacts()
        self._show_snackbar("Cambios guardados exitosamente", ft.Colors.GREEN)

    async def _reload_contacts(self) -> None:
        """Recarga solo los contactos desde la API."""
        try:
            import httpx

            async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                response = await client.get(f"/api/v1/contacts/company/{self.company_id}")
                if response.status_code == 200:
                    self._contacts = response.json()
                    logger.success(f"Reloaded {len(self._contacts)} contacts")
                else:
                    logger.warning(f"Error reloading contacts: {response.status_code}")
                    self._contacts = []

        except Exception as e:
            logger.exception(f"Error reloading contacts: {e}")
            self._contacts = []

        # Reconstruir solo el contenido
        self.content = self.build()
        if self.page:
            self.update()

    # ========================================================================
    # SNACKBAR
    # ========================================================================

    def _show_snackbar(self, message: str, bgcolor: str = ft.Colors.GREEN) -> None:
        """Muestra un snackbar con un mensaje."""
        if not self.page:
            return

        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=bgcolor,
            duration=3000,
        )

        self.page.snack_bar = snackbar
        snackbar.open = True
        self.page.update()

        logger.debug(f"Snackbar shown: {message}")

    def _on_state_changed(self) -> None:
        """Observer: Se ejecuta cuando cambia el estado."""
        if self.page:
            self.update()
