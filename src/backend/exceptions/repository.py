"""
Excepciones de la capa de repositorio.

Define excepciones específicas para operaciones de acceso a datos
y gestión de entidades en la capa de repositorio.
"""

from src.backend.exceptions.base import DatabaseException


class NotFoundException(DatabaseException):
    """
    Excepción lanzada cuando una entidad no se encuentra en la base de datos.

    Se utiliza en operaciones get_by_id, update, delete cuando la entidad
    solicitada no existe.

    Example:
        company = repository.get_by_id(999)
        if not company:
            raise NotFoundException(
                "Company no encontrada",
                details={"company_id": 999}
            )
    """

    def __init__(self, message: str = "Entidad no encontrada", details: dict = None):
        super().__init__(message, details)


class DuplicateException(DatabaseException):
    """
    Excepción lanzada cuando se intenta crear una entidad duplicada.

    Se utiliza cuando se viola una constraint UNIQUE, como intentar
    crear una empresa con un trigram que ya existe.

    Example:
        existing = repository.get_by_trigram("AKG")
        if existing:
            raise DuplicateException(
                "Trigram ya existe",
                details={"trigram": "AKG", "company_id": existing.id}
            )
    """

    def __init__(self, message: str = "Entidad duplicada", details: dict = None):
        super().__init__(message, details)


class InvalidStateException(DatabaseException):
    """
    Excepción lanzada cuando una entidad está en un estado inválido.

    Se utiliza cuando se intenta realizar una operación sobre una entidad
    que no está en el estado correcto (ej: eliminar una entidad ya eliminada).

    Example:
        if company.is_deleted:
            raise InvalidStateException(
                "No se puede modificar una empresa eliminada",
                details={"company_id": company.id, "is_deleted": True}
            )
    """

    def __init__(self, message: str = "Estado inválido de entidad", details: dict = None):
        super().__init__(message, details)
