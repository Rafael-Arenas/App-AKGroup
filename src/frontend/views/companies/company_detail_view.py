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
from src.frontend.i18n.translation_manager import t
from src.frontend.utils.rut_utils import validate_rut, format_rut

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
        self._plants: list[dict] = []
        self._ruts: list[dict] = []
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
                content=LoadingSpinner(message=t("companies.messages.loading")),
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
                t("companies.status.active") if self._company.get("is_active") else t("companies.status.inactive"),
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
                                tooltip=t("companies.actions.edit_company"),
                                on_click=self._on_edit_click,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip=t("companies.actions.delete_company"),
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
                self._create_info_row(t("companies.detail.legal_name"), self._company.get("name", "-")),
                self._create_info_row(t("companies.detail.trigram"), self._company.get("trigram", "-")),
                self._create_info_row(t("companies.columns.type"), self._format_company_type(
                    self._company.get("company_type", "")
                )),
                self._create_info_row(t("companies.detail.status"), t("companies.status.active") if self._company.get("is_active") else t("companies.status.inactive")),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        general_card = BaseCard(
            title=t("companies.sections.general_info"),
            icon=ft.Icons.BUSINESS,
            content=general_info,
        )

        # Tarjeta de Información de Contacto
        contact_info = ft.Column(
            controls=[
                self._create_info_row(t("companies.detail.phone"), self._company.get("phone", "-")),
                self._create_info_row(t("companies.detail.website"), self._company.get("website", "-")),
                self._create_info_row(t("companies.detail.intracommunity_number"), self._company.get("intracommunity_number", "-")),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        contact_card = BaseCard(
            title=t("companies.sections.contact_info"),
            icon=ft.Icons.CONTACT_PHONE,
            content=contact_info,
        )

        # Tarjeta de Ubicación
        location_info = ft.Column(
            controls=[
                self._create_info_row(t("companies.detail.country"), self._company.get("country_name", "-")),
                self._create_info_row(t("companies.detail.city"), self._company.get("city_name", "-")),
                self._create_info_row(t("companies.detail.main_address"), self._company.get("main_address", "-")),
            ],
            spacing=LayoutConstants.SPACING_SM,
        )

        location_card = BaseCard(
            title=t("companies.sections.location"),
            icon=ft.Icons.LOCATION_ON,
            content=location_info,
        )

        # Tarjeta de Información Fiscal (si existe)
        fiscal_controls = []
        if self._company.get("intracommunity_number"):
            fiscal_controls.append(
                self._create_info_row(t("companies.detail.intracommunity_number"), self._company.get("intracommunity_number"))
            )

        fiscal_card = None
        if fiscal_controls:
            fiscal_info = ft.Column(
                controls=fiscal_controls,
                spacing=LayoutConstants.SPACING_SM,
            )
            fiscal_card = BaseCard(
                title=t("companies.sections.fiscal_info"),
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

        # Tarjetas de RUTs, Contactos, Plantas y Direcciones
        ruts_card = BaseCard(
            title="RUTs",
            icon=ft.Icons.ASSIGNMENT_IND,
            content=self._create_ruts_section(),
            collapsible=True,
            initially_collapsed=False,
        )
        cards.append(ruts_card)

        plants_card = BaseCard(
            title="Plantas",
            icon=ft.Icons.FACTORY,
            content=self._create_plants_section(),
            collapsible=True,
            initially_collapsed=False,
        )
        cards.append(plants_card)

        contacts_card = BaseCard(
            title=t("companies.sections.contacts"),
            icon=ft.Icons.CONTACTS,
            content=self._create_contacts_section(),
            collapsible=True,
            initially_collapsed=False,
        )
        cards.append(contacts_card)

        addresses_card = BaseCard(
            title=t("companies.sections.addresses"),
            icon=ft.Icons.LOCATION_ON,
            content=self._create_addresses_section(),
            collapsible=True,
            initially_collapsed=False,
        )
        cards.append(addresses_card)

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
                            t("companies.empty_states.no_addresses"),
                            size=LayoutConstants.FONT_SIZE_MD,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.ElevatedButton(
                            text=t("companies.actions.add_first_address"),
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
                "delivery": t("companies.address_types.delivery"),
                "billing": t("companies.address_types.billing"),
                "headquarters": t("companies.address_types.headquarters"),
                "plant": t("companies.address_types.plant"),
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
                            t("companies.labels.primary"),
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
                                            tooltip=t("companies.actions.edit_address"),
                                            on_click=lambda e, a=addr: self._on_edit_address(e, a),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            icon_size=LayoutConstants.ICON_SIZE_SM,
                                            tooltip=t("companies.actions.delete_address"),
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
            text=t("companies.address.add"),
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
                            t("companies.empty_states.no_contacts"),
                            size=LayoutConstants.FONT_SIZE_MD,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.ElevatedButton(
                            text=t("companies.actions.add_first_contact"),
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
                    t("companies.status.active") if contact.get("is_active") else t("companies.status.inactive"),
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
                                    tooltip=t("companies.actions.edit_contact"),
                                    on_click=lambda e, c=contact: self._on_edit_contact(e, c),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=LayoutConstants.ICON_SIZE_SM,
                                    tooltip=t("companies.actions.delete_contact"),
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
            text=t("companies.contact.add"),
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

    def _create_ruts_section(self) -> ft.Control:
        """
        Crea la sección de RUTs con lista de cards.

        Returns:
            Control con la lista de RUTs
        """
        if not self._ruts:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            name=ft.Icons.ASSIGNMENT_IND_OUTLINED,
                            size=LayoutConstants.ICON_SIZE_LG,
                            color=ft.Colors.GREY_400,
                        ),
                        ft.Text(
                            "No hay RUTs registrados",
                            size=LayoutConstants.FONT_SIZE_MD,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.ElevatedButton(
                            text="Agregar primer RUT",
                            icon=ft.Icons.ADD,
                            on_click=self._on_add_rut,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=LayoutConstants.SPACING_SM,
                ),
                padding=LayoutConstants.PADDING_MD,
                alignment=ft.alignment.center,
            )

        # Lista de RUTs
        rut_cards = []
        for rut in self._ruts:
            # Badge de principal
            badges = []
            if rut.get("is_main"):
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

            rut_card = ft.Container(
                content=ft.Row(
                    controls=[
                        # RUT
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=badges,
                                        spacing=LayoutConstants.SPACING_XS,
                                    ),
                                    ft.Text(
                                        rut.get("rut", "-"),
                                        size=LayoutConstants.FONT_SIZE_MD,
                                        weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                                    ),
                                ],
                                spacing=LayoutConstants.SPACING_XS,
                            ),
                            width=200,
                        ),
                        # Estado y acciones
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.EDIT_OUTLINED,
                                    icon_size=LayoutConstants.ICON_SIZE_SM,
                                    tooltip="Editar RUT",
                                    on_click=lambda e, r=rut: self._on_edit_rut(e, r),
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE,
                                    icon_size=LayoutConstants.ICON_SIZE_SM,
                                    tooltip="Eliminar RUT",
                                    on_click=lambda e, r=rut: self._on_delete_rut(e, r),
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
            rut_cards.append(rut_card)

        # Botón para agregar nuevo RUT
        add_button = ft.ElevatedButton(
            text="Agregar RUT",
            icon=ft.Icons.ADD,
            on_click=self._on_add_rut,
        )

        return ft.Column(
            controls=[
                *rut_cards,
                ft.Container(
                    content=add_button,
                    padding=ft.padding.only(top=LayoutConstants.PADDING_SM),
                ),
            ],
            spacing=0,
        )

    def _create_plants_section(self) -> ft.Control:
        """
        Crea la sección de plantas con lista de cards.

        Returns:
            Control con la lista de plantas
        """
        if not self._plants:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            name=ft.Icons.FACTORY_OUTLINED,
                            size=LayoutConstants.ICON_SIZE_LG,
                            color=ft.Colors.GREY_400,
                        ),
                        ft.Text(
                            "No hay plantas registradas",
                            size=LayoutConstants.FONT_SIZE_MD,
                            color=ft.Colors.GREY_600,
                        ),
                        ft.ElevatedButton(
                            text="Agregar primera planta",
                            icon=ft.Icons.ADD,
                            on_click=self._on_add_plant,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=LayoutConstants.SPACING_SM,
                ),
                padding=LayoutConstants.PADDING_MD,
                alignment=ft.alignment.center,
            )

        # Lista de plantas
        plant_cards = []
        for plant in self._plants:
            # Badge de activo/inactivo (si aplica, el modelo tiene ActiveMixin)
            status_badge = ft.Container(
                content=ft.Text(
                    t("companies.status.active") if plant.get("is_active", True) else t("companies.status.inactive"),
                    size=LayoutConstants.FONT_SIZE_XS,
                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                    color=ft.Colors.WHITE,
                ),
                padding=ft.padding.symmetric(
                    horizontal=LayoutConstants.PADDING_SM,
                    vertical=2,
                ),
                border_radius=LayoutConstants.RADIUS_FULL,
                bgcolor=ft.Colors.GREEN if plant.get("is_active", True) else ft.Colors.RED_400,
            )

            plant_card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Icon(
                                    name=ft.Icons.FACTORY,
                                    size=LayoutConstants.ICON_SIZE_MD,
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text(
                                                    plant.get("name", "-"),
                                                    size=LayoutConstants.FONT_SIZE_MD,
                                                    weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD,
                                                ),
                                                status_badge,
                                            ],
                                            spacing=LayoutConstants.SPACING_SM,
                                        ),
                                        ft.Text(
                                            plant.get("address", "-"),
                                            size=LayoutConstants.FONT_SIZE_SM,
                                            color=ft.Colors.GREY_700,
                                        ),
                                        ft.Text(
                                            f"{plant.get('city', {}).get('name', '') if isinstance(plant.get('city'), dict) else plant.get('city_name', '')}".strip() or "-",
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
                                            tooltip="Editar planta",
                                            on_click=lambda e, p=plant: self._on_edit_plant(e, p),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE_OUTLINE,
                                            icon_size=LayoutConstants.ICON_SIZE_SM,
                                            tooltip="Eliminar planta",
                                            on_click=lambda e, p=plant: self._on_delete_plant(e, p),
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
            plant_cards.append(plant_card)

        # Botón para agregar nueva planta
        add_button = ft.ElevatedButton(
            text="Agregar Planta",
            icon=ft.Icons.ADD,
            on_click=self._on_add_plant,
        )

        return ft.Column(
            controls=[
                *plant_cards,
                ft.Container(
                    content=add_button,
                    padding=ft.padding.only(top=LayoutConstants.PADDING_SM),
                ),
            ],
            spacing=LayoutConstants.SPACING_SM,
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
            "CLIENT": t("clients.title"),
            "SUPPLIER": t("suppliers.title"),
            "BOTH": t("companies.title"),
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

                try:
                    # Cargar RUTs
                    rut_response = await client.get(f"/api/v1/company-ruts/company/{self.company_id}")
                    if rut_response.status_code == 200:
                        self._ruts = rut_response.json()
                        logger.success(f"Loaded {len(self._ruts)} RUTs")
                    else:
                        logger.warning(f"Error loading RUTs: {rut_response.status_code}")
                        self._ruts = []
                except Exception as e:
                    logger.warning(f"Error loading RUTs: {e}")
                    self._ruts = []

                try:
                    # Cargar Plantas
                    plant_response = await client.get(f"/api/v1/plants/company/{self.company_id}")
                    if plant_response.status_code == 200:
                        self._plants = plant_response.json()
                        logger.success(f"Loaded {len(self._plants)} plants")
                    else:
                        logger.warning(f"Error loading plants: {plant_response.status_code}")
                        self._plants = []
                except Exception as e:
                    logger.warning(f"Error loading plants: {e}")
                    self._plants = []

            self._is_loading = False

        except Exception as e:
            logger.exception(f"Error loading company: {e}")
            self._error_message = t("companies.messages.error_loading").format(error=str(e))
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
            title=t("companies.messages.delete_title"),
            message=t("companies.messages.delete_confirm").format(name=self._company.get('name')),
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
        """Abre el bottom sheet para agregar una nueva dirección."""
        logger.info(f"Add address clicked for company ID={self.company_id}")

        # Diccionario para almacenar países y sus ciudades  (se carga dinámicamente)
        countries_data = {}  # {country_id: country_name}
        cities_by_country = {}  # {country_id: [city_objects]}

        # Crear campos del formulario
        address_field = ft.TextField(
            label=t("companies.labels.address") + " *",
            multiline=True,
            min_lines=2,
            max_lines=4,
        )

        postal_code_field = ft.TextField(label=t("companies.labels.postal_code"), max_length=20)

        # Dropdown de ciudades (inicialmente vacío)
        city_dropdown = ft.Dropdown(
            label=t("companies.columns.city"),
            options=[],
            disabled=True,
        )

        # Dropdown de países (se cargará con datos de la API)
        country_dropdown = ft.Dropdown(
            label=t("companies.form.country") + " *",
            options=[],
            disabled=True,
        )

        async def load_countries():
            """Carga los países desde la API."""
            try:
                import httpx
                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    response = await client.get("/api/v1/lookups/countries/")
                    if response.status_code == 200:
                        countries = response.json()
                        for country in countries:
                            countries_data[country["id"]] = country["name"]

                        # Actualizar dropdown de países
                        country_dropdown.options = [
                            ft.dropdown.Option(str(cid), cname)
                            for cid, cname in sorted(countries_data.items(), key=lambda x: x[1])
                        ]
                        country_dropdown.disabled = False
                        country_dropdown.update()
                        logger.success(f"Loaded {len(countries_data)} countries from API")
                    else:
                        logger.error(f"Error loading countries: {response.status_code}")
            except Exception as ex:
                logger.exception(f"Error loading countries: {ex}")

        async def load_cities(country_id: int):
            """Carga las ciudades de un país desde la API."""
            try:
                import httpx
                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    response = await client.get(f"/api/v1/lookups/cities/?country_id={country_id}")
                    if response.status_code == 200:
                        cities = response.json()
                        cities_by_country[country_id] = cities

                        # Actualizar dropdown de ciudades
                        city_dropdown.options = [
                            ft.dropdown.Option(city["name"], city["name"])
                            for city in sorted(cities, key=lambda x: x["name"])
                        ]
                        city_dropdown.disabled = False
                        city_dropdown.value = None
                        city_dropdown.update()
                        logger.success(f"Loaded {len(cities)} cities for country {country_id}")
                    else:
                        logger.error(f"Error loading cities: {response.status_code}")
            except Exception as ex:
                logger.exception(f"Error loading cities: {ex}")

        def on_country_change(e):
            """Maneja el cambio de país."""
            selected_country_id = e.control.value
            if selected_country_id:
                # Cargar ciudades del país seleccionado
                self.page.run_task(load_cities, int(selected_country_id))
            else:
                city_dropdown.options = []
                city_dropdown.disabled = True
                city_dropdown.value = None
                city_dropdown.update()

        country_dropdown.on_change = on_country_change

        # Cargar países al abrir el bottom sheet
        self.page.run_task(load_countries)

        type_dropdown = ft.Dropdown(
            label=t("companies.columns.type") + " *",
            options=[
                ft.dropdown.Option("delivery", t("companies.address_types.delivery")),
                ft.dropdown.Option("billing", t("companies.address_types.billing")),
                ft.dropdown.Option("headquarters", t("companies.address_types.headquarters")),
                ft.dropdown.Option("plant", t("companies.address_types.plant")),
            ],
            value="delivery",
        )
        is_default_checkbox = ft.Checkbox(label=t("companies.labels.main_address"), value=False)

        def close_bottom_sheet():
            self.page.close(bottom_sheet)

        async def save_address():
            # Validación simple
            if not address_field.value or not type_dropdown.value or not country_dropdown.value:
                snack = ft.SnackBar(
                    content=ft.Text(t("companies.address.required_fields")),
                    bgcolor=ft.Colors.RED_400,
                )
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()
                return

            try:
                import httpx
                # Obtener el nombre del país seleccionado
                country_id = int(country_dropdown.value)
                country_name = countries_data.get(country_id, "")

                data = {
                    "address": address_field.value,
                    "city": city_dropdown.value or None,
                    "postal_code": postal_code_field.value or None,
                    "country": country_name,
                    "is_default": is_default_checkbox.value,
                    "address_type": type_dropdown.value,
                    "company_id": self.company_id,
                }

                async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                    response = await client.post("/api/v1/addresses/", json=data)
                    if response.status_code == 201:
                        close_bottom_sheet()
                        await self._on_address_saved()
                    else:
                        try:
                            error_detail = response.json().get("detail", t("companies.messages.unknown_error"))
                        except Exception:
                            error_detail = f"Error {response.status_code}"

                        snack = ft.SnackBar(
                            content=ft.Text(f"Error: {error_detail}"),
                            bgcolor=ft.Colors.RED_400,
                        )
                        self.page.snack_bar = snack
                        snack.open = True
                        self.page.update()
            except Exception as ex:
                logger.exception(f"Error saving address: {ex}")
                snack = ft.SnackBar(
                    content=ft.Text(f"Error de conexión: {str(ex)}"),
                    bgcolor=ft.Colors.RED_400,
                )
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()

        # Crear BottomSheet en lugar de AlertDialog
        bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(t("companies.address.add"), size=20, weight=ft.FontWeight.BOLD),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    on_click=lambda _: close_bottom_sheet(),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Divider(),
                        address_field,
                        country_dropdown,
                        ft.Row(
                            controls=[
                                ft.Container(content=city_dropdown, expand=2),
                                ft.Container(content=postal_code_field, expand=1),
                            ],
                            spacing=10,
                        ),
                        type_dropdown,
                        is_default_checkbox,
                        ft.Row(
                            controls=[
                                ft.TextButton("Cancelar", on_click=lambda _: close_bottom_sheet()),
                                ft.ElevatedButton(
                                    "Guardar",
                                    icon=ft.Icons.SAVE,
                                    on_click=lambda _: self.page.run_task(save_address),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
            ),
        )

        self.page.open(bottom_sheet)
        logger.info("BottomSheet opened for adding address")

    def _on_edit_address(self, e: ft.ControlEvent, address: dict) -> None:
        """Abre el bottom sheet para editar una dirección."""
        logger.info(f"Edit address clicked: ID={address.get('id')}")

        address_id = address.get("id")

        # Diccionario para almacenar países y sus ciudades (se carga dinámicamente)
        countries_data = {}  # {country_id: country_name}
        cities_by_country = {}  # {country_id: [city_objects]}

        # Crear campos del formulario con datos iniciales
        address_field = ft.TextField(
            label="Dirección *",
            value=address.get("address", ""),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )

        postal_code_field = ft.TextField(
            label="Código Postal",
            value=address.get("postal_code", ""),
            max_length=20,
        )

        # Obtener país y ciudad actuales
        current_country_name = address.get("country", "")
        current_city_name = address.get("city", "")

        # Dropdown de ciudades (se cargará después de cargar el país)
        city_dropdown = ft.Dropdown(
            label="Ciudad",
            options=[],
            disabled=True,
        )

        # Dropdown de países (se cargará con datos de la API)
        country_dropdown = ft.Dropdown(
            label="País *",
            options=[],
            disabled=True,
        )

        async def load_countries():
            """Carga los países desde la API."""
            try:
                import httpx
                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    response = await client.get("/api/v1/lookups/countries/")
                    if response.status_code == 200:
                        countries = response.json()
                        current_country_id = None

                        for country in countries:
                            countries_data[country["id"]] = country["name"]
                            # Encontrar el ID del país actual
                            if country["name"] == current_country_name:
                                current_country_id = country["id"]

                        # Actualizar dropdown de países
                        country_dropdown.options = [
                            ft.dropdown.Option(str(cid), cname)
                            for cid, cname in sorted(countries_data.items(), key=lambda x: x[1])
                        ]
                        country_dropdown.disabled = False

                        # Establecer el país actual si existe
                        if current_country_id:
                            country_dropdown.value = str(current_country_id)
                            # Cargar ciudades del país actual
                            await load_cities(current_country_id, set_current=True)

                        country_dropdown.update()
                        logger.success(f"Loaded {len(countries_data)} countries from API")
                    else:
                        logger.error(f"Error loading countries: {response.status_code}")
            except Exception as ex:
                logger.exception(f"Error loading countries: {ex}")

        async def load_cities(country_id: int, set_current: bool = False):
            """Carga las ciudades de un país desde la API."""
            try:
                import httpx
                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    response = await client.get(f"/api/v1/lookups/cities/?country_id={country_id}")
                    if response.status_code == 200:
                        cities = response.json()
                        cities_by_country[country_id] = cities

                        # Actualizar dropdown de ciudades
                        city_dropdown.options = [
                            ft.dropdown.Option(city["name"], city["name"])
                            for city in sorted(cities, key=lambda x: x["name"])
                        ]
                        city_dropdown.disabled = False

                        # Si estamos cargando inicialmente, establecer la ciudad actual
                        if set_current and current_city_name:
                            city_names = [c["name"] for c in cities]
                            if current_city_name in city_names:
                                city_dropdown.value = current_city_name
                        else:
                            city_dropdown.value = None

                        city_dropdown.update()
                        logger.success(f"Loaded {len(cities)} cities for country {country_id}")
                    else:
                        logger.error(f"Error loading cities: {response.status_code}")
            except Exception as ex:
                logger.exception(f"Error loading cities: {ex}")

        def on_country_change(e):
            """Maneja el cambio de país."""
            selected_country_id = e.control.value
            if selected_country_id:
                # Cargar ciudades del país seleccionado
                self.page.run_task(load_cities, int(selected_country_id), False)
            else:
                city_dropdown.options = []
                city_dropdown.disabled = True
                city_dropdown.value = None
                city_dropdown.update()

        country_dropdown.on_change = on_country_change

        # Cargar países al abrir el bottom sheet
        self.page.run_task(load_countries)

        type_dropdown = ft.Dropdown(
            label="Tipo de Dirección *",
            value=address.get("address_type", "delivery"),
            options=[
                ft.dropdown.Option("delivery", "Entrega"),
                ft.dropdown.Option("billing", "Facturación"),
                ft.dropdown.Option("headquarters", "Sede Principal"),
                ft.dropdown.Option("plant", "Planta"),
            ],
        )
        is_default_checkbox = ft.Checkbox(
            label="Dirección principal",
            value=address.get("is_default", False),
        )

        def close_bottom_sheet():
            self.page.close(bottom_sheet)

        async def save_address():
            # Validación simple
            if not address_field.value or not type_dropdown.value or not country_dropdown.value:
                snack = ft.SnackBar(
                    content=ft.Text(t("companies.address.required_fields")),
                    bgcolor=ft.Colors.RED_400,
                )
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()
                return

            try:
                import httpx
                # Obtener el nombre del país seleccionado
                country_id = int(country_dropdown.value)
                country_name = countries_data.get(country_id, "")

                data = {
                    "address": address_field.value,
                    "city": city_dropdown.value or None,
                    "postal_code": postal_code_field.value or None,
                    "country": country_name,
                    "is_default": is_default_checkbox.value,
                    "address_type": type_dropdown.value,
                }

                async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                    response = await client.put(
                        f"/api/v1/addresses/{address_id}/", json=data
                    )
                    if response.status_code == 200:
                        close_bottom_sheet()
                        await self._on_address_saved()
                    else:
                        try:
                            error_detail = response.json().get("detail", t("companies.messages.unknown_error"))
                        except Exception:
                            error_detail = f"Error {response.status_code}"

                        snack = ft.SnackBar(
                            content=ft.Text(f"Error: {error_detail}"),
                            bgcolor=ft.Colors.RED_400,
                        )
                        self.page.snack_bar = snack
                        snack.open = True
                        self.page.update()
            except Exception as ex:
                logger.exception(f"Error saving address: {ex}")
                snack = ft.SnackBar(
                    content=ft.Text(f"Error de conexión: {str(ex)}"),
                    bgcolor=ft.Colors.RED_400,
                )
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()

        # Crear BottomSheet
        bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("Editar Dirección", size=20, weight=ft.FontWeight.BOLD),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    on_click=lambda _: close_bottom_sheet(),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Divider(),
                        address_field,
                        country_dropdown,
                        ft.Row(
                            controls=[
                                ft.Container(content=city_dropdown, expand=2),
                                ft.Container(content=postal_code_field, expand=1),
                            ],
                            spacing=10,
                        ),
                        type_dropdown,
                        is_default_checkbox,
                        ft.Row(
                            controls=[
                                ft.TextButton("Cancelar", on_click=lambda _: close_bottom_sheet()),
                                ft.ElevatedButton(
                                    "Guardar",
                                    icon=ft.Icons.SAVE,
                                    on_click=lambda _: self.page.run_task(save_address),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
            ),
        )

        self.page.open(bottom_sheet)
        logger.info("BottomSheet opened for editing address")

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

            async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                response = await client.delete(f"/api/v1/addresses/{address_id}/")

                if response.status_code == 200:
                    logger.success(f"Address {address_id} deleted successfully")
                    await self._on_address_saved()
                    self._show_snackbar(t("companies.messages.address_deleted"), ft.Colors.GREEN)
                else:
                    try:
                        error_detail = response.json().get("detail", t("companies.messages.unknown_error"))
                    except Exception:
                        error_detail = f"Error {response.status_code}"
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

            async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                response = await client.get(f"/api/v1/addresses/company/{self.company_id}/")
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
        """Abre el bottom sheet para agregar un nuevo contacto."""
        logger.info(f"Add contact clicked for company ID={self.company_id}")

        # Crear campos del formulario
        first_name_field = ft.TextField(label="Nombre *")
        last_name_field = ft.TextField(label="Apellido *")
        email_field = ft.TextField(label="Email", keyboard_type=ft.KeyboardType.EMAIL)
        phone_field = ft.TextField(label="Teléfono", max_length=20)
        mobile_field = ft.TextField(label="Móvil", max_length=20)
        position_field = ft.TextField(label="Cargo")

        def close_bottom_sheet():
            self.page.close(bottom_sheet)

        async def save_contact():
            # Validación simple
            if not first_name_field.value or not last_name_field.value:
                snack = ft.SnackBar(
                    content=ft.Text(t("companies.address.required_fields")),
                    bgcolor=ft.Colors.RED_400,
                )
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()
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

                async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                    response = await client.post("/api/v1/contacts", json=data)
                    if response.status_code == 201:
                        close_bottom_sheet()
                        await self._on_contact_saved()
                    else:
                        try:
                            error_detail = response.json().get("detail", t("companies.messages.unknown_error"))
                        except Exception:
                            error_detail = f"Error {response.status_code}"

                        snack = ft.SnackBar(
                            content=ft.Text(f"Error: {error_detail}"),
                            bgcolor=ft.Colors.RED_400,
                        )
                        self.page.snack_bar = snack
                        snack.open = True
                        self.page.update()
            except Exception as ex:
                logger.exception(f"Error saving contact: {ex}")
                snack = ft.SnackBar(
                    content=ft.Text(f"Error de conexión: {str(ex)}"),
                    bgcolor=ft.Colors.RED_400,
                )
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()

        # Crear BottomSheet
        bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("Agregar Contacto", size=20, weight=ft.FontWeight.BOLD),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    on_click=lambda _: close_bottom_sheet(),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Divider(),
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
                        ft.Row(
                            controls=[
                                ft.TextButton("Cancelar", on_click=lambda _: close_bottom_sheet()),
                                ft.ElevatedButton(
                                    "Guardar",
                                    icon=ft.Icons.SAVE,
                                    on_click=lambda _: self.page.run_task(save_contact),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
            ),
        )

        self.page.open(bottom_sheet)
        logger.info("BottomSheet opened for adding contact")

    def _on_edit_contact(self, e: ft.ControlEvent, contact: dict) -> None:
        """Abre el bottom sheet para editar un contacto."""
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

        def close_bottom_sheet():
            self.page.close(bottom_sheet)

        async def save_contact():
            # Validación simple
            if not first_name_field.value or not last_name_field.value:
                snack = ft.SnackBar(
                    content=ft.Text(t("companies.address.required_fields")),
                    bgcolor=ft.Colors.RED_400,
                )
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()
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

                async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                    response = await client.put(
                        f"/api/v1/contacts/{contact_id}", json=data
                    )
                    if response.status_code == 200:
                        close_bottom_sheet()
                        await self._on_contact_saved()
                    else:
                        try:
                            error_detail = response.json().get("detail", t("companies.messages.unknown_error"))
                        except Exception:
                            error_detail = f"Error {response.status_code}"

                        snack = ft.SnackBar(
                            content=ft.Text(f"Error: {error_detail}"),
                            bgcolor=ft.Colors.RED_400,
                        )
                        self.page.snack_bar = snack
                        snack.open = True
                        self.page.update()
            except Exception as ex:
                logger.exception(f"Error saving contact: {ex}")
                snack = ft.SnackBar(
                    content=ft.Text(f"Error de conexión: {str(ex)}"),
                    bgcolor=ft.Colors.RED_400,
                )
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()

        # Crear BottomSheet
        bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("Editar Contacto", size=20, weight=ft.FontWeight.BOLD),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    on_click=lambda _: close_bottom_sheet(),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Divider(),
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
                        ft.Row(
                            controls=[
                                ft.TextButton("Cancelar", on_click=lambda _: close_bottom_sheet()),
                                ft.ElevatedButton(
                                    "Guardar",
                                    icon=ft.Icons.SAVE,
                                    on_click=lambda _: self.page.run_task(save_contact),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
            ),
        )

        self.page.open(bottom_sheet)
        logger.info("BottomSheet opened for editing contact")

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

            async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                response = await client.delete(f"/api/v1/contacts/{contact_id}")

                if response.status_code == 200:
                    logger.success(f"Contact {contact_id} deleted successfully")
                    await self._on_contact_saved()
                    self._show_snackbar(t("companies.messages.contact_deleted"), ft.Colors.GREEN)
                else:
                    try:
                        error_detail = response.json().get("detail", t("companies.messages.unknown_error"))
                    except Exception:
                        error_detail = f"Error {response.status_code}"
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

            async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
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
    # MÉTODOS PARA PLANTS
    # ========================================================================

    def _on_add_plant(self, e: ft.ControlEvent) -> None:
        """Abre el bottom sheet para agregar una nueva planta."""
        logger.info(f"Add plant clicked for company ID={self.company_id}")

        # Diccionario para almacenar países y sus ciudades (se carga dinámicamente)
        countries_data = {}  # {country_id: country_name}
        cities_by_country = {}  # {country_id: [city_objects]}

        # Crear campos del formulario
        name_field = ft.TextField(label="Nombre de la planta *")
        address_field = ft.TextField(
            label="Dirección",
            multiline=True,
            min_lines=2,
            max_lines=3,
        )
        phone_field = ft.TextField(label="Teléfono", max_length=20)
        email_field = ft.TextField(label="Email", keyboard_type=ft.KeyboardType.EMAIL)

        # Dropdown de ciudades (inicialmente vacío)
        city_dropdown = ft.Dropdown(
            label="Ciudad",
            options=[],
            disabled=True,
        )

        # Dropdown de países (para filtrar ciudades)
        country_dropdown = ft.Dropdown(
            label="País (para filtrar ciudades)",
            options=[],
            disabled=True,
        )

        async def load_countries():
            """Carga los países desde la API."""
            try:
                import httpx
                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    response = await client.get("/api/v1/lookups/countries/")
                    if response.status_code == 200:
                        countries = response.json()
                        for country in countries:
                            countries_data[country["id"]] = country["name"]

                        # Actualizar dropdown de países
                        country_dropdown.options = [
                            ft.dropdown.Option(str(cid), cname)
                            for cid, cname in sorted(countries_data.items(), key=lambda x: x[1])
                        ]
                        country_dropdown.disabled = False
                        country_dropdown.update()
                    else:
                        logger.error(f"Error loading countries: {response.status_code}")
            except Exception as ex:
                logger.exception(f"Error loading countries: {ex}")

        async def load_cities(country_id: int):
            """Carga las ciudades de un país desde la API."""
            try:
                import httpx
                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    response = await client.get(f"/api/v1/lookups/cities/?country_id={country_id}")
                    if response.status_code == 200:
                        cities = response.json()
                        cities_by_country[country_id] = cities

                        # Actualizar dropdown de ciudades
                        city_dropdown.options = [
                            ft.dropdown.Option(str(city["id"]), city["name"]) # Value es el ID
                            for city in sorted(cities, key=lambda x: x["name"])
                        ]
                        city_dropdown.disabled = False
                        city_dropdown.value = None
                        city_dropdown.update()
                    else:
                        logger.error(f"Error loading cities: {response.status_code}")
            except Exception as ex:
                logger.exception(f"Error loading cities: {ex}")

        def on_country_change(e):
            """Maneja el cambio de país."""
            selected_country_id = e.control.value
            if selected_country_id:
                # Cargar ciudades del país seleccionado
                self.page.run_task(load_cities, int(selected_country_id))
            else:
                city_dropdown.options = []
                city_dropdown.disabled = True
                city_dropdown.value = None
                city_dropdown.update()

        country_dropdown.on_change = on_country_change

        # Cargar países al abrir el bottom sheet
        self.page.run_task(load_countries)

        def close_bottom_sheet():
            self.page.close(bottom_sheet)

        async def save_plant():
            logger.info("Iniciando guardado de planta...")
            # Validación simple
            if not name_field.value:
                logger.warning("Validación fallida: Nombre vacío")
                snack = ft.SnackBar(
                    content=ft.Text("El nombre es obligatorio"),
                    bgcolor=ft.Colors.RED_400,
                )
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()
                return

            try:
                import httpx
                
                # Obtener ID de ciudad si se seleccionó
                city_id = int(city_dropdown.value) if city_dropdown.value else None
                logger.debug(f"Datos a enviar: name={name_field.value}, city_id={city_id}, company_id={self.company_id}")

                data = {
                    "name": name_field.value,
                    "address": address_field.value or None,
                    "phone": phone_field.value or None,
                    "email": email_field.value or None,
                    "city_id": city_id,
                    "company_id": self.company_id,
                }

                async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                    logger.info("Enviando petición POST /api/v1/plants/")
                    response = await client.post("/api/v1/plants/", json=data)
                    logger.info(f"Respuesta recibida: {response.status_code}")
                    
                    if response.status_code == 201:
                        close_bottom_sheet()
                        await self._on_plant_saved()
                    else:
                        try:
                            error_detail = response.json().get("detail", t("companies.messages.unknown_error"))
                        except Exception:
                            error_detail = f"Error {response.status_code}"
                        
                        logger.error(f"Error al guardar planta: {error_detail}")
                        snack = ft.SnackBar(
                            content=ft.Text(f"Error: {error_detail}"),
                            bgcolor=ft.Colors.RED_400,
                        )
                        self.page.snack_bar = snack
                        snack.open = True
                        self.page.update()
            except Exception as ex:
                logger.exception(f"Excepción en save_plant: {ex}")
                snack = ft.SnackBar(
                    content=ft.Text(f"Error de conexión: {str(ex)}"),
                    bgcolor=ft.Colors.RED_400,
                )
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()

        # Crear BottomSheet
        bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("Agregar Planta", size=20, weight=ft.FontWeight.BOLD),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    on_click=lambda _: close_bottom_sheet(),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Divider(),
                        name_field,
                        address_field,
                        country_dropdown,
                        city_dropdown,
                        ft.Row(
                            controls=[
                                ft.Container(content=phone_field, expand=1),
                                ft.Container(content=email_field, expand=1),
                            ],
                            spacing=10,
                        ),
                        ft.Row(
                            controls=[
                                ft.TextButton("Cancelar", on_click=lambda _: close_bottom_sheet()),
                                ft.ElevatedButton(
                                    "Guardar",
                                    icon=ft.Icons.SAVE,
                                    on_click=lambda _: self.page.run_task(save_plant),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
            ),
        )

        self.page.open(bottom_sheet)
        logger.info("BottomSheet opened for adding plant")

    def _on_edit_plant(self, e: ft.ControlEvent, plant: dict) -> None:
        """Abre el bottom sheet para editar una planta."""
        logger.info(f"Edit plant clicked: ID={plant.get('id')}")

        plant_id = plant.get("id")

        # Diccionario para almacenar países y sus ciudades
        countries_data = {}
        cities_by_country = {}

        # Crear campos con valores iniciales
        name_field = ft.TextField(label="Nombre de la planta *", value=plant.get("name", ""))
        address_field = ft.TextField(
            label="Dirección",
            value=plant.get("address", ""),
            multiline=True,
            min_lines=2,
            max_lines=3,
        )
        phone_field = ft.TextField(label="Teléfono", value=plant.get("phone", ""), max_length=20)
        email_field = ft.TextField(
            label="Email",
            value=plant.get("email", ""),
            keyboard_type=ft.KeyboardType.EMAIL
        )

        # Determinar país y ciudad actuales
        current_city_id = plant.get("city_id")
        current_country_id = None
        
        # Si tenemos el objeto city completo en la planta (joined loading)
        if isinstance(plant.get("city"), dict):
            current_city_id = plant["city"].get("id")
            current_country_id = plant["city"].get("country_id")

        # Dropdown de ciudades
        city_dropdown = ft.Dropdown(
            label="Ciudad",
            options=[],
            disabled=True,
        )

        # Dropdown de países
        country_dropdown = ft.Dropdown(
            label="País (para filtrar ciudades)",
            options=[],
            disabled=True,
        )

        async def load_countries():
            """Carga los países."""
            try:
                import httpx
                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    response = await client.get("/api/v1/lookups/countries/")
                    if response.status_code == 200:
                        countries = response.json()
                        for country in countries:
                            countries_data[country["id"]] = country["name"]
                        
                        country_dropdown.options = [
                            ft.dropdown.Option(str(cid), cname)
                            for cid, cname in sorted(countries_data.items(), key=lambda x: x[1])
                        ]
                        country_dropdown.disabled = False
                        
                        # Si tenemos current_country_id, seleccionarlo
                        if current_country_id:
                            country_dropdown.value = str(current_country_id)
                            # Y cargar ciudades
                            await load_cities(current_country_id, set_current=True)
                            
                        country_dropdown.update()
                    else:
                        logger.error(f"Error loading countries: {response.status_code}")
            except Exception as ex:
                logger.exception(f"Error loading countries: {ex}")

        async def load_cities(country_id: int, set_current: bool = False):
            """Carga las ciudades."""
            try:
                import httpx
                async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
                    response = await client.get(f"/api/v1/lookups/cities/?country_id={country_id}")
                    if response.status_code == 200:
                        cities = response.json()
                        cities_by_country[country_id] = cities

                        city_dropdown.options = [
                            ft.dropdown.Option(str(city["id"]), city["name"])
                            for city in sorted(cities, key=lambda x: x["name"])
                        ]
                        city_dropdown.disabled = False
                        
                        if set_current and current_city_id:
                            # Verificar si la ciudad actual está en la lista
                            city_ids = [c["id"] for c in cities]
                            if current_city_id in city_ids:
                                city_dropdown.value = str(current_city_id)
                        
                        city_dropdown.update()
                    else:
                        logger.error(f"Error loading cities: {response.status_code}")
            except Exception as ex:
                logger.exception(f"Error loading cities: {ex}")

        def on_country_change(e):
            selected_country_id = e.control.value
            if selected_country_id:
                self.page.run_task(load_cities, int(selected_country_id), False)
            else:
                city_dropdown.options = []
                city_dropdown.disabled = True
                city_dropdown.value = None
                city_dropdown.update()

        country_dropdown.on_change = on_country_change
        self.page.run_task(load_countries)

        def close_bottom_sheet():
            self.page.close(bottom_sheet)

        async def save_plant():
            if not name_field.value:
                snack = ft.SnackBar(content=ft.Text("El nombre es obligatorio"), bgcolor=ft.Colors.RED_400)
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()
                return

            try:
                import httpx
                city_id = int(city_dropdown.value) if city_dropdown.value else None

                data = {
                    "name": name_field.value,
                    "address": address_field.value or None,
                    "phone": phone_field.value or None,
                    "email": email_field.value or None,
                    "city_id": city_id,
                }

                async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                    response = await client.put(f"/api/v1/plants/{plant_id}", json=data)
                    if response.status_code == 200:
                        close_bottom_sheet()
                        await self._on_plant_saved()
                    else:
                        try:
                            error_detail = response.json().get("detail", "Error desconocido")
                        except Exception:
                            error_detail = f"Error {response.status_code}"
                        snack = ft.SnackBar(content=ft.Text(f"Error: {error_detail}"), bgcolor=ft.Colors.RED_400)
                        self.page.snack_bar = snack
                        snack.open = True
                        self.page.update()
            except Exception as ex:
                logger.exception(f"Error saving plant: {ex}")
                snack = ft.SnackBar(content=ft.Text(f"Error de conexión: {str(ex)}"), bgcolor=ft.Colors.RED_400)
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()

        bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("Editar Planta", size=20, weight=ft.FontWeight.BOLD),
                                ft.IconButton(icon=ft.Icons.CLOSE, on_click=lambda _: close_bottom_sheet()),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Divider(),
                        name_field,
                        address_field,
                        country_dropdown,
                        city_dropdown,
                        ft.Row(
                            controls=[
                                ft.Container(content=phone_field, expand=1),
                                ft.Container(content=email_field, expand=1),
                            ],
                            spacing=10,
                        ),
                        ft.Row(
                            controls=[
                                ft.TextButton("Cancelar", on_click=lambda _: close_bottom_sheet()),
                                ft.ElevatedButton("Guardar", icon=ft.Icons.SAVE, on_click=lambda _: self.page.run_task(save_plant)),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
            ),
        )

        self.page.open(bottom_sheet)
        logger.info("BottomSheet opened for editing plant")

    def _on_delete_plant(self, e: ft.ControlEvent, plant: dict) -> None:
        """Muestra confirmación para eliminar una planta."""
        logger.info(f"Delete plant clicked: ID={plant.get('id')}")

        confirm_dialog = ConfirmDialog(
            title="Eliminar Planta",
            message=f"¿Está seguro de que desea eliminar la planta '{plant.get('name')}'?",
            on_confirm=lambda: self.page.run_task(self._confirm_delete_plant, plant.get("id")),
        )

        if self.page:
            confirm_dialog.show(self.page)

    async def _confirm_delete_plant(self, plant_id: int) -> None:
        """Ejecuta la eliminación de una planta."""
        logger.info(f"Confirming deletion of plant ID={plant_id}")

        try:
            import httpx

            async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                response = await client.delete(f"/api/v1/plants/{plant_id}")

                if response.status_code == 200:
                    logger.success(f"Plant {plant_id} deleted successfully")
                    await self._on_plant_saved()
                    self._show_snackbar("Planta eliminada correctamente", ft.Colors.GREEN)
                else:
                    try:
                        error_detail = response.json().get("detail", "Error desconocido")
                    except Exception:
                        error_detail = f"Error {response.status_code}"
                    logger.error(f"Error deleting plant: {response.status_code} - {error_detail}")
                    self._show_snackbar(f"Error al eliminar: {error_detail}", ft.Colors.RED_400)

        except Exception as e:
            logger.exception(f"Error deleting plant: {e}")
            self._show_snackbar(f"Error de conexión: {str(e)}", ft.Colors.RED_400)

    async def _on_plant_saved(self) -> None:
        """Callback después de guardar/eliminar una planta."""
        logger.info("Plant saved, reloading plants")
        await self._reload_plants()
        self._show_snackbar("Cambios guardados exitosamente", ft.Colors.GREEN)

    async def _reload_plants(self) -> None:
        """Recarga solo las plantas desde la API."""
        try:
            import httpx

            async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                response = await client.get(f"/api/v1/plants/company/{self.company_id}")
                if response.status_code == 200:
                    self._plants = response.json()
                    logger.success(f"Reloaded {len(self._plants)} plants")
                else:
                    logger.warning(f"Error reloading plants: {response.status_code}")
                    self._plants = []

        except Exception as e:
            logger.exception(f"Error reloading plants: {e}")
            self._plants = []

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
        logger.debug("CompanyDetailView state changed, rebuilding content")
        # Reconstruir el contenido con las nuevas traducciones
        self.content = self.build()
        if self.page:
            self.update()

    # ========================================================================
    # MÉTODOS PARA RUTS
    # ========================================================================

    def _on_add_rut(self, e: ft.ControlEvent) -> None:
        """Abre el bottom sheet para agregar un nuevo RUT."""
        logger.info(f"Add RUT clicked for company ID={self.company_id}")

        def on_rut_change(e):
            """Valida y formatea el RUT mientras se escribe."""
            value = rut_field.value
            
            # Formatear si tiene largo suficiente
            if len(value) >= 8:
                formatted = format_rut(value)
                if formatted != value:
                    rut_field.value = formatted
                    rut_field.update()
            
            # Validar
            is_valid, error = validate_rut(rut_field.value)
            if not is_valid:
                rut_field.error_text = error
            else:
                rut_field.error_text = None
            rut_field.update()

        # Crear campos del formulario
        rut_field = ft.TextField(
            label="RUT *",
            hint_text="Ej: 76.123.456-7 o 76123456-7",
            on_change=on_rut_change,
        )
        is_main_checkbox = ft.Checkbox(
            label="RUT principal",
            value=False,
        )

        def close_bottom_sheet():
            self.page.close(bottom_sheet)

        async def save_rut():
            # Validación
            is_valid, error = validate_rut(rut_field.value)
            if not is_valid:
                rut_field.error_text = error
                rut_field.update()
                return

            try:
                import httpx
                # Enviar el RUT formateado
                formatted_rut = format_rut(rut_field.value)
                data = {
                    "rut": formatted_rut,
                    "is_main": is_main_checkbox.value,
                    "company_id": self.company_id,
                }

                async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                    response = await client.post("/api/v1/company-ruts/", json=data)
                    if response.status_code == 201:
                        close_bottom_sheet()
                        await self._on_rut_saved()
                    else:
                        try:
                            error_data = response.json()
                            if "detail" in error_data:
                                if isinstance(error_data["detail"], list):
                                    # Pydantic error
                                    error_msgs = [e["msg"] for e in error_data["detail"]]
                                    error_detail = "\n".join(error_msgs)
                                else:
                                    error_detail = str(error_data["detail"])
                            else:
                                error_detail = "Error desconocido"
                        except Exception:
                            error_detail = f"Error {response.status_code}: {response.text}"

                        snack = ft.SnackBar(
                            content=ft.Text(f"Error: {error_detail}"),
                            bgcolor=ft.Colors.RED_400,
                        )
                        self.page.snack_bar = snack
                        snack.open = True
                        self.page.update()
            except Exception as ex:
                logger.exception(f"Error saving RUT: {ex}")
                snack = ft.SnackBar(
                    content=ft.Text(f"Error de conexión: {str(ex)}"),
                    bgcolor=ft.Colors.RED_400,
                )
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()

        # Crear BottomSheet
        bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("Agregar RUT", size=20, weight=ft.FontWeight.BOLD),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    on_click=lambda _: close_bottom_sheet(),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Divider(),
                        rut_field,
                        is_main_checkbox,
                        ft.Row(
                            controls=[
                                ft.TextButton("Cancelar", on_click=lambda _: close_bottom_sheet()),
                                ft.ElevatedButton(
                                    "Guardar",
                                    icon=ft.Icons.SAVE,
                                    on_click=lambda _: self.page.run_task(save_rut),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
            ),
        )

        self.page.open(bottom_sheet)
        logger.info("BottomSheet opened for adding RUT")

    def _on_edit_rut(self, e: ft.ControlEvent, rut: dict) -> None:
        """Abre el bottom sheet para editar un RUT."""
        logger.info(f"Edit RUT clicked: ID={rut.get('id')}")

        rut_id = rut.get("id")

        def on_rut_change(e):
            """Valida y formatea el RUT mientras se escribe."""
            value = rut_field.value
            
            # Formatear si tiene largo suficiente
            if len(value) >= 8:
                formatted = format_rut(value)
                if formatted != value:
                    rut_field.value = formatted
                    rut_field.update()
            
            # Validar
            is_valid, error = validate_rut(rut_field.value)
            if not is_valid:
                rut_field.error_text = error
            else:
                rut_field.error_text = None
            rut_field.update()

        # Crear campos del formulario con datos iniciales
        rut_field = ft.TextField(
            label="RUT *",
            value=rut.get("rut", ""),
            hint_text="Ej: 76.123.456-7 o 76123456-7",
            on_change=on_rut_change,
        )
        is_main_checkbox = ft.Checkbox(
            label="RUT principal",
            value=rut.get("is_main", False),
        )

        def close_bottom_sheet():
            self.page.close(bottom_sheet)

        async def save_rut():
            # Validación
            is_valid, error = validate_rut(rut_field.value)
            if not is_valid:
                rut_field.error_text = error
                rut_field.update()
                return

            try:
                import httpx
                # Enviar el RUT formateado
                formatted_rut = format_rut(rut_field.value)
                data = {
                    "rut": formatted_rut,
                    "is_main": is_main_checkbox.value,
                }

                async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                    response = await client.put(
                        f"/api/v1/company-ruts/{rut_id}", json=data
                    )
                    if response.status_code == 200:
                        close_bottom_sheet()
                        await self._on_rut_saved()
                    else:
                        try:
                            error_data = response.json()
                            if "detail" in error_data:
                                if isinstance(error_data["detail"], list):
                                    # Pydantic error
                                    error_msgs = [e["msg"] for e in error_data["detail"]]
                                    error_detail = "\n".join(error_msgs)
                                else:
                                    error_detail = str(error_data["detail"])
                            else:
                                error_detail = "Error desconocido"
                        except Exception:
                            error_detail = f"Error {response.status_code}: {response.text}"

                        snack = ft.SnackBar(
                            content=ft.Text(f"Error: {error_detail}"),
                            bgcolor=ft.Colors.RED_400,
                        )
                        self.page.snack_bar = snack
                        snack.open = True
                        self.page.update()
            except Exception as ex:
                logger.exception(f"Error saving RUT: {ex}")
                snack = ft.SnackBar(
                    content=ft.Text(f"Error de conexión: {str(ex)}"),
                    bgcolor=ft.Colors.RED_400,
                )
                self.page.snack_bar = snack
                snack.open = True
                self.page.update()

        # Crear BottomSheet
        bottom_sheet = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("Editar RUT", size=20, weight=ft.FontWeight.BOLD),
                                ft.IconButton(
                                    icon=ft.Icons.CLOSE,
                                    on_click=lambda _: close_bottom_sheet(),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        ft.Divider(),
                        rut_field,
                        is_main_checkbox,
                        ft.Row(
                            controls=[
                                ft.TextButton("Cancelar", on_click=lambda _: close_bottom_sheet()),
                                ft.ElevatedButton(
                                    "Guardar",
                                    icon=ft.Icons.SAVE,
                                    on_click=lambda _: self.page.run_task(save_rut),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,
                            spacing=10,
                        ),
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                ),
                padding=20,
            ),
        )

        self.page.open(bottom_sheet)
        logger.info("BottomSheet opened for editing RUT")

    def _on_delete_rut(self, e: ft.ControlEvent, rut: dict) -> None:
        """Muestra confirmación para eliminar un RUT."""
        logger.info(f"Delete RUT clicked: ID={rut.get('id')}")

        confirm_dialog = ConfirmDialog(
            title="Eliminar RUT",
            message=f"¿Está seguro de que desea eliminar el RUT '{rut.get('rut')}'?",
            on_confirm=lambda: self.page.run_task(self._confirm_delete_rut, rut.get("id")),
        )

        if self.page:
            confirm_dialog.show(self.page)

    async def _confirm_delete_rut(self, rut_id: int) -> None:
        """Ejecuta la eliminación de un RUT."""
        logger.info(f"Confirming deletion of RUT ID={rut_id}")

        try:
            import httpx

            async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                response = await client.delete(f"/api/v1/company-ruts/{rut_id}")

                if response.status_code == 200:
                    logger.success(f"RUT {rut_id} deleted successfully")
                    await self._on_rut_saved()
                    self._show_snackbar("RUT eliminado exitosamente", ft.Colors.GREEN)
                else:
                    try:
                        error_detail = response.json().get("detail", "Error desconocido")
                    except Exception:
                        error_detail = f"Error {response.status_code}"
                    logger.error(f"Error deleting RUT: {response.status_code} - {error_detail}")
                    self._show_snackbar(f"Error al eliminar: {error_detail}", ft.Colors.RED_400)

        except Exception as e:
            logger.exception(f"Error deleting RUT: {e}")
            self._show_snackbar(f"Error de conexión: {str(e)}", ft.Colors.RED_400)

    async def _on_rut_saved(self) -> None:
        """Callback después de guardar/eliminar un RUT."""
        logger.info("RUT saved, reloading RUTs")
        await self._reload_ruts()
        self._show_snackbar("Cambios guardados exitosamente", ft.Colors.GREEN)

    async def _reload_ruts(self) -> None:
        """Recarga solo los RUTs desde la API."""
        try:
            import httpx

            async with httpx.AsyncClient(base_url="http://localhost:8000", follow_redirects=True) as client:
                response = await client.get(f"/api/v1/company-ruts/company/{self.company_id}")
                if response.status_code == 200:
                    self._ruts = response.json()
                    logger.success(f"Reloaded {len(self._ruts)} RUTs")
                else:
                    logger.warning(f"Error reloading RUTs: {response.status_code}")
                    self._ruts = []

        except Exception as e:
            logger.exception(f"Error reloading RUTs: {e}")
            self._ruts = []

        # Reconstruir solo el contenido
        self.content = self.build()
        if self.page:
            self.update()
