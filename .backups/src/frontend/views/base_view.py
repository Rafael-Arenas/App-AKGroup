"""
Vista base para todas las vistas de la aplicación.

Proporciona funcionalidad común y estructura para vistas específicas.
"""

from abc import ABC, abstractmethod
import flet as ft
from loguru import logger


class BaseView(ft.UserControl, ABC):
    """
    Clase base abstracta para todas las vistas.

    Todas las vistas deben heredar de esta clase e implementar
    el método build().

    Example:
        class HomeView(BaseView):
            def build(self) -> ft.Control:
                return ft.Text("Welcome!")
    """

    def __init__(self, page: ft.Page) -> None:
        """
        Inicializa la vista base.

        Args:
            page: Página de Flet donde se renderizará la vista
        """
        super().__init__()
        self.page = page
        logger.debug(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def build(self) -> ft.Control:
        """
        Construye y retorna el control de Flet para esta vista.

        Este método debe ser implementado por todas las subclases.

        Returns:
            Control de Flet que representa la vista

        Example:
            def build(self) -> ft.Control:
                return ft.Column([
                    ft.Text("Hello"),
                    ft.ElevatedButton("Click me")
                ])
        """
        pass

    def show_snackbar(
        self,
        message: str,
        severity: str = "info",
    ) -> None:
        """
        Muestra un snackbar con un mensaje.

        Args:
            message: Mensaje a mostrar
            severity: Nivel de severidad (success, error, warning, info)

        Example:
            self.show_snackbar("Operación exitosa", "success")
        """
        colors = {
            "success": ft.colors.GREEN,
            "error": ft.colors.RED,
            "warning": ft.colors.ORANGE,
            "info": ft.colors.BLUE,
        }

        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=colors.get(severity, ft.colors.BLUE),
        )
        self.page.snack_bar.open = True
        self.page.update()

    def show_dialog(
        self,
        title: str,
        content: str | ft.Control,
        actions: list[ft.Control] | None = None,
    ) -> None:
        """
        Muestra un diálogo modal.

        Args:
            title: Título del diálogo
            content: Contenido del diálogo (texto o control)
            actions: Lista de botones de acción

        Example:
            self.show_dialog(
                "Confirmar",
                "¿Está seguro?",
                [
                    ft.TextButton("Cancelar", on_click=lambda _: close()),
                    ft.ElevatedButton("Aceptar", on_click=lambda _: do_action())
                ]
            )
        """
        if isinstance(content, str):
            content = ft.Text(content)

        def close_dialog(e: ft.ControlEvent | None = None) -> None:
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=content,
            actions=actions or [
                ft.TextButton("Cerrar", on_click=close_dialog)
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_loading(self, message: str = "Cargando...") -> None:
        """
        Muestra indicador de carga.

        Args:
            message: Mensaje a mostrar durante la carga

        Example:
            self.show_loading("Guardando datos...")
        """
        self.page.overlay.append(
            ft.Container(
                content=ft.Column(
                    [
                        ft.ProgressRing(),
                        ft.Text(message),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                alignment=ft.alignment.center,
                bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLACK),
                expand=True,
            )
        )
        self.page.update()

    def hide_loading(self) -> None:
        """
        Oculta indicador de carga.

        Example:
            self.hide_loading()
        """
        if self.page.overlay:
            self.page.overlay.clear()
            self.page.update()

    def navigate_to(self, route: str) -> None:
        """
        Navega a otra ruta de la aplicación.

        Args:
            route: Ruta destino (ej: /companies, /products)

        Example:
            self.navigate_to("/companies")
        """
        self.page.go(route)
        logger.debug(f"Navigated to {route}")
