"""
Vista de listado de empresas.

Muestra una tabla con todas las empresas y permite CRUD operations.
"""

import flet as ft
from loguru import logger

from src.frontend.views.base_view import BaseView
from src.frontend.services.company_api import CompanyAPIClient, APIException
from src.shared.schemas.core.company import CompanyResponse


class CompaniesListView(BaseView):
    """
    Vista de listado de empresas.

    Muestra una tabla con todas las empresas y proporciona
    funcionalidad para crear, editar y eliminar empresas.

    Example:
        view = CompaniesListView(page)
        page.add(view)
    """

    def __init__(self, page: ft.Page) -> None:
        """
        Inicializa la vista de listado de empresas.

        Args:
            page: Página de Flet
        """
        super().__init__(page)
        self.api_client = CompanyAPIClient()
        self.companies: list[CompanyResponse] = []
        self.data_table: ft.DataTable | None = None

    def build(self) -> ft.Control:
        """
        Construye la vista de listado de empresas.

        Returns:
            Control de Flet con la vista completa
        """
        # Header con título y botón de crear
        header = ft.Row(
            [
                ft.Text(
                    "Empresas",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Container(expand=True),
                ft.ElevatedButton(
                    "Nueva Empresa",
                    icon=ft.icons.ADD,
                    on_click=self._on_create_company,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Barra de búsqueda
        search_bar = ft.Row(
            [
                ft.TextField(
                    label="Buscar empresa",
                    hint_text="Nombre o trigram",
                    prefix_icon=ft.icons.SEARCH,
                    on_change=self._on_search,
                    expand=True,
                ),
                ft.IconButton(
                    icon=ft.icons.REFRESH,
                    tooltip="Actualizar",
                    on_click=lambda _: self._load_companies(),
                ),
            ],
        )

        # Tabla de datos
        self.data_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Trigram")),
                ft.DataColumn(ft.Text("Tipo")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Activa")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
            border=ft.border.all(1, ft.colors.GREY_400),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_300),
            horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_300),
        )

        # Cargar datos iniciales
        self._load_companies()

        # Layout principal
        return ft.Column(
            [
                header,
                ft.Divider(),
                search_bar,
                ft.Container(height=20),
                ft.Container(
                    content=self.data_table,
                    border=ft.border.all(1, ft.colors.GREY_400),
                    border_radius=10,
                    padding=10,
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )

    def _load_companies(self) -> None:
        """
        Carga las empresas desde la API.

        Muestra loading spinner mientras carga.
        """
        try:
            self.show_loading("Cargando empresas...")
            self.companies = self.api_client.get_all_companies()
            self._update_table()
            self.hide_loading()
            logger.info(f"Loaded {len(self.companies)} companies")
        except APIException as e:
            self.hide_loading()
            self.show_snackbar(
                f"Error cargando empresas: {e.message}",
                "error",
            )
            logger.error(f"Error loading companies: {e}")
        except Exception as e:
            self.hide_loading()
            self.show_snackbar(
                f"Error inesperado: {str(e)}",
                "error",
            )
            logger.exception("Unexpected error loading companies")

    def _update_table(self) -> None:
        """
        Actualiza la tabla con las empresas cargadas.
        """
        if not self.data_table:
            return

        self.data_table.rows.clear()

        for company in self.companies:
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(company.id))),
                    ft.DataCell(ft.Text(company.name)),
                    ft.DataCell(ft.Text(company.trigram)),
                    ft.DataCell(ft.Text(str(company.company_type_id))),
                    ft.DataCell(ft.Text(company.phone or "-")),
                    ft.DataCell(
                        ft.Icon(
                            ft.icons.CHECK_CIRCLE if company.is_active
                            else ft.icons.CANCEL,
                            color=ft.colors.GREEN if company.is_active
                            else ft.colors.RED,
                        )
                    ),
                    ft.DataCell(
                        ft.Row(
                            [
                                ft.IconButton(
                                    icon=ft.icons.EDIT,
                                    tooltip="Editar",
                                    on_click=lambda _, c=company: self._on_edit_company(c),
                                ),
                                ft.IconButton(
                                    icon=ft.icons.DELETE,
                                    tooltip="Eliminar",
                                    icon_color=ft.colors.RED,
                                    on_click=lambda _, c=company: self._on_delete_company(c),
                                ),
                            ],
                            spacing=0,
                        )
                    ),
                ],
            )
            self.data_table.rows.append(row)

        self.update()

    def _on_search(self, e: ft.ControlEvent) -> None:
        """
        Maneja la búsqueda de empresas.

        Args:
            e: Evento de cambio del TextField
        """
        search_term = e.control.value.lower().strip()

        if not search_term:
            self._load_companies()
            return

        try:
            self.companies = self.api_client.search_companies(search_term)
            self._update_table()
            logger.debug(f"Search results: {len(self.companies)} companies")
        except APIException as e:
            self.show_snackbar(f"Error en búsqueda: {e.message}", "error")
            logger.error(f"Search error: {e}")

    def _on_create_company(self, e: ft.ControlEvent) -> None:
        """
        Maneja el click en botón de crear empresa.

        Args:
            e: Evento del botón
        """
        # TODO: Implementar formulario de creación
        self.show_snackbar(
            "Formulario de creación en desarrollo",
            "info",
        )
        logger.debug("Create company clicked")

    def _on_edit_company(self, company: CompanyResponse) -> None:
        """
        Maneja el click en botón de editar empresa.

        Args:
            company: Empresa a editar
        """
        # TODO: Implementar formulario de edición
        self.show_snackbar(
            f"Editar {company.name} - En desarrollo",
            "info",
        )
        logger.debug(f"Edit company {company.id} clicked")

    def _on_delete_company(self, company: CompanyResponse) -> None:
        """
        Maneja el click en botón de eliminar empresa.

        Args:
            company: Empresa a eliminar
        """
        def confirm_delete(e: ft.ControlEvent) -> None:
            try:
                self.api_client.delete_company(company.id)
                self.show_snackbar(
                    f"Empresa {company.name} eliminada",
                    "success",
                )
                self._load_companies()
                dialog.open = False
                self.page.update()
            except APIException as e:
                self.show_snackbar(
                    f"Error eliminando empresa: {e.message}",
                    "error",
                )
                logger.error(f"Delete error: {e}")

        def cancel(e: ft.ControlEvent) -> None:
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmar Eliminación"),
            content=ft.Text(
                f"¿Está seguro que desea eliminar la empresa '{company.name}'?\n\n"
                "Esta acción no se puede deshacer."
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=cancel),
                ft.ElevatedButton(
                    "Eliminar",
                    on_click=confirm_delete,
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.RED,
                ),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
