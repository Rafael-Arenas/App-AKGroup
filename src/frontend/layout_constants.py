"""
Layout constants for the application.

Centralizes all spacing, sizing, and animation constants.
"""
import flet as ft


class LayoutConstants:
    """Constantes de layout para la aplicación."""

    # Navigation Rail dimensions
    RAIL_WIDTH_COLLAPSED = 72
    RAIL_WIDTH_EXPANDED = 256
    RAIL_TRANSITION_DURATION = 300  # milliseconds

    # Spacing
    SPACING_NONE = 0
    SPACING_XXS = 2
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 16
    SPACING_LG = 24
    SPACING_XL = 32
    SPACING_XXL = 48

    # Padding
    PADDING_NONE = 0
    PADDING_XS = 4
    PADDING_SM = 8
    PADDING_MD = 16
    PADDING_LG = 24
    PADDING_XL = 32

    # Border radius
    RADIUS_NONE = 0
    RADIUS_XS = 4
    RADIUS_SM = 8
    RADIUS_MD = 12
    RADIUS_LG = 16
    RADIUS_XL = 24
    RADIUS_FULL = 9999

    # Elevations
    ELEVATION_NONE = 0
    ELEVATION_LOW = 2
    ELEVATION_MEDIUM = 4
    ELEVATION_HIGH = 8
    ELEVATION_HIGHEST = 16

    # AppBar
    APPBAR_HEIGHT = 64
    APPBAR_PADDING = 16

    # Icon sizes
    ICON_SIZE_SM = 16
    ICON_SIZE_MD = 24
    ICON_SIZE_LG = 32
    ICON_SIZE_XL = 48

    # Font sizes
    FONT_SIZE_XS = 10
    FONT_SIZE_SM = 12
    FONT_SIZE_MD = 14
    FONT_SIZE_LG = 16
    FONT_SIZE_XL = 20
    FONT_SIZE_XXL = 24
    FONT_SIZE_DISPLAY_SM = 32
    FONT_SIZE_DISPLAY_MD = 40
    FONT_SIZE_DISPLAY_LG = 48

    # Font weights
    FONT_WEIGHT_LIGHT = ft.FontWeight.W_300
    FONT_WEIGHT_NORMAL = ft.FontWeight.W_400
    FONT_WEIGHT_MEDIUM = ft.FontWeight.W_500
    FONT_WEIGHT_SEMIBOLD = ft.FontWeight.W_600
    FONT_WEIGHT_BOLD = ft.FontWeight.W_700

    # Component heights
    BUTTON_HEIGHT = 40
    TEXTFIELD_HEIGHT = 56
    DROPDOWN_HEIGHT = 56
    CHIP_HEIGHT = 32
    APPBAR_HEIGHT = 64

    # Component widths
    BUTTON_WIDTH_SM = 80
    BUTTON_WIDTH_MD = 120
    BUTTON_WIDTH_LG = 160
    DIALOG_WIDTH_SM = 400
    DIALOG_WIDTH_MD = 600
    DIALOG_WIDTH_LG = 800

    # Breakpoints (for responsive design)
    BREAKPOINT_XS = 600  # Extra small devices
    BREAKPOINT_SM = 960  # Small devices
    BREAKPOINT_MD = 1280  # Medium devices
    BREAKPOINT_LG = 1920  # Large devices
    BREAKPOINT_XL = 2560  # Extra large devices

    # Animation durations (milliseconds)
    ANIMATION_DURATION_FAST = 150
    ANIMATION_DURATION_NORMAL = 300
    ANIMATION_DURATION_SLOW = 500

    # Animation curves
    ANIMATION_CURVE_DEFAULT = ft.AnimationCurve.EASE_IN_OUT
    ANIMATION_CURVE_EASE_IN = ft.AnimationCurve.EASE_IN
    ANIMATION_CURVE_EASE_OUT = ft.AnimationCurve.EASE_OUT
    ANIMATION_CURVE_LINEAR = ft.AnimationCurve.LINEAR

    # Data table
    TABLE_ROW_HEIGHT = 52
    TABLE_HEADER_HEIGHT = 56
    TABLE_PADDING = 16

    # Card dimensions
    CARD_MIN_HEIGHT = 100
    CARD_PADDING = 16

    # Badge dimensions
    BADGE_SIZE = 20
    BADGE_SIZE_SM = 16
    BADGE_OFFSET = 4

    # Divider thickness
    DIVIDER_THICKNESS = 1

    # Border widths
    BORDER_WIDTH_THIN = 1
    BORDER_WIDTH_MEDIUM = 2
    BORDER_WIDTH_THICK = 4

    # Z-index layers
    Z_INDEX_DROPDOWN = 1000
    Z_INDEX_STICKY = 1020
    Z_INDEX_FIXED = 1030
    Z_INDEX_MODAL_BACKDROP = 1040
    Z_INDEX_MODAL = 1050
    Z_INDEX_POPOVER = 1060
    Z_INDEX_TOOLTIP = 1070

    # Form field spacing
    FORM_FIELD_SPACING = 16
    FORM_SECTION_SPACING = 32

    # List item heights
    LIST_ITEM_HEIGHT_SM = 48
    LIST_ITEM_HEIGHT_MD = 56
    LIST_ITEM_HEIGHT_LG = 72

    @classmethod
    def get_animation(
        cls,
        duration: int | None = None,
        curve: ft.AnimationCurve | None = None
    ) -> ft.Animation:
        """
        Crea una configuración de animación.

        Args:
            duration: Duración en milisegundos (default: ANIMATION_DURATION_NORMAL)
            curve: Curva de animación (default: ANIMATION_CURVE_DEFAULT)

        Returns:
            Objeto Animation de Flet

        Example:
            >>> LayoutConstants.get_animation(300, ft.AnimationCurve.EASE_IN_OUT)
            Animation(300, AnimationCurve.EASE_IN_OUT)
        """
        duration = duration or cls.ANIMATION_DURATION_NORMAL
        curve = curve or cls.ANIMATION_CURVE_DEFAULT
        return ft.Animation(duration, curve)

    @classmethod
    def get_responsive_width(cls, page_width: float) -> str:
        """
        Determina el tamaño de dispositivo basado en el ancho de página.

        Args:
            page_width: Ancho de la página en píxeles

        Returns:
            Tamaño del dispositivo: "xs", "sm", "md", "lg", "xl"

        Example:
            >>> LayoutConstants.get_responsive_width(800)
            "sm"
        """
        if page_width < cls.BREAKPOINT_XS:
            return "xs"
        elif page_width < cls.BREAKPOINT_SM:
            return "sm"
        elif page_width < cls.BREAKPOINT_MD:
            return "md"
        elif page_width < cls.BREAKPOINT_LG:
            return "lg"
        else:
            return "xl"
