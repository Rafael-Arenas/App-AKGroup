"""
Servicio centralizado para gestión de zonas horarias y formatos de fecha.

Este módulo proporciona funcionalidades para:
- Listar zonas horarias disponibles
- Convertir fechas entre zonas horarias
- Formatear fechas para visualización
- Comparar horas entre diferentes países
- Determinar horarios de negocio
"""
import pendulum
from typing import Sequence
from pendulum import Date

from src.shared.constants import (
    COMMON_TIMEZONES,
    DEFAULT_TIMEZONE,
    PENDULUM_DATETIME_FORMAT,
    BUSINESS_HOUR_START,
    BUSINESS_HOUR_END,
    BUSINESS_DAYS,
)
from src.shared.providers.time_provider import ITimeProvider, TimeProvider


class TimezoneService:
    """
    Servicio centralizado para gestión de zonas horarias y formatos de fecha.
    
    Permite:
    - Listar zonas horarias disponibles
    - Convertir fechas entre zonas horarias
    - Formatear fechas para visualización
    - Comparar horas entre diferentes países
    - Determinar horarios de negocio
    
    Ejemplo de uso:
        >>> svc = TimezoneService()
        >>> svc.get_time_in_countries()  # Hora actual en varios países
        >>> svc.format_datetime(some_utc_date, "America/Santiago")
    """
    
    def __init__(self, time_provider: ITimeProvider | None = None):
        """
        Inicializa el servicio.
        
        Args:
            time_provider: Proveedor de tiempo (opcional, usa TimeProvider por defecto).
                          Útil para inyectar FakeTimeProvider en tests.
        """
        self._time_provider = time_provider or TimeProvider()
    
    # =========================================================================
    # OBTENCIÓN DE TIEMPO
    # =========================================================================
    
    def now_utc(self) -> pendulum.DateTime:
        """Obtiene la fecha/hora actual en UTC."""
        return self._time_provider.now()
    
    def now_in_timezone(self, timezone: str) -> pendulum.DateTime:
        """
        Obtiene la fecha/hora actual en una zona horaria específica.
        
        Args:
            timezone: Identificador de zona horaria (ej: "America/Santiago")
        """
        return self._time_provider.now().in_timezone(timezone)
    
    def today_utc(self) -> Date:
        """Obtiene la fecha actual en UTC (sin componente de hora)."""
        return self._time_provider.today()
    
    # =========================================================================
    # LISTADO DE ZONAS HORARIAS
    # =========================================================================
    
    def get_available_timezones(self) -> Sequence[str]:
        """Devuelve todas las zonas horarias soportadas por Pendulum."""
        return pendulum.timezones
    
    def get_common_timezones(self) -> list[tuple[str, str, str]]:
        """
        Devuelve las zonas horarias comunes configuradas.
        
        Returns:
            Lista de tuplas (timezone_id, nombre_display, código_país)
        """
        return list(COMMON_TIMEZONES)
    
    def get_timezone_info(self, timezone: str) -> dict:
        """
        Obtiene información detallada de una zona horaria.
        
        Args:
            timezone: Identificador de zona horaria
        
        Returns:
            Dict con 'name', 'offset', 'offset_hours', 'abbreviation'
        """
        now = self._time_provider.now().in_timezone(timezone)
        return {
            "name": timezone,
            "offset": now.format("Z"),
            "offset_hours": now.offset_hours,
            "abbreviation": now.timezone_name,
        }
    
    def is_valid_timezone(self, timezone: str) -> bool:
        """Verifica si un identificador de zona horaria es válido."""
        return timezone in pendulum.timezones
    
    # =========================================================================
    # CONVERSIÓN ENTRE ZONAS
    # =========================================================================
    
    def convert_to_timezone(
        self,
        dt: pendulum.DateTime,
        target_timezone: str
    ) -> pendulum.DateTime:
        """
        Convierte una fecha a otra zona horaria.
        
        Args:
            dt: Fecha a convertir (cualquier timezone)
            target_timezone: Zona horaria destino
        """
        if not isinstance(dt, pendulum.DateTime):
            dt = pendulum.instance(dt)
        return dt.in_timezone(target_timezone)
    
    def convert_to_utc(self, dt: pendulum.DateTime) -> pendulum.DateTime:
        """Convierte una fecha cualquiera a UTC."""
        return self.convert_to_timezone(dt, "UTC")
    
    # =========================================================================
    # FORMATEO DE FECHAS
    # =========================================================================
    
    def format_datetime(
        self,
        dt: pendulum.DateTime,
        user_timezone: str = DEFAULT_TIMEZONE,
        fmt: str = PENDULUM_DATETIME_FORMAT,
        locale: str = "es"
    ) -> str:
        """
        Formatea una fecha/hora para visualización.
        
        Args:
            dt: Fecha en cualquier zona (se convierte automáticamente)
            user_timezone: Zona horaria del usuario para visualización
            fmt: Formato Pendulum (DD/MM/YYYY HH:mm por defecto)
            locale: Idioma para nombres de meses/días
        
        Returns:
            String formateado de la fecha
        """
        local_dt = self.convert_to_timezone(dt, user_timezone)
        return local_dt.format(fmt, locale=locale)
    
    def format_date(
        self,
        dt: pendulum.DateTime,
        user_timezone: str = DEFAULT_TIMEZONE,
        locale: str = "es"
    ) -> str:
        """
        Formatea solo la parte de fecha (sin hora).
        
        Args:
            dt: Fecha a formatear
            user_timezone: Zona horaria del usuario
            locale: Idioma
        """
        local_dt = self.convert_to_timezone(dt, user_timezone)
        return local_dt.format("DD/MM/YYYY", locale=locale)
    
    def format_time(
        self,
        dt: pendulum.DateTime,
        user_timezone: str = DEFAULT_TIMEZONE
    ) -> str:
        """
        Formatea solo la hora (sin fecha).
        
        Args:
            dt: Fecha/hora a formatear
            user_timezone: Zona horaria del usuario
        """
        local_dt = self.convert_to_timezone(dt, user_timezone)
        return local_dt.format("HH:mm")
    
    def humanize(
        self,
        dt: pendulum.DateTime,
        locale: str = "es"
    ) -> str:
        """
        Devuelve descripción humana relativa al ahora.
        
        Ejemplo: 'hace 2 horas', 'ayer', 'en 3 días'
        
        Args:
            dt: Fecha a humanizar
            locale: Idioma (default: español)
        """
        if not isinstance(dt, pendulum.DateTime):
            dt = pendulum.instance(dt)
        return dt.diff_for_humans(locale=locale)
    
    # =========================================================================
    # COMPARACIÓN MULTI-PAÍS
    # =========================================================================
    
    def get_time_in_countries(
        self, 
        timezones: list[str] | None = None
    ) -> list[dict]:
        """
        Obtiene la hora actual en múltiples países.
        
        Útil para mostrar un panel de relojes mundiales.
        
        Args:
            timezones: Lista de IDs de timezone. Si es None, usa COMMON_TIMEZONES.
        
        Returns:
            Lista de dicts con información de cada país:
            - timezone: ID de la zona
            - display_name: Nombre para mostrar
            - country_code: Código de país (2 letras)
            - current_time: Objeto DateTime
            - formatted_time: Hora formateada (HH:mm)
            - formatted_datetime: Fecha y hora formateada
            - offset: Offset UTC (ej: "-03:00")
            - date: Fecha formateada en español
        """
        if timezones is None:
            zones = COMMON_TIMEZONES
        else:
            # Crear tuplas básicas para timezones personalizadas
            zones = [(tz, tz, "") for tz in timezones]
        
        result = []
        now = self._time_provider.now()
        
        for tz_id, display_name, country_code in zones:
            local_time = now.in_timezone(tz_id)
            result.append({
                "timezone": tz_id,
                "display_name": display_name,
                "country_code": country_code,
                "current_time": local_time,
                "formatted_time": local_time.format("HH:mm", locale="es"),
                "formatted_datetime": local_time.format(
                    PENDULUM_DATETIME_FORMAT, locale="es"
                ),
                "offset": local_time.format("Z"),
                "date": local_time.format("dddd D MMMM", locale="es"),
            })
        
        return result
    
    def get_time_difference(
        self,
        timezone1: str,
        timezone2: str
    ) -> dict:
        """
        Calcula la diferencia de hora entre dos zonas horarias.
        
        Args:
            timezone1: Primera zona horaria
            timezone2: Segunda zona horaria
        
        Returns:
            Dict con 'hours_difference' y 'description'
        """
        now = self._time_provider.now()
        time1 = now.in_timezone(timezone1)
        time2 = now.in_timezone(timezone2)
        
        diff_hours = time1.offset_hours - time2.offset_hours
        
        if diff_hours > 0:
            description = f"{timezone1} está {abs(diff_hours)} horas adelante de {timezone2}"
        elif diff_hours < 0:
            description = f"{timezone1} está {abs(diff_hours)} horas atrás de {timezone2}"
        else:
            description = f"{timezone1} y {timezone2} tienen la misma hora"
        
        return {
            "hours_difference": diff_hours,
            "description": description,
        }
    
    # =========================================================================
    # UTILIDADES DE NEGOCIO
    # =========================================================================
    
    def is_business_hours(
        self,
        dt: pendulum.DateTime | None = None,
        timezone: str = DEFAULT_TIMEZONE,
        start_hour: int = BUSINESS_HOUR_START,
        end_hour: int = BUSINESS_HOUR_END
    ) -> bool:
        """
        Verifica si la fecha/hora está dentro del horario de negocio.
        
        Args:
            dt: Fecha a verificar (None = ahora)
            timezone: Zona horaria del negocio
            start_hour: Hora de inicio (default: 9)
            end_hour: Hora de fin (default: 18)
        
        Returns:
            True si está en horario laboral
        """
        if dt is None:
            dt = self._time_provider.now()
        
        local_dt = self.convert_to_timezone(dt, timezone)
        return (
            local_dt.weekday() in BUSINESS_DAYS
            and start_hour <= local_dt.hour < end_hour
        )
    
    def get_business_day_range(
        self,
        date: Date,
        timezone: str = DEFAULT_TIMEZONE
    ) -> tuple[pendulum.DateTime, pendulum.DateTime]:
        """
        Obtiene el rango de inicio y fin del día de negocio en UTC.
        
        Útil para queries de base de datos que necesitan filtrar por día laboral.
        
        Args:
            date: Fecha del día de negocio
            timezone: Zona horaria del negocio
        
        Returns:
            Tupla (start_utc, end_utc)
        """
        start = pendulum.datetime(
            date.year, date.month, date.day,
            BUSINESS_HOUR_START, 0, 0,
            tz=timezone
        ).in_timezone("UTC")
        
        end = pendulum.datetime(
            date.year, date.month, date.day,
            BUSINESS_HOUR_END, 0, 0,
            tz=timezone
        ).in_timezone("UTC")
        
        return (start, end)
    
    def get_day_range_utc(
        self,
        date: Date,
        timezone: str = DEFAULT_TIMEZONE
    ) -> tuple[pendulum.DateTime, pendulum.DateTime]:
        """
        Obtiene el rango completo de un día (00:00 - 23:59:59) en UTC.
        
        Args:
            date: Fecha del día
            timezone: Zona horaria de referencia
        
        Returns:
            Tupla (start_utc, end_utc)
        """
        start = pendulum.datetime(
            date.year, date.month, date.day,
            0, 0, 0,
            tz=timezone
        ).in_timezone("UTC")
        
        end = pendulum.datetime(
            date.year, date.month, date.day,
            23, 59, 59,
            tz=timezone
        ).in_timezone("UTC")
        
        return (start, end)
    
    def days_until(self, target_date: Date) -> int:
        """
        Calcula los días hasta una fecha objetivo.
        
        Args:
            target_date: Fecha objetivo
        
        Returns:
            Número de días (positivo si es futuro, negativo si es pasado)
        """
        today = self._time_provider.today()
        return (target_date - today).days
    
    def days_since(self, past_date: Date) -> int:
        """
        Calcula los días desde una fecha pasada.
        
        Args:
            past_date: Fecha pasada
        
        Returns:
            Número de días transcurridos
        """
        today = self._time_provider.today()
        return (today - past_date).days
    
    def is_today(self, dt: pendulum.DateTime, timezone: str = DEFAULT_TIMEZONE) -> bool:
        """Verifica si una fecha corresponde al día de hoy."""
        local_dt = self.convert_to_timezone(dt, timezone)
        today = self._time_provider.now().in_timezone(timezone)
        return local_dt.date() == today.date()
    
    def is_past(self, dt: pendulum.DateTime) -> bool:
        """Verifica si una fecha ya pasó."""
        now = self._time_provider.now()
        if not isinstance(dt, pendulum.DateTime):
            dt = pendulum.instance(dt)
        return dt < now
    
    def is_future(self, dt: pendulum.DateTime) -> bool:
        """Verifica si una fecha está en el futuro."""
        now = self._time_provider.now()
        if not isinstance(dt, pendulum.DateTime):
            dt = pendulum.instance(dt)
        return dt > now
    
    # =========================================================================
    # PARSING
    # =========================================================================
    
    def parse(
        self,
        date_str: str,
        user_timezone: str = DEFAULT_TIMEZONE,
        convert_to_utc: bool = True
    ) -> pendulum.DateTime:
        """
        Parsea un string de fecha asumiendo la zona del usuario.
        
        Soporta múltiples formatos comunes automáticamente.
        
        Args:
            date_str: String de fecha (formatos comunes aceptados)
            user_timezone: Zona horaria asumida del input
            convert_to_utc: Si True, convierte el resultado a UTC
        
        Returns:
            DateTime parseado
        """
        local_dt = pendulum.parse(date_str, tz=user_timezone)
        if convert_to_utc:
            return local_dt.in_timezone("UTC")
        return local_dt
    
    def parse_date(self, date_str: str, fmt: str = "DD/MM/YYYY") -> Date:
        """
        Parsea un string de fecha con formato específico.
        
        Args:
            date_str: String de fecha
            fmt: Formato esperado (default: DD/MM/YYYY)
        
        Returns:
            Date parseado
        """
        return pendulum.from_format(date_str, fmt).date()
