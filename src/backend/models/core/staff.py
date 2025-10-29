"""
Staff model - System users.

Este módulo define el modelo de usuarios/staff del sistema.
Los usuarios pueden crear, modificar y eliminar registros en el sistema.
"""

from typing import Optional

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import validates

from ..base import AuditMixin, Base, EmailValidator, PhoneValidator, TimestampMixin


class Staff(Base, TimestampMixin, AuditMixin):
    """
    Usuarios del sistema (staff/empleados).

    Representa a los usuarios que tienen acceso al sistema.
    Se usa para auditoría en otros modelos (created_by, updated_by).

    Attributes:
        id: Primary key
        username: Nombre de usuario único
        email: Email único del usuario
        first_name: Nombre(s)
        last_name: Apellido(s)
        trigram: Código de 3 letras (opcional)
        phone: Teléfono de contacto (opcional)
        position: Cargo/puesto (opcional)
        is_active: Si el usuario está activo
        is_admin: Si el usuario tiene permisos de administrador

    Properties:
        full_name: Nombre completo (first_name + last_name)

    Example:
        >>> staff = Staff(
        ...     username="jdoe",
        ...     email="john.doe@akgroup.com",
        ...     first_name="John",
        ...     last_name="Doe",
        ...     trigram="JDO",
        ...     phone="+56912345678",
        ...     position="Gerente de Ventas",
        ...     is_admin=False
        ... )
        >>> print(staff.full_name)
        'John Doe'
        >>> print(staff.trigram)
        'JDO'
    """

    __tablename__ = "staff"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Authentication
    username = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique username for login",
    )

    email = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique email address",
    )

    # Personal Information
    first_name = Column(
        String(50),
        nullable=False,
        comment="First name(s)",
    )

    last_name = Column(
        String(50),
        nullable=False,
        comment="Last name(s)",
    )

    trigram = Column(
        String(3),
        nullable=True,
        unique=True,
        index=True,
        comment="Three-letter unique staff code (optional)",
    )

    phone = Column(
        String(20),
        nullable=True,
        comment="Contact phone number (E.164 format recommended)",
    )

    position = Column(
        String(100),
        nullable=True,
        comment="Job position/title",
    )

    # Status Flags
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Whether user account is active",
    )

    is_admin = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether user has admin privileges",
    )

    # Validators
    @validates("email")
    def validate_email(self, key: str, value: str) -> str:
        """
        Valida formato de email.

        Args:
            key: Nombre del campo
            value: Email a validar

        Returns:
            Email validado y normalizado (lowercase)

        Raises:
            ValueError: Si el formato del email es inválido
        """
        return EmailValidator.validate(value)

    @validates("username")
    def validate_username(self, key: str, value: str) -> str:
        """
        Valida username.

        Args:
            key: Nombre del campo
            value: Username a validar

        Returns:
            Username normalizado (lowercase, sin espacios)

        Raises:
            ValueError: Si el username es muy corto o inválido
        """
        if not value or len(value.strip()) < 3:
            raise ValueError("Username must be at least 3 characters")

        # Normalizar a lowercase y sin espacios
        normalized = value.strip().lower()

        # Solo permitir alfanuméricos, guiones y underscores
        import re

        if not re.match(r"^[a-z0-9_-]+$", normalized):
            raise ValueError(
                "Username can only contain lowercase letters, numbers, hyphens and underscores"
            )

        return normalized

    @validates("first_name", "last_name")
    def validate_name(self, key: str, value: str) -> str:
        """
        Valida nombres.

        Args:
            key: Nombre del campo
            value: Nombre a validar

        Returns:
            Nombre normalizado (capitalizado)

        Raises:
            ValueError: Si el nombre está vacío
        """
        if not value or len(value.strip()) == 0:
            raise ValueError(f"{key} cannot be empty")

        return value.strip()

    @validates("trigram")
    def validate_trigram(self, key: str, value: Optional[str]) -> Optional[str]:
        """
        Valida trigrama (3 letras, único).

        Args:
            key: Nombre del campo
            value: Trigrama a validar

        Returns:
            Trigrama normalizado (mayúsculas) o None

        Raises:
            ValueError: Si el trigrama no tiene 3 letras

        Example:
            >>> staff.trigram = "jdo"
            >>> staff.trigram
            'JDO'
        """
        if value is None or value.strip() == "":
            return None

        value = value.strip()

        if len(value) != 3:
            raise ValueError("Trigram must be exactly 3 characters")

        if not value.isalpha():
            raise ValueError("Trigram must contain only letters")

        return value.upper()

    @validates("phone")
    def validate_phone(self, key: str, value: Optional[str]) -> Optional[str]:
        """
        Valida teléfono.

        Args:
            key: Nombre del campo
            value: Teléfono a validar

        Returns:
            Teléfono validado o None

        Raises:
            ValueError: Si el formato del teléfono es inválido

        Example:
            >>> staff.phone = "+56 9 1234 5678"
            >>> staff.phone
            '+56912345678'
        """
        return PhoneValidator.validate(value)

    @validates("position")
    def validate_position(self, key: str, value: Optional[str]) -> Optional[str]:
        """
        Valida cargo/puesto.

        Args:
            key: Nombre del campo
            value: Cargo a validar

        Returns:
            Cargo normalizado o None

        Example:
            >>> staff.position = "  Gerente de Ventas  "
            >>> staff.position
            'Gerente de Ventas'
        """
        if value is None or value.strip() == "":
            return None

        return value.strip()

    # Properties
    @property
    def full_name(self) -> str:
        """
        Nombre completo del usuario.

        Returns:
            Nombre completo en formato "First Last"

        Example:
            >>> staff = Staff(first_name="John", last_name="Doe")
            >>> staff.full_name
            'John Doe'
        """
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        """String representation."""
        trigram_str = f", trigram={self.trigram}" if self.trigram else ""
        return f"<Staff(id={self.id}, username={self.username}{trigram_str}, active={self.is_active})>"
