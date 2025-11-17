"""
Script de prueba para verificar si los diálogos funcionan con controles nativos.
"""
import flet as ft

def main(page: ft.Page):
    page.title = "Test Dialog"

    def show_simple_dialog(e):
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Test Dialog"),
            content=ft.Column(
                controls=[
                    ft.TextField(label="Campo 1", hint_text="Ingrese texto"),
                    ft.TextField(label="Campo 2", hint_text="Ingrese texto"),
                    ft.Dropdown(
                        label="Dropdown",
                        options=[
                            ft.dropdown.Option("1", "Opción 1"),
                            ft.dropdown.Option("2", "Opción 2"),
                        ],
                    ),
                ],
                tight=True,
                width=500,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: close_dialog(dialog)),
                ft.ElevatedButton("Guardar", on_click=lambda e: close_dialog(dialog)),
            ],
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    def close_dialog(dialog):
        dialog.open = False
        page.update()

    page.add(
        ft.ElevatedButton("Mostrar Diálogo Simple", on_click=show_simple_dialog)
    )

if __name__ == "__main__":
    ft.app(target=main)
