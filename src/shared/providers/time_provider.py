from typing import Protocol
import pendulum

class ITimeProvider(Protocol):
    """Interfaz para proveedores de tiempo."""
    def now(self) -> pendulum.DateTime:
        """Devuelve el instante actual en UTC."""
        ...

class TimeProvider:
    """
    Proveedor de tiempo real del sistema.
    Debe usarse como la implementación por defecto en producción.
    """
    def now(self) -> pendulum.DateTime:
        return pendulum.now("UTC")

class FakeTimeProvider:
    """
    Proveedor de tiempo falso para testing.
    Permite fijar una hora específica y avanzar el tiempo manualmente.
    """
    def __init__(self, start_time: pendulum.DateTime | None = None):
        if start_time is None:
            start_time = pendulum.now("UTC")
        self._current_time = start_time

    def now(self) -> pendulum.DateTime:
        return self._current_time

    def set_time(self, new_time: pendulum.DateTime) -> None:
        """Establece una nueva hora fija."""
        self._current_time = new_time

    def advance(self, **kwargs) -> None:
        """
        Avanza el reloj interno por la duración especificada.
        Ejemplo: provider.advance(days=1, hours=2)
        """
        self._current_time = self._current_time.add(**kwargs)
