"""
Color constants for the application.

Centralizes all color definitions for easy theming and maintenance.
"""


class ColorConstants:
    """Constantes de colores para la aplicación."""

    # Primary colors
    PRIMARY = "#1976D2"
    PRIMARY_DARK = "#004BA0"
    PRIMARY_LIGHT = "#63A4FF"
    PRIMARY_CONTAINER = "#E3F2FD"

    # Secondary colors
    SECONDARY = "#FF6F00"
    SECONDARY_DARK = "#C43E00"
    SECONDARY_LIGHT = "#FFA040"
    SECONDARY_CONTAINER = "#FFE0B2"

    # Neutral colors - Light theme
    BACKGROUND_LIGHT = "#FAFAFA"
    SURFACE_LIGHT = "#FFFFFF"
    SURFACE_VARIANT_LIGHT = "#F5F5F5"
    ON_SURFACE_LIGHT = "#212121"
    ON_SURFACE_VARIANT_LIGHT = "#757575"

    # Neutral colors - Dark theme
    BACKGROUND_DARK = "#121212"
    SURFACE_DARK = "#1E1E1E"
    SURFACE_VARIANT_DARK = "#2C2C2C"
    ON_SURFACE_DARK = "#FFFFFF"
    ON_SURFACE_VARIANT_DARK = "#BDBDBD"

    # Status colors
    SUCCESS = "#4CAF50"
    SUCCESS_CONTAINER = "#C8E6C9"
    ERROR = "#F44336"
    ERROR_CONTAINER = "#FFCDD2"
    WARNING = "#FF9800"
    WARNING_CONTAINER = "#FFE0B2"
    INFO = "#2196F3"
    INFO_CONTAINER = "#BBDEFB"

    # Divider colors
    DIVIDER_LIGHT = "#E0E0E0"
    DIVIDER_DARK = "#424242"

    # Border colors
    BORDER_LIGHT = "#BDBDBD"
    BORDER_DARK = "#616161"

    # Overlay colors
    OVERLAY_LIGHT = "rgba(0, 0, 0, 0.05)"
    OVERLAY_DARK = "rgba(255, 255, 255, 0.05)"
    SCRIM = "rgba(0, 0, 0, 0.5)"

    # Disabled colors
    DISABLED_LIGHT = "#BDBDBD"
    DISABLED_DARK = "#757575"

    # Navigation Rail colors
    RAIL_BACKGROUND_LIGHT = "#FFFFFF"
    RAIL_BACKGROUND_DARK = "#1E1E1E"
    RAIL_SELECTED_LIGHT = "#E3F2FD"
    RAIL_SELECTED_DARK = "#1565C0"

    # AppBar colors
    APPBAR_BACKGROUND_LIGHT = "#1976D2"
    APPBAR_BACKGROUND_DARK = "#0D47A1"
    APPBAR_ON_BACKGROUND = "#FFFFFF"

    # Card colors
    CARD_BACKGROUND_LIGHT = "#FFFFFF"
    CARD_BACKGROUND_DARK = "#1E1E1E"

    # Text colors
    TEXT_PRIMARY_LIGHT = "#212121"
    TEXT_SECONDARY_LIGHT = "#757575"
    TEXT_DISABLED_LIGHT = "#BDBDBD"
    TEXT_PRIMARY_DARK = "#FFFFFF"
    TEXT_SECONDARY_DARK = "#BDBDBD"
    TEXT_DISABLED_DARK = "#757575"

    # Badge colors
    BADGE_BACKGROUND = "#F44336"
    BADGE_TEXT = "#FFFFFF"

    # Data table colors
    TABLE_HEADER_LIGHT = "#F5F5F5"
    TABLE_HEADER_DARK = "#2C2C2C"
    TABLE_ROW_HOVER_LIGHT = "#F5F5F5"
    TABLE_ROW_HOVER_DARK = "#2C2C2C"
    TABLE_ROW_SELECTED_LIGHT = "#E3F2FD"
    TABLE_ROW_SELECTED_DARK = "#1565C0"

    @classmethod
    def get_color_for_theme(cls, color_name: str, is_dark: bool) -> str:
        """
        Obtiene el color apropiado según el tema.

        Args:
            color_name: Nombre base del color (sin sufijo _LIGHT o _DARK)
            is_dark: True si es tema oscuro, False si es tema claro

        Returns:
            Código hexadecimal del color

        Example:
            >>> ColorConstants.get_color_for_theme("BACKGROUND", False)
            "#FAFAFA"
            >>> ColorConstants.get_color_for_theme("BACKGROUND", True)
            "#121212"
        """
        suffix = "_DARK" if is_dark else "_LIGHT"
        full_name = f"{color_name}{suffix}"

        # Intentar obtener el color con sufijo
        if hasattr(cls, full_name):
            return getattr(cls, full_name)

        # Si no existe con sufijo, devolver sin sufijo
        if hasattr(cls, color_name):
            return getattr(cls, color_name)

        # Fallback
        return cls.PRIMARY
