"""
Global application state management using Singleton and Observer patterns.

This module provides centralized state management for the entire application,
including navigation, internationalization, and theme management.
"""
from typing import Callable
from loguru import logger
import flet as ft


class NavigationState:
    """
    Estado de navegación de la aplicación.

    Mantiene información sobre la sección actual, ruta, y breadcrumb.
    Implementa patrón Observer para notificar cambios.
    """

    def __init__(self):
        """Inicializa el estado de navegación."""
        self._observers: list[Callable[[], None]] = []
        self.current_section_index: int = 0
        self.current_section_title: str = ""
        self.current_route: str = "/"
        self.breadcrumb_path: list[dict[str, str | None]] = []
        self.navigation_rail_expanded: bool = True

    def add_observer(self, callback: Callable[[], None]) -> None:
        """
        Agrega un observer que será notificado de cambios.

        Args:
            callback: Función a llamar cuando hay cambios

        Example:
            >>> nav_state.add_observer(my_update_function)
        """
        if callback not in self._observers:
            self._observers.append(callback)
            logger.debug(f"Observer added to NavigationState. Total: {len(self._observers)}")

    def remove_observer(self, callback: Callable[[], None]) -> None:
        """
        Remueve un observer.

        Args:
            callback: Función a remover
        """
        if callback in self._observers:
            self._observers.remove(callback)
            logger.debug(f"Observer removed from NavigationState. Total: {len(self._observers)}")

    def notify_observers(self) -> None:
        """Notifica a todos los observers de cambios en el estado."""
        logger.debug(f"Notifying {len(self._observers)} observers of navigation change")
        for callback in self._observers:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error notifying observer: {e}")

    def set_section(self, index: int, title: str, route: str) -> None:
        """
        Actualiza la sección actual.

        Args:
            index: Índice de la sección
            title: Título de la sección (i18n key)
            route: Ruta de la sección

        Example:
            >>> nav_state.set_section(1, "companies.title", "/companies")
        """
        logger.info(f"Navigating to section: {index} - {title} ({route})")
        self.current_section_index = index
        self.current_section_title = title
        self.current_route = route
        self.notify_observers()

    def set_breadcrumb(self, path: list[dict[str, str | None]]) -> None:
        """
        Actualiza el breadcrumb path.

        Args:
            path: Lista de diccionarios con 'label' y 'route'

        Example:
            >>> nav_state.set_breadcrumb([
            ...     {"label": "Inicio", "route": "/"},
            ...     {"label": "Empresas", "route": "/companies"},
            ...     {"label": "Editar", "route": None}
            ... ])
        """
        self.breadcrumb_path = path
        logger.debug(f"Breadcrumb updated: {path}")
        self.notify_observers()

    def toggle_rail_expanded(self) -> None:
        """Alterna el estado expandido/colapsado del navigation rail."""
        self.navigation_rail_expanded = not self.navigation_rail_expanded
        logger.debug(f"Navigation rail expanded: {self.navigation_rail_expanded}")
        self.notify_observers()

    def set_rail_expanded(self, expanded: bool) -> None:
        """
        Establece el estado expandido/colapsado del navigation rail.

        Args:
            expanded: True para expandido, False para colapsado
        """
        if self.navigation_rail_expanded != expanded:
            self.navigation_rail_expanded = expanded
            logger.debug(f"Navigation rail expanded set to: {expanded}")
            self.notify_observers()


class I18nState:
    """
    Estado de internacionalización.

    Mantiene el idioma actual y notifica a observers cuando cambia.
    """

    def __init__(self):
        """Inicializa el estado de i18n."""
        self._observers: list[Callable[[], None]] = []
        self.current_language: str = "es"  # Idioma por defecto
        self.available_languages: list[str] = ["es", "en", "fr"]

    def add_observer(self, callback: Callable[[], None]) -> None:
        """
        Agrega un observer que será notificado de cambios.

        Args:
            callback: Función a llamar cuando cambia el idioma
        """
        if callback not in self._observers:
            self._observers.append(callback)
            logger.debug(f"Observer added to I18nState. Total: {len(self._observers)}")

    def remove_observer(self, callback: Callable[[], None]) -> None:
        """
        Remueve un observer.

        Args:
            callback: Función a remover
        """
        if callback in self._observers:
            self._observers.remove(callback)
            logger.debug(f"Observer removed from I18nState. Total: {len(self._observers)}")

    def notify_observers(self) -> None:
        """Notifica a todos los observers de cambios en el idioma."""
        logger.debug(f"Notifying {len(self._observers)} observers of language change")
        for callback in self._observers:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error notifying observer: {e}")

    def set_language(self, lang: str) -> None:
        """
        Cambia el idioma actual.

        Args:
            lang: Código del idioma ("es", "en", "fr")

        Raises:
            ValueError: Si el idioma no está disponible

        Example:
            >>> i18n_state.set_language("en")
        """
        if lang not in self.available_languages:
            raise ValueError(f"Language '{lang}' not available. Available: {self.available_languages}")

        if self.current_language != lang:
            logger.info(f"Changing language from {self.current_language} to {lang}")
            self.current_language = lang
            self.notify_observers()


