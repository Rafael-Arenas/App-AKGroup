"""
Excepciones base para la aplicación AK Group.

Define las excepciones base de las cuales heredan todas las demás
excepciones personalizadas de la aplicación.
"""


class AppException(Exception):
    """
    Excepción base para todas las excepciones de la aplicación.

    Todas las excepciones personalizadas deben heredar de esta clase.
    Permite capturar todas las excepciones de la aplicación en un solo except.

    Attributes:
        message: Mensaje descriptivo del error
        details: Detalles adicionales opcionales

    Example:
        try:
            # operación
            pass
        except AppException as e:
            logger.error(f"Error de aplicación: {e.message}")
    """

    def __init__(self, message: str, details: dict = None):
        """
        Inicializa la excepción.

        Args:
            message: Mensaje descriptivo del error
            details: Diccionario con detalles adicionales opcionales
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        """Representación en string de la excepción."""
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class DatabaseException(AppException):
    """
    Excepción relacionada con operaciones de base de datos.

    Se lanza cuando ocurren errores al interactuar con la base de datos,
    como problemas de conexión, constraints violados, etc.

    Example:
        if connection_failed:
            raise DatabaseException(
                "No se pudo conectar a la base de datos",
                details={"host": "localhost", "port": 3306}
            )
    """

    pass
