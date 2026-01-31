"""
Componente base con manejo automático de observers y utilidades comunes.

Proporciona funcionalidad reutilizable para todos los componentes del frontend,
incluyendo gestión automática de observers y métodos de actualización seguros.
"""
from typing import Any, Callable
import flet as ft
from loguru import logger


class ObservableComponent(ft.Container):
    """
    Componente base con manejo automático de observers.

    Extiende ft.Container añadiendo:
    - Gestión automática de suscripciones a observers
    - Limpieza automática en will_unmount()
    - Método safe_update() para actualizaciones seguras
    - Método run_async() para ejecutar tareas asíncronas

    Example:
        >>> class MyView(ObservableComponent):
        ...     def __init__(self):
        ...         super().__init__()
        ...         # Suscribirse a cambios de tema (se limpia automáticamente)
        ...         self.subscribe(app_state.theme, self._on_theme_changed)
        ...         self.subscribe(app_state.i18n, self._on_language_changed)
        ...
        ...     def _on_theme_changed(self):
        ...         self.safe_update()  # No necesita verificar self.page
    """

    def __init__(self, **kwargs):
        """Inicializa el componente base."""
        super().__init__(**kwargs)
        self._observers: list[tuple[Any, Callable[[], None]]] = []
        self._is_mounted: bool = False

    def subscribe(self, state_obj: Any, callback: Callable[[], None]) -> None:
        """
        Registra un observer que se limpia automáticamente en will_unmount.

        Args:
            state_obj: Objeto de estado con métodos add_observer/remove_observer
            callback: Función a llamar cuando cambie el estado

        Example:
            >>> self.subscribe(app_state.theme, self._on_theme_changed)
            >>> self.subscribe(app_state.i18n, self._on_language_changed)
        """
        if hasattr(state_obj, "add_observer"):
            state_obj.add_observer(callback)
            self._observers.append((state_obj, callback))
            logger.debug(
                f"{self.__class__.__name__}: Subscribed to {state_obj.__class__.__name__}"
            )
        else:
            logger.warning(
                f"{self.__class__.__name__}: Cannot subscribe - "
                f"{state_obj.__class__.__name__} has no add_observer method"
            )

    def unsubscribe(self, state_obj: Any, callback: Callable[[], None]) -> None:
        """
        Remueve un observer específico.

        Args:
            state_obj: Objeto de estado
            callback: Función a remover

        Example:
            >>> self.unsubscribe(app_state.theme, self._on_theme_changed)
        """
        if hasattr(state_obj, "remove_observer"):
            state_obj.remove_observer(callback)
            self._observers = [
                (s, c) for s, c in self._observers if not (s is state_obj and c is callback)
            ]
            logger.debug(
                f"{self.__class__.__name__}: Unsubscribed from {state_obj.__class__.__name__}"
            )

    def safe_update(self) -> None:
        """
        Actualiza el componente solo si está montado en una página.

        Evita errores cuando se intenta actualizar un componente
        que aún no está en el árbol de UI o ya fue desmontado.

        Example:
            >>> def _on_data_loaded(self):
            ...     self._data = new_data
            ...     self.safe_update()  # Seguro incluso si no está montado
        """
        if self._is_mounted and self.page:
            self.update()

    def run_async(self, coro) -> None:
        """
        Ejecuta una corutina de forma segura usando page.run_task.

        Args:
            coro: Corutina a ejecutar

        Example:
            >>> def did_mount(self):
            ...     self.run_async(self.load_data())
        """
        if self.page:
            self.page.run_task(coro)
        else:
            logger.warning(
                f"{self.__class__.__name__}: Cannot run async task - not mounted"
            )

    def did_mount(self) -> None:
        """
        Lifecycle: Se ejecuta cuando el componente se monta.

        Override este método para inicialización post-montaje.
        Siempre llama a super().did_mount() primero.
        """
        self._is_mounted = True
        logger.debug(f"{self.__class__.__name__}: Mounted")

    def will_unmount(self) -> None:
        """
        Lifecycle: Se ejecuta cuando el componente se desmonta.

        Limpia automáticamente todos los observers registrados.
        Si override, siempre llama a super().will_unmount() al final.
        """
        self._is_mounted = False
        
        # Limpiar todos los observers registrados
        for state_obj, callback in self._observers:
            if hasattr(state_obj, "remove_observer"):
                try:
                    state_obj.remove_observer(callback)
                except Exception as e:
                    logger.warning(
                        f"{self.__class__.__name__}: Error removing observer: {e}"
                    )
        
        observer_count = len(self._observers)
        self._observers.clear()
        
        if observer_count > 0:
            logger.debug(
                f"{self.__class__.__name__}: Unmounted, cleaned up {observer_count} observers"
            )
        else:
            logger.debug(f"{self.__class__.__name__}: Unmounted")

    @property
    def is_mounted(self) -> bool:
        """Indica si el componente está actualmente montado."""
        return self._is_mounted