class ThemeState:
    """
    Estado del tema de la aplicación.

    Mantiene el modo de tema (claro/oscuro/sistema) y notifica cambios.
    """

    def __init__(self):
        """Inicializa el estado del tema."""
        self._observers: list[Callable[[], None]] = []
        self.theme_mode: str = "system"  # "light", "dark", "system"
        self.is_dark_mode: bool = False  # Se actualiza basado en theme_mode y sistema

    def add_observer(self, callback: Callable[[], None]) -> None:
        """
        Agrega un observer que será notificado de cambios.

        Args:
            callback: Función a llamar cuando cambia el tema
        """
        if callback not in self._observers:
            self._observers.append(callback)
            logger.debug(f"Observer added to ThemeState. Total: {len(self._observers)}")

    def remove_observer(self, callback: Callable[[], None]) -> None:
        """
        Remueve un observer.

        Args:
            callback: Función a remover
        """
        if callback in self._observers:
            self._observers.remove(callback)
            logger.debug(f"Observer removed from ThemeState. Total: {len(self._observers)}")

    def notify_observers(self) -> None:
        """Notifica a todos los observers de cambios en el tema."""
        logger.debug(f"Notifying {len(self._observers)} observers of theme change")
        for callback in self._observers:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error notifying observer: {e}")

    def set_theme_mode(self, mode: str) -> None:
        """
        Establece el modo de tema.

        Args:
            mode: Modo de tema ("light", "dark", "system")

        Raises:
            ValueError: Si el modo no es válido

        Example:
            >>> theme_state.set_theme_mode("dark")
        """
        valid_modes = ["light", "dark", "system"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid theme mode '{mode}'. Valid: {valid_modes}")

        if self.theme_mode != mode:
            logger.info(f"Changing theme mode from {self.theme_mode} to {mode}")
            self.theme_mode = mode
            self._update_is_dark_mode()
            self.notify_observers()

    def _update_is_dark_mode(self) -> None:
        """Actualiza is_dark_mode basado en theme_mode y preferencia del sistema."""
        if self.theme_mode == "dark":
            self.is_dark_mode = True
        elif self.theme_mode == "light":
            self.is_dark_mode = False
        else:  # system
            # TODO: Detectar preferencia del sistema
            # Por ahora, usar claro por defecto
            self.is_dark_mode = False
        logger.debug(f"Dark mode: {self.is_dark_mode}")

    def get_flet_theme_mode(self) -> ft.ThemeMode:
        """
        Obtiene el ThemeMode de Flet correspondiente.

        Returns:
            ThemeMode de Flet

        Example:
            >>> theme_state.get_flet_theme_mode()
            ft.ThemeMode.LIGHT
        """
        if self.theme_mode == "dark":
            return ft.ThemeMode.DARK
        elif self.theme_mode == "light":
            return ft.ThemeMode.LIGHT
        else:
            return ft.ThemeMode.SYSTEM


class AppState:
    """
    Estado global de la aplicación (Singleton).

    Provee acceso centralizado a todos los estados de la aplicación.
    """

    _instance: "AppState | None" = None

    def __new__(cls) -> "AppState":
        """
        Crea o retorna la instancia única del AppState.

        Returns:
            Instancia única de AppState
        """
        if cls._instance is None:
            logger.info("Creating AppState singleton instance")
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Inicializa los estados de la aplicación."""
        logger.info("Initializing AppState")
        self.navigation = NavigationState()
        self.i18n = I18nState()
        self.theme = ThemeState()
        logger.success("AppState initialized successfully")

    def reset(self) -> None:
        """Resetea el estado de la aplicación (útil para testing)."""
        logger.warning("Resetting AppState")
        self._initialize()


# Instancia global única del estado
app_state = AppState()
