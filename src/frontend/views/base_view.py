"""
Vista base para todas las vistas de la aplicación.
"""

import flet as ft


class BaseView:
    """
    Vista base para todas las vistas de la aplicación.

    Proporciona funcionalidad común y estructura para todas las vistas.
    """

    def __init__(self, page: ft.Page):
        """
        Inicializa la vista base.

        Args:
            page: Página de Flet
        """
        self.page = page

    def build(self):
        """
        Construye la vista.

        Las subclases deben implementar este método.

        Returns:
            Control de Flet
        """
        return ft.Text("Vista base - implementar en subclase")
