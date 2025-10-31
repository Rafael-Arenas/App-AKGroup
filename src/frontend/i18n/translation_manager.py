"""
Translation manager for internationalization.

Provides centralized management of translations with Observer pattern support.
"""
import json
from pathlib import Path
from typing import Callable
from loguru import logger


class TranslationManager:
    """
    Gestor de traducciones con patrón Observer.

    Carga traducciones desde archivos JSON y permite cambiar el idioma
    dinámicamente, notificando a los observers de cambios.
    """

    _instance: "TranslationManager | None" = None

    def __new__(cls) -> "TranslationManager":
        """
        Crea o retorna la instancia única del TranslationManager.

        Returns:
            Instancia única de TranslationManager
        """
        if cls._instance is None:
            logger.info("Creating TranslationManager singleton instance")
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Inicializa el gestor de traducciones."""
        self._observers: list[Callable[[], None]] = []
        self._translations: dict[str, dict] = {}
        self._current_language: str = "es"
        self._available_languages: list[str] = ["es", "en", "fr"]
        self._locales_dir: Path = Path(__file__).parent / "locales"
        self._load_translations()

    def _load_translations(self) -> None:
        """Carga todos los archivos de traducción disponibles."""
        logger.info("Loading translations...")

        for lang in self._available_languages:
            locale_file = self._locales_dir / f"{lang}.json"

            if locale_file.exists():
                try:
                    with open(locale_file, "r", encoding="utf-8") as f:
                        self._translations[lang] = json.load(f)
                    logger.success(f"Loaded translations for '{lang}'")
                except Exception as e:
                    logger.error(f"Error loading translations for '{lang}': {e}")
                    self._translations[lang] = {}
            else:
                logger.warning(f"Translation file not found: {locale_file}")
                self._translations[lang] = {}

        logger.info(f"Translations loaded for {len(self._translations)} languages")

    def add_observer(self, callback: Callable[[], None]) -> None:
        """
        Agrega un observer que será notificado de cambios de idioma.

        Args:
            callback: Función a llamar cuando cambia el idioma
        """
        if callback not in self._observers:
            self._observers.append(callback)
            logger.debug(f"Observer added to TranslationManager. Total: {len(self._observers)}")

    def remove_observer(self, callback: Callable[[], None]) -> None:
        """
        Remueve un observer.

        Args:
            callback: Función a remover
        """
        if callback in self._observers:
            self._observers.remove(callback)
            logger.debug(f"Observer removed from TranslationManager. Total: {len(self._observers)}")

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
            >>> tm = TranslationManager()
            >>> tm.set_language("en")
        """
        if lang not in self._available_languages:
            raise ValueError(
                f"Language '{lang}' not available. Available: {self._available_languages}"
            )

        if self._current_language != lang:
            logger.info(f"Changing language from {self._current_language} to {lang}")
            self._current_language = lang
            self.notify_observers()

    def get_current_language(self) -> str:
        """
        Obtiene el idioma actual.

        Returns:
            Código del idioma actual

        Example:
            >>> tm = TranslationManager()
            >>> tm.get_current_language()
            'es'
        """
        return self._current_language

    def get_available_languages(self) -> list[str]:
        """
        Obtiene los idiomas disponibles.

        Returns:
            Lista de códigos de idiomas disponibles

        Example:
            >>> tm = TranslationManager()
            >>> tm.get_available_languages()
            ['es', 'en', 'fr']
        """
        return self._available_languages

    def t(self, key: str, params: dict[str, str] | None = None, lang: str | None = None) -> str:
        """
        Obtiene una traducción por clave.

        Args:
            key: Clave de traducción (soporta notación punto: "app.title")
            params: Diccionario de parámetros para reemplazar en la traducción
            lang: Idioma específico (si None, usa el idioma actual)

        Returns:
            Traducción o la clave si no se encuentra

        Example:
            >>> tm = TranslationManager()
            >>> tm.t("app.title")
            'AK Group - Sistema de Gestión'
            >>> tm.t("common.error", {"error": "404"})
            'Error: 404'
        """
        language = lang or self._current_language

        # Obtener traducciones para el idioma
        translations = self._translations.get(language, {})

        # Navegar por la estructura usando la notación punto
        keys = key.split(".")
        value = translations

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    logger.warning(f"Translation key not found: '{key}' (lang: {language})")
                    return key
            else:
                logger.warning(f"Invalid translation path: '{key}' (lang: {language})")
                return key

        # Si el valor final no es string, retornar la clave
        if not isinstance(value, str):
            logger.warning(f"Translation value is not string: '{key}' (lang: {language})")
            return key

        # Reemplazar parámetros si se proporcionan
        if params:
            for param_key, param_value in params.items():
                placeholder = f"{{{param_key}}}"
                value = value.replace(placeholder, str(param_value))

        return value

    def reload_translations(self) -> None:
        """
        Recarga todas las traducciones desde los archivos.

        Útil durante desarrollo o si se actualizan archivos de traducción.
        """
        logger.info("Reloading translations...")
        self._load_translations()
        self.notify_observers()


# Instancia global única
translation_manager = TranslationManager()


# Función de conveniencia para acceso rápido
def t(key: str, params: dict[str, str] | None = None, lang: str | None = None) -> str:
    """
    Función de conveniencia para obtener traducciones.

    Args:
        key: Clave de traducción
        params: Parámetros opcionales
        lang: Idioma opcional

    Returns:
        Traducción

    Example:
        >>> from src.frontend.i18n.translation_manager import t
        >>> t("app.title")
        'AK Group - Sistema de Gestión'
    """
    return translation_manager.t(key, params, lang)
