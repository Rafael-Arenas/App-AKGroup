"""
Componente de barra de búsqueda.

Proporciona búsqueda con debouncing e historial opcional.
"""
from typing import Callable
import asyncio
import flet as ft
from loguru import logger

from src.frontend.layout_constants import LayoutConstants
from src.frontend.i18n.translation_manager import t


class SearchBar(ft.Container):
    """
    Barra de búsqueda con debouncing e historial.

    Args:
        placeholder: Texto placeholder
        on_search: Callback cuando se realiza la búsqueda
        debounce_ms: Milisegundos de delay antes de buscar (default: 500)
        max_history: Máximo de elementos en historial (0 = sin historial)
        autofocus: Si True, enfoca automáticamente

    Example:
        >>> def handle_search(query: str):
        ...     print(f"Searching for: {query}")
        >>> search = SearchBar(
        ...     placeholder="Buscar productos...",
        ...     on_search=handle_search,
        ...     max_history=5
        ... )
        >>> page.add(search)
    """

    def __init__(
        self,
        placeholder: str | None = None,
        on_search: Callable[[str], None] | None = None,
        debounce_ms: int = 500,
        max_history: int = 5,
        autofocus: bool = False,
    ):
        """Inicializa la barra de búsqueda."""
        super().__init__()
        self.placeholder = placeholder or t("common.search")
        self.on_search = on_search
        self.debounce_ms = debounce_ms
        self.max_history = max_history
        self.autofocus = autofocus
        self._search_field: ft.TextField | None = None
        self._clear_button: ft.IconButton | None = None
        self._history_button: ft.IconButton | None = None
        self._debounce_task: asyncio.Task | None = None
        self._search_history: list[str] = []
        logger.debug(f"SearchBar initialized with debounce={debounce_ms}ms")

    def build(self) -> ft.Control:
        """
        Construye el componente de búsqueda.

        Returns:
            Control de Flet con la barra de búsqueda
        """
        self._clear_button = ft.IconButton(
            icon=ft.Icons.CLEAR,
            icon_size=LayoutConstants.ICON_SIZE_SM,
            visible=False,
            on_click=self._handle_clear,
            tooltip=t("common.clear"),
        )

        self._history_button = ft.IconButton(
            icon=ft.Icons.HISTORY,
            icon_size=LayoutConstants.ICON_SIZE_SM,
            visible=self.max_history > 0,
            on_click=self._show_history,
            tooltip=t("common.search_history"),
        )

        self._search_field = ft.TextField(
            hint_text=self.placeholder,
            prefix_icon=ft.Icons.SEARCH,
            border=ft.InputBorder.OUTLINE,
            on_change=self._on_change,
            on_submit=self._on_submit,
            autofocus=self.autofocus,
            expand=True,
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    self._search_field,
                    self._clear_button,
                    self._history_button,
                ],
                spacing=LayoutConstants.SPACING_XS,
            ),
        )

    def _on_change(self, e: ft.ControlEvent) -> None:
        """
        Callback cuando cambia el texto.

        Args:
            e: Evento de Flet
        """
        query = self._search_field.value if self._search_field else ""

        # Mostrar/ocultar botón clear
        if self._clear_button:
            self._clear_button.visible = len(query) > 0
            if self.page:
                self.update()

        # Cancelar tarea anterior de debounce
        if self._debounce_task and not self._debounce_task.done():
            self._debounce_task.cancel()

        # Crear nueva tarea de debounce
        if query:
            self._debounce_task = asyncio.create_task(self._debounced_search(query))

    async def _debounced_search(self, query: str) -> None:
        """
        Ejecuta la búsqueda después del debounce.

        Args:
            query: Texto de búsqueda
        """
        try:
            await asyncio.sleep(self.debounce_ms / 1000.0)
            self._execute_search(query)
        except asyncio.CancelledError:
            logger.debug("Debounced search cancelled")

    def _on_submit(self, e: ft.ControlEvent) -> None:
        """
        Callback cuando se presiona Enter.

        Args:
            e: Evento de Flet
        """
        query = self._search_field.value if self._search_field else ""
        if query:
            # Cancelar debounce si existe
            if self._debounce_task and not self._debounce_task.done():
                self._debounce_task.cancel()
            self._execute_search(query)

    def _execute_search(self, query: str) -> None:
        """
        Ejecuta la búsqueda y actualiza el historial.

        Args:
            query: Texto de búsqueda
        """
        logger.info(f"Executing search: {query}")

        # Agregar al historial
        if self.max_history > 0:
            if query in self._search_history:
                self._search_history.remove(query)
            self._search_history.insert(0, query)
            self._search_history = self._search_history[:self.max_history]

        # Ejecutar callback
        if self.on_search:
            try:
                self.on_search(query)
            except Exception as ex:
                logger.error(f"Error in search callback: {ex}")

    def _handle_clear(self, e: ft.ControlEvent) -> None:
        """
        Maneja el click en clear.

        Args:
            e: Evento de Flet
        """
        logger.debug("Search cleared")
        if self._search_field:
            self._search_field.value = ""
        if self._clear_button:
            self._clear_button.visible = False

        # Ejecutar búsqueda vacía
        if self.on_search:
            try:
                self.on_search("")
            except Exception as ex:
                logger.error(f"Error in search callback: {ex}")

        if self.page:
            self.update()

    def _show_history(self, e: ft.ControlEvent) -> None:
        """
        Muestra el historial de búsquedas.

        Args:
            e: Evento de Flet
        """
        if not self._search_history:
            logger.debug("No search history available")
            return

        # Crear lista de opciones
        history_items = [
            ft.ListTile(
                leading=ft.Icon(ft.Icons.HISTORY),
                title=ft.Text(item),
                on_click=lambda e, q=item: self._select_history_item(q),
            )
            for item in self._search_history
        ]

        # Mostrar en diálogo
        dialog = ft.AlertDialog(
            title=ft.Text(t("common.search_history")),
            content=ft.Column(
                controls=history_items,
                tight=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            actions=[
                ft.TextButton(
                    text=t("common.clear_history"),
                    on_click=lambda e: self._clear_history(e, e.page),
                ),
                ft.TextButton(
                    text=t("common.close"),
                    on_click=lambda e: self._close_history_dialog(e, e.page),
                ),
            ],
        )

        if e.page:
            e.page.dialog = dialog
            dialog.open = True
            e.page.update()

    def _select_history_item(self, query: str) -> None:
        """
        Selecciona un item del historial.

        Args:
            query: Texto de búsqueda del historial
        """
        logger.debug(f"Selected history item: {query}")
        if self._search_field:
            self._search_field.value = query
        self._execute_search(query)
        if self.page:
            self.page.dialog.open = False
            self.page.update()

    def _clear_history(self, e: ft.ControlEvent, page: ft.Page) -> None:
        """
        Limpia el historial.

        Args:
            e: Evento de Flet
            page: Página de Flet
        """
        logger.info("Clearing search history")
        self._search_history = []
        if page:
            page.dialog.open = False
            page.update()

    def _close_history_dialog(self, e: ft.ControlEvent, page: ft.Page) -> None:
        """
        Cierra el diálogo de historial.

        Args:
            e: Evento de Flet
            page: Página de Flet
        """
        if page:
            page.dialog.open = False
            page.update()

    def get_query(self) -> str:
        """
        Obtiene el texto actual de búsqueda.

        Returns:
            Texto de búsqueda

        Example:
            >>> query = search.get_query()
        """
        if self._search_field:
            return self._search_field.value or ""
        return ""

    def set_query(self, query: str) -> None:
        """
        Establece el texto de búsqueda.

        Args:
            query: Texto de búsqueda

        Example:
            >>> search.set_query("producto")
            >>> search.update()
        """
        if self._search_field:
            self._search_field.value = query
            if self._clear_button:
                self._clear_button.visible = len(query) > 0
            if self.page:
                self.update()

    def clear(self) -> None:
        """
        Limpia el campo de búsqueda.

        Example:
            >>> search.clear()
        """
        if self._search_field:
            self._search_field.value = ""
        if self._clear_button:
            self._clear_button.visible = False
        if self.page:
            self.update()

    def get_history(self) -> list[str]:
        """
        Obtiene el historial de búsquedas.

        Returns:
            Lista de búsquedas anteriores

        Example:
            >>> history = search.get_history()
        """
        return self._search_history.copy()

    def clear_history(self) -> None:
        """
        Limpia el historial de búsquedas.

        Example:
            >>> search.clear_history()
        """
        self._search_history = []
        logger.debug("Search history cleared")
