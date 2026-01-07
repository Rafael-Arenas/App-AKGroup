"""
Ejemplo de integración de servicios API con Flet.

Este archivo muestra cómo integrar los servicios API con componentes Flet
para crear una interfaz de usuario reactiva.
"""

import flet as ft  # type: ignore
from loguru import logger

from . import company_api, APIException, NotFoundException


class CompanyListView(ft.Container):
    """
    Vista de lista de empresas con operaciones CRUD.

    Ejemplo de componente Flet que usa los servicios API para:
    - Listar empresas
    - Buscar empresas
    - Crear nuevas empresas
    - Actualizar empresas existentes
    - Eliminar empresas
    """

    def __init__(self) -> None:
        """Inicializa la vista de lista de empresas."""
        super().__init__()
        self.companies: list[dict] = []
        self.is_loading = False

        # Componentes UI
        self.search_field = ft.TextField(
            label="Buscar empresa",
            hint_text="Ingrese el nombre de la empresa",
            on_change=self.on_search_changed,
            expand=True,
        )

        self.companies_list = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
        )

        self.loading_indicator = ft.ProgressRing(visible=False)

    def build(self) -> ft.Control:
        """
        Construye la interfaz de usuario.

        Returns:
            Control de Flet con la UI completa
        """
        return ft.Column(
            controls=[
                # Header
                ft.Row(
                    controls=[
                        ft.Text("Empresas", size=24, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            tooltip="Actualizar lista",
                            on_click=lambda _: self.load_companies(),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            tooltip="Nueva empresa",
                            on_click=lambda _: self.show_create_dialog(),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                # Búsqueda
                ft.Row(
                    controls=[
                        self.search_field,
                        ft.IconButton(
                            icon=ft.Icons.SEARCH,
                            tooltip="Buscar",
                            on_click=lambda _: self.search_companies(),
                        ),
                    ]
                ),
                # Loading indicator
                ft.Row(
                    controls=[self.loading_indicator],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                # Lista de empresas
                ft.Container(
                    content=self.companies_list,
                    expand=True,
                    border=ft.border.all(1, ft.Colors.OUTLINE),
                    border_radius=10,
                ),
            ],
            spacing=20,
            expand=True,
        )

    async def did_mount(self) -> None:
        """Se ejecuta cuando el componente se monta en la página."""
        await self.load_companies()

    async def load_companies(self) -> None:
        """Carga la lista de empresas desde el backend."""
        try:
            self.set_loading(True)

            # Llamar al servicio API
            self.companies = await company_api.get_active()

            # Actualizar UI
            self.update_companies_list()
            self.show_snackbar("Empresas cargadas exitosamente", is_error=False)

        except APIException as e:
            logger.error(f"Error al cargar empresas: {e.message}")
            self.show_snackbar(f"Error: {e.message}", is_error=True)

        finally:
            self.set_loading(False)

    async def search_companies(self) -> None:
        """Busca empresas por nombre."""
        search_text = self.search_field.value

        if not search_text or search_text.strip() == "":
            await self.load_companies()
            return

        try:
            self.set_loading(True)

            # Llamar al servicio API
            self.companies = await company_api.search(search_text.strip())

            # Actualizar UI
            self.update_companies_list()

            if len(self.companies) == 0:
                self.show_snackbar(
                    f"No se encontraron empresas con '{search_text}'",
                    is_error=False,
                )
            else:
                self.show_snackbar(
                    f"Se encontraron {len(self.companies)} empresas",
                    is_error=False,
                )

        except APIException as e:
            logger.error(f"Error al buscar empresas: {e.message}")
            self.show_snackbar(f"Error: {e.message}", is_error=True)

        finally:
            self.set_loading(False)

    def on_search_changed(self, e: ft.ControlEvent) -> None:  # type: ignore
        """Se ejecuta cuando cambia el texto de búsqueda."""
        # Buscar automáticamente cuando el campo está vacío
        if not self.search_field.value or self.search_field.value.strip() == "":
            # Nota: En producción usar un debounce aquí
            pass  # load_companies() necesita await, ignorar en callback síncrono

    def update_companies_list(self) -> None:
        """Actualiza la lista de empresas en la UI."""
        self.companies_list.controls.clear()

        if not self.companies:
            self.companies_list.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No hay empresas para mostrar",
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.GREY,
                    ),
                    alignment=ft.Alignment(0, 0),  # center
                    padding=50,
                )
            )
        else:
            for company in self.companies:
                self.companies_list.controls.append(self.create_company_card(company))

        self.update()

    def create_company_card(self, company: dict) -> ft.Control:
        """
        Crea una tarjeta para mostrar una empresa.

        Args:
            company: Datos de la empresa

        Returns:
            Card de Flet con la información de la empresa
        """
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.ListTile(
                            leading=ft.Icon(ft.Icons.BUSINESS),
                            title=ft.Text(company["name"], weight=ft.FontWeight.BOLD),
                            subtitle=ft.Text(
                                f"NIT: {company.get('nit', 'N/A')} | "
                                f"Email: {company.get('email', 'N/A')}"
                            ),
                            trailing=ft.Row(
                                controls=[
                                    ft.IconButton(
                                        icon=ft.Icons.EDIT,
                                        tooltip="Editar",
                                        on_click=lambda _, c=company: self.show_edit_dialog(
                                            c
                                        ),
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE,
                                        tooltip="Eliminar",
                                        icon_color=ft.Colors.RED,
                                        on_click=lambda _, c=company: self.confirm_delete(
                                            c
                                        ),
                                    ),
                                ],
                                spacing=0,
                            ),
                        ),
                    ],
                ),
                padding=10,
            ),
        )

    async def delete_company(self, company: dict) -> None:
        """
        Elimina una empresa.

        Args:
            company: Datos de la empresa a eliminar
        """
        try:
            self.set_loading(True)

            # Llamar al servicio API
            await company_api.delete(company["id"])

            # Remover de la lista local
            self.companies = [c for c in self.companies if c["id"] != company["id"]]

            # Actualizar UI
            self.update_companies_list()
            self.show_snackbar(
                f"Empresa '{company['name']}' eliminada exitosamente",
                is_error=False,
            )

        except NotFoundException:
            self.show_snackbar("La empresa ya no existe", is_error=True)
            await self.load_companies()

        except APIException as e:
            logger.error(f"Error al eliminar empresa: {e.message}")
            self.show_snackbar(f"Error: {e.message}", is_error=True)

        finally:
            self.set_loading(False)

    def confirm_delete(self, company: dict) -> None:  # type: ignore
        """
        Muestra un diálogo de confirmación para eliminar una empresa.

        Args:
            company: Datos de la empresa a eliminar
        """
        dlg: ft.AlertDialog = ft.AlertDialog(  # type: ignore
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(
                f"¿Está seguro que desea eliminar la empresa '{company['name']}'?"
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda _: self.close_dialog(dlg)),
                ft.TextButton(
                    "Eliminar",
                    on_click=lambda _: self.handle_delete_confirm(dlg, company),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def handle_delete_confirm(self, dialog: ft.AlertDialog, company: dict) -> None:  # type: ignore
        """Maneja la confirmación de eliminación."""
        self.close_dialog(dialog)
        # Nota: delete_company() necesita await, este es solo un ejemplo simplificado
        # En producción, usar page.run_task() o similar

    def show_create_dialog(self) -> None:
        """Muestra el diálogo para crear una nueva empresa."""
        # TODO: Implementar diálogo de creación
        self.show_snackbar("Funcionalidad en desarrollo", is_error=False)

    def show_edit_dialog(self, company: dict) -> None:
        """
        Muestra el diálogo para editar una empresa.

        Args:
            company: Datos de la empresa a editar
        """
        # TODO: Implementar diálogo de edición
        self.show_snackbar("Funcionalidad en desarrollo", is_error=False)

    def close_dialog(self, dialog: ft.AlertDialog) -> None:
        """Cierra un diálogo."""
        dialog.open = False
        self.page.update()

    def set_loading(self, is_loading: bool) -> None:
        """
        Establece el estado de carga.

        Args:
            is_loading: True si está cargando, False si no
        """
        self.is_loading = is_loading
        self.loading_indicator.visible = is_loading
        self.update()

    def show_snackbar(self, message: str, is_error: bool = False) -> None:
        """
        Muestra un snackbar con un mensaje.

        Args:
            message: Mensaje a mostrar
            is_error: True si es un mensaje de error, False si no
        """
        if not self.page:
            return

        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED if is_error else ft.Colors.GREEN,
        )
        self.page.snack_bar.open = True
        self.page.update()


async def main(page: ft.Page) -> None:
    """
    Función principal de la aplicación Flet.

    Args:
        page: Página de Flet
    """
    page.title = "Gestión de Empresas - AK Group"
    page.padding = 20

    # Agregar vista de empresas
    company_view = CompanyListView()
    page.add(company_view)


if __name__ == "__main__":
    # Configurar logger
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True,
    )

    # Ejecutar aplicación Flet
    ft.app(target=main)
