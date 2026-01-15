"""
Staff model - System users.

Este módulo define el modelo de usuarios/staff del sistema.
Los usuarios pueden crear, modificar y eliminar registros en el sistema.
"""

import re
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, validates

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
    """

    __tablename__ = "staff"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Authentication
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, comment="Unique username for login"
    )
    email: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, comment="Unique email address"
    )

    # Personal Information
    first_name: Mapped[str] = mapped_column(String(50), comment="First name(s)")
    last_name: Mapped[str] = mapped_column(String(50), comment="Last name(s)")
    trigram: Mapped[str | None] = mapped_column(
        String(3),
        unique=True,
        index=True,
        comment="Three-letter unique staff code (optional)",
    )
    phone: Mapped[str | None] = mapped_column(
        String(20), comment="Contact phone number (E.164 format recommended)"
    )
    position: Mapped[str | None] = mapped_column(
        String(100), comment="Job position/title"
    )

    # Status Flags
    is_active: Mapped[bool] = mapped_column(
        default=True, index=True, comment="Whether user account is active"
    )
    is_admin: Mapped[bool] = mapped_column(
        default=False, comment="Whether user has admin privileges"
    )

    # Validators
    @validates("email")
    def validate_email(self, key: str, value: str) -> str:
        """Valida formato de email."""
        return EmailValidator.validate(value)

    @validates("username")
    def validate_username(self, key: str, value: str) -> str:
        """Valida username."""
        if not value or len(value.strip()) < 3:
            raise ValueError("Username must be at least 3 characters")

        normalized = value.strip().lower()

        if not re.match(r"^[a-z0-9_-]+$", normalized):
            raise ValueError(
                "Username can only contain lowercase letters, numbers, hyphens and underscores"
            )

        return normalized

    @validates("first_name", "last_name")
    def validate_name(self, key: str, value: str) -> str:
        """Valida nombres."""
        if not value or len(value.strip()) == 0:
            raise ValueError(f"{key} cannot be empty")
        return value.strip()

    @validates("trigram")
    def validate_trigram(self, key: str, value: str | None) -> str | None:
        """Valida trigrama (3 letras, único)."""
        if value is None or value.strip() == "":
            return None

        value = value.strip()

        if len(value) != 3:
            raise ValueError("Trigram must be exactly 3 characters")

        if not value.isalpha():
            raise ValueError("Trigram must contain only letters")

        return value.upper()

    @validates("phone")
    def validate_phone(self, key: str, value: str | None) -> str | None:
        """Valida teléfono."""
        return PhoneValidator.validate(value)

    @validates("position")
    def validate_position(self, key: str, value: str | None) -> str | None:
        """Valida cargo/puesto."""
        if value is None or value.strip() == "":
            return None
        return value.strip()

    # Properties
    @property
    def full_name(self) -> str:
        """Nombre completo del usuario."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        """String representation."""
        trigram_str = f", trigram={self.trigram}" if self.trigram else ""
        return f"<Staff(id={self.id}, username={self.username}{trigram_str}, active={self.is_active})>"
