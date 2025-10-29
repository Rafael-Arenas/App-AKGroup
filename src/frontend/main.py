"""
Punto de entrada de la aplicación Frontend Flet.

Aplicación de escritorio cross-platform para AK Group.
"""

import flet as ft
from loguru import logger

from src.frontend.config.settings import settings
from src.frontend.views.companies.companies_list_view import CompaniesListView


def main(page: ft.Page) -> None:
    """
    Función principal de la aplicación Flet.

    Configura la aplicación y maneja el routing.

    Args:
        page: Página principal de Flet
    """
    # Configurar página
    page.title = settings.app_title
    page.window_width = settings.app_width
    page.window_height = settings.app_height
    page.theme_mode = (
        ft.ThemeMode.DARK if settings.ui_theme == "dark"
        else ft.ThemeMode.LIGHT
    )
    page.padding = 20

    logger.info(f"Starting {settings.app_title}")
    logger.info(f"API URL: {settings.api_url}")

    def route_change(e: ft.RouteChangeEvent) -> None:
        """
        Maneja cambios de ruta.

        Args:
            e: Evento de cambio de ruta
        """
        page.views.clear()

        # AppBar común para todas las vistas
        app_bar = ft.AppBar(
            title=ft.Text(settings.app_title),
            center_title=False,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.IconButton(
                    icon=ft.icons.HOME,
                    tooltip="Inicio",
                    on_click=lambda _: page.go("/"),
                ),
                ft.IconButton(
                    icon=ft.icons.BUSINESS,
                    tooltip="Empresas",
                    on_click=lambda _: page.go("/companies"),
                ),
                ft.IconButton(
                    icon=ft.icons.INVENTORY,
                    tooltip="Productos",
                    on_click=lambda _: page.go("/products"),
                ),
                ft.IconButton(
                    icon=ft.icons.SETTINGS,
                    tooltip="Configuración",
                    on_click=lambda _: page.go("/settings"),
                ),
            ],
        )

        # Routing
        if page.route == "/":
            # Vista de inicio
            page.views.append(
                ft.View(
                    "/",
                    [
                        app_bar,
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Bienvenido a AK Group",
                                        size=40,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        "Sistema de Gestión Empresarial",
                                        size=20,
                                    ),
                                    ft.Container(height=30),
                                    ft.Row(
                                        [
                                            ft.ElevatedButton(
                                                "Empresas",
                                                icon=ft.icons.BUSINESS,
                                                on_click=lambda _: page.go("/companies"),
                                                style=ft.ButtonStyle(
                                                    padding=20,
                                                ),
                                            ),
                                            ft.ElevatedButton(
                                                "Productos",
                                                icon=ft.icons.INVENTORY,
                                                on_click=lambda _: page.go("/products"),
                                                style=ft.ButtonStyle(
                                                    padding=20,
                                                ),
                                            ),
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=20,
                                    ),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=20,
                            ),
                            alignment=ft.alignment.center,
                            expand=True,
                        ),
                    ],
                )
            )

        elif page.route == "/companies":
            # Vista de empresas
            page.views.append(
                ft.View(
                    "/companies",
                    [
                        app_bar,
                        CompaniesListView(page),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                )
            )

        elif page.route == "/products":
            # Vista de productos (placeholder)
            page.views.append(
                ft.View(
                    "/products",
                    [
                        app_bar,
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Productos",
                                        size=32,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text("Vista en desarrollo..."),
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            alignment=ft.alignment.center,
                            expand=True,
                        ),
                    ],
                )
            )

        elif page.route == "/settings":
            # Vista de configuración (placeholder)
            page.views.append(
                ft.View(
                    "/settings",
                    [
                        app_bar,
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Configuración",
                                        size=32,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Divider(),
                                    ft.ListTile(
                                        leading=ft.Icon(ft.icons.API),
                                        title=ft.Text("API URL"),
                                        subtitle=ft.Text(settings.api_url),
                                    ),
                                    ft.ListTile(
                                        leading=ft.Icon(ft.icons.PALETTE),
                                        title=ft.Text("Tema"),
                                        subtitle=ft.Text(settings.ui_theme),
                                    ),
                                    ft.ListTile(
                                        leading=ft.Icon(ft.icons.INFO),
                                        title=ft.Text("Versión"),
                                        subtitle=ft.Text("1.0.0"),
                                    ),
                                ],
                            ),
                            padding=20,
                        ),
                    ],
                )
            )

        page.update()

    def view_pop(e: ft.ViewPopEvent) -> None:
        """
        Maneja el evento de volver atrás.

        Args:
            e: Evento de pop de vista
        """
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    # Configurar event handlers
    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # Ir a la ruta inicial
    page.go(page.route)


if __name__ == "__main__":
    logger.info("Starting Flet application...")
    ft.app(target=main)
