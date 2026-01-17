import pendulum
from typing import Sequence

class TimezoneService:
    """
    Servicio para gestión de zonas horarias y formatos de fecha.
    Permite listar zonas disponibles y convertir/formatear fechas para usuarios.
    """

    def get_available_timezones(self) -> Sequence[str]:
        """Devuelve una lista de todas las zonas horarias soportadas."""
        return pendulum.timezones

    def convert_to_user_timezone(
        self, 
        dt_utc: pendulum.DateTime, 
        user_timezone: str
    ) -> pendulum.DateTime:
        """
        Convierte una fecha UTC a la zona horaria del usuario.
        
        Args:
            dt_utc: Fecha en UTC (debe ser aware).
            user_timezone: String identificador de zona (ej: "America/Santiago").
        """
        # Aseguramos que sea una instancia de Pendulum y tenga zona
        if not isinstance(dt_utc, pendulum.DateTime):
            dt_utc = pendulum.instance(dt_utc)
            
        return dt_utc.in_timezone(user_timezone)

    def format_date(
        self,
        dt_utc: pendulum.DateTime,
        user_timezone: str,
        fmt: str = "DD/MM/YYYY HH:mm",
        locale: str = "es"
    ) -> str:
        """
        Convierte a zona horaria local y formatea a string.
        
        Args:
            dt_utc: Fecha original en UTC.
            user_timezone: Zona destino.
            fmt: Formato de salida (sintaxis Pendulum).
            locale: Idioma para nombres de meses/días (default: español).
        """
        local_dt = self.convert_to_user_timezone(dt_utc, user_timezone)
        return local_dt.format(fmt, locale=locale)
