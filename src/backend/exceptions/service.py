"""
Excepciones de la capa de servicio.

Define excepciones específicas para lógica de negocio y validaciones
en la capa de servicio.
"""

from src.backend.exceptions.base import AppException


class ValidationException(AppException):
    """
    Excepción lanzada cuando fallan las validaciones de datos.

    Se utiliza cuando los datos de entrada no cumplen con las reglas
    de validación de negocio o formato.

    Example:
        if discount_percentage > 50:
            raise ValidationException(
                "El descuento no puede exceder el 50%",
                details={"discount_percentage": discount_percentage, "max": 50}
            )
    """

    def __init__(self, message: str = "Error de validación", details: dict | None = None):
        super().__init__(message, details)


class BusinessRuleException(AppException):
    """
    Excepción lanzada cuando se viola una regla de negocio.

    Se utiliza cuando una operación no se puede realizar porque viola
    una regla de negocio específica.

    Example:
        if quote.status != "ACCEPTED":
            raise BusinessRuleException(
                "Solo se pueden convertir cotizaciones aceptadas a órdenes",
                details={"quote_id": quote.id, "status": quote.status}
            )
    """

    def __init__(self, message: str = "Regla de negocio violada", details: dict | None = None):
        super().__init__(message, details)


class UnauthorizedException(AppException):
    """
    Excepción lanzada cuando un usuario no tiene autorización.

    Se utiliza cuando un usuario intenta realizar una operación para
    la cual no tiene permisos.

    Example:
        if not user.is_admin:
            raise UnauthorizedException(
                "Solo administradores pueden eliminar empresas",
                details={"user_id": user.id, "required_role": "admin"}
            )
    """

    def __init__(self, message: str = "No autorizado", details: dict | None = None):
        super().__init__(message, details)
