"""
Vista de configuración de la aplicación.

Permite al usuario personalizar preferencias de interfaz como idioma y tema.
"""
import flet as ft
from loguru import logger

from src.frontend.app_state import app_state
from src.frontend.layout_constants import LayoutConstants
from src.frontend.components.common import BaseCard
from src.frontend.i18n.translation_manager import t


class SettingsView(ft.Container):
    """
    Vista de configuración para preferencias de usuario.
    """
    
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = LayoutConstants.PADDING_LG
        
        # El contenido se building en build() o similar, 
        # pero en Flet Containers usamos self.content
        self.column = ft.Column(
            spacing=LayoutConstants.SPACING_LG,
            scroll=ft.ScrollMode.AUTO,
        )
        self.content = self.column
        self._update_content()
        
        logger.info("SettingsView initialized")

    def did_mount(self):
        """Lifecycle: Se ejecuta cuando el componente se monta."""
        logger.debug("SettingsView mounted, adding observers")
        app_state.i18n.add_observer(self._update_ui)
        app_state.theme.add_observer(self._update_ui)

    def will_unmount(self):
        """Lifecycle: Se ejecuta cuando el componente se desmonta."""
        logger.debug("SettingsView unmounting, removing observers")
        app_state.i18n.remove_observer(self._update_ui)
        app_state.theme.remove_observer(self._update_ui)

    async def _on_theme_change(self, e: ft.ControlEvent) -> None:
        """Maneja el cambio de tema."""
        # Manejar diferentes versiones de Flet para SegmentedButton.on_change
        selection = e.data if isinstance(e.data, (list, set)) else getattr(e, "selection", [])
        if not selection and hasattr(e.control, "selected"):
            selection = e.control.selected
            
        if selection:
            theme_mode = list(selection)[0]
            logger.info(f"Changing theme to: {theme_mode}")
            await app_state.theme.set_theme_mode(theme_mode)

    async def _on_language_change(self, e: ft.ControlEvent) -> None:
        """Maneja el cambio de idioma."""
        logger.info(f"Language change event triggered. Control value: {e.control.value}, Data: {e.data}")
        lang = e.control.value
        if not lang:
            logger.warning("Language value is empty!")
            return
            
        logger.info(f"Changing language to: {lang}")
        try:
            await app_state.i18n.set_language(lang)
            logger.info("Language set in app_state")
        except Exception as ex:
            logger.error(f"Error setting language: {ex}")

    def _update_ui(self):
        """Callback de los observers para actualizar la UI."""
        logger.info("Updating Settings UI")
        self._update_content()
        if self.page:
            self.update()

    def _update_content(self):
        """Construye/actualiza los controles de la vista."""
        current_lang = app_state.i18n.current_language
        logger.debug(f"Building content with language: {current_lang}")
        
        self.column.controls = [
            # Título de la vista
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SETTINGS, size=LayoutConstants.ICON_SIZE_LG),
                    ft.Text(
                        t("settings.title"),
                        size=LayoutConstants.FONT_SIZE_DISPLAY_MD,
                        weight=LayoutConstants.FONT_WEIGHT_BOLD,
                    ),
                ],
                spacing=LayoutConstants.SPACING_MD,
            ),
            ft.Text(
                t("settings.description"),
                size=LayoutConstants.FONT_SIZE_MD,
                color=ft.Colors.ON_SURFACE_VARIANT,
            ),
            ft.Divider(),
            
            # Sección de Apariencia
            BaseCard(
                title=t("settings.appearance"),
                icon=ft.Icons.PALETTE,
                content=ft.Column(
                    controls=[
                        ft.Text(t("settings.theme"), weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD),
                        ft.SegmentedButton(
                            selected=[app_state.theme.theme_mode],
                            allow_multiple_selection=False,
                            on_change=self._on_theme_change,
                            segments=[
                                ft.Segment(
                                    value="light",
                                    label=ft.Text(t("settings.theme_light")),
                                    icon=ft.Icon(ft.Icons.LIGHT_MODE),
                                ),
                                ft.Segment(
                                    value="dark",
                                    label=ft.Text(t("settings.theme_dark")),
                                    icon=ft.Icon(ft.Icons.DARK_MODE),
                                ),
                                ft.Segment(
                                    value="system",
                                    label=ft.Text(t("settings.theme_system")),
                                    icon=ft.Icon(ft.Icons.BRIGHTNESS_AUTO),
                                ),
                            ],
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_MD,
                ),
            ),
            
            # Sección de Idioma
            BaseCard(
                title=t("settings.language"),
                icon=ft.Icons.LANGUAGE,
                content=ft.Column(
                    controls=[
                        ft.Text(t("settings.language"), weight=LayoutConstants.FONT_WEIGHT_SEMIBOLD),
                        ft.RadioGroup(
                            content=ft.Row(
                                controls=[
                                    ft.Radio(value="es", label=t("language.es")),
                                    ft.Radio(value="en", label=t("language.en")),
                                    ft.Radio(value="fr", label=t("language.fr")),
                                ],
                                spacing=LayoutConstants.SPACING_LG,
                            ),
                            value=current_lang,
                            on_change=self._on_language_change,
                        ),
                    ],
                    spacing=LayoutConstants.SPACING_MD,
                ),
            ),
        ]
