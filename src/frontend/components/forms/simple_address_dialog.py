"""
Diálogo simplificado para direcciones usando controles nativos de Flet.
Version de prueba para diagnosticar problemas de renderizado.
"""
from typing import Callable
import flet as ft
from loguru import logger


def show_simple_address_dialog(
    page: ft.Page,
    mode: str = "create",
    initial_data: dict | None = None,
    on_save: Callable[[], None] | None = None,
) -> None:
    """Muestra un diálogo simple de dirección con controles nativos."""

    logger.info(f"Simple address dialog: mode={mode}")

    initial_data = initial_data or {}

    # Controles nativos de Flet (sin wrappers personalizados)
    address_field = ft.TextField(
        label="Dirección *",
        value=initial_data.get("address", ""),
        multiline=True,
        min_lines=2,
        max_lines=4,
    )

    city_field = ft.TextField(
        label="Ciudad",
        value=initial_data.get("city", ""),
    )

    postal_code_field = ft.TextField(
        label="Código Postal",
        value=initial_data.get("postal_code", ""),
    )

    type_dropdown = ft.Dropdown(
        label="Tipo de Dirección *",
        value=initial_data.get("address_type", "delivery"),
        options=[
            ft.dropdown.Option("delivery", "Entrega"),
            ft.dropdown.Option("billing", "Facturación"),
            ft.dropdown.Option("headquarters", "Sede Principal"),
            ft.dropdown.Option("branch", "Sucursal"),
        ],
    )

    def close_dialog(e):
        dialog.open = False
        page.update()
        logger.info("Simple dialog closed")

    def save_and_close(e):
        logger.info(f"Save clicked: address={address_field.value}")
        close_dialog(e)
        if on_save:
            on_save()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Editar Dirección" if mode == "edit" else "Agregar Dirección"),
        content=ft.Column(
            controls=[
                address_field,
                city_field,
                postal_code_field,
                type_dropdown,
            ],
            tight=True,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=close_dialog),
            ft.ElevatedButton("Guardar", on_click=save_and_close),
        ],
    )

    logger.info("Creating simple AlertDialog")
    page.dialog = dialog
    dialog.open = True
    page.update()
    logger.success("Simple dialog should be visible now")
