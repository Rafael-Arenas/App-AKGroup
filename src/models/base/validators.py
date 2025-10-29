"""
Validadores comunes para campos de modelos.

Este módulo proporciona validadores reutilizables para campos comunes:
- EmailValidator: Valida formato de email
- PhoneValidator: Valida teléfonos (formato E.164)
- RutValidator: Valida RUT chileno con dígito verificador

Uso típico en modelos:
    from sqlalchemy.orm import validates
    from models.base.validators import EmailValidator

    class Contact(Base):
        email = Column(String(100))

        @validates("email")
        def validate_email(self, key, value):
            return EmailValidator.validate(value)
"""

import re
from decimal import Decimal
from typing import Optional


class EmailValidator:
    """
    Validador de direcciones de email.

    Valida formato básico según RFC 5322 simplificado.
    Convierte a lowercase para normalización.

    Example:
        >>> EmailValidator.validate("user@example.com")
        'user@example.com'
        >>> EmailValidator.validate("INVALID")
        ValueError: Invalid email format: INVALID
    """

    @staticmethod
    def validate(value: Optional[str]) -> Optional[str]:
        """
        Valida y normaliza un email.

        Args:
            value: Email a validar (puede ser None)

        Returns:
            Email normalizado (lowercase) o None si value es None

        Raises:
            ValueError: Si el formato del email es inválido
        """
        if not value:
            return value

        value = value.strip().lower()

        # Patrón RFC 5322 simplificado
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(pattern, value):
            raise ValueError(f"Invalid email format: {value}")

        return value


class PhoneValidator:
    """
    Validador de números telefónicos (formato E.164).

    Formato E.164: +[código país][número], 8-15 dígitos totales
    Ejemplos válidos: +56912345678, +33123456789, 912345678

    El validador acepta separadores comunes (-,espacios,paréntesis,puntos)
    pero los elimina para validación.

    Example:
        >>> PhoneValidator.validate("+56 9 1234 5678")
        '+56912345678'
        >>> PhoneValidator.validate("123")
        ValueError: Phone must be 8-15 digits...
    """

    @staticmethod
    def validate(value: Optional[str]) -> Optional[str]:
        """
        Valida formato de teléfono.

        Args:
            value: Número telefónico (puede ser None)

        Returns:
            Número telefónico original (con formato) o None

        Raises:
            ValueError: Si el formato es inválido
        """
        if not value:
            return value

        # Eliminar separadores comunes para validación
        clean = re.sub(r"[\s\-\(\)\.]+", "", value)

        # Validar formato E.164: +[país][número], 8-15 dígitos
        if not re.match(r"^\+?[0-9]{8,15}$", clean):
            raise ValueError(
                f"Phone must be 8-15 digits, optionally starting with +. Got: {value}"
            )

        return value  # Retornar con formato original


class RutValidator:
    """
    Validador de RUT chileno (Rol Único Tributario).

    Valida:
    - Formato: 12345678-9 o 12.345.678-9
    - Dígito verificador correcto (algoritmo módulo 11)

    El validador acepta formatos con/sin puntos/guiones y
    retorna en formato normalizado: 12345678-9

    Example:
        >>> RutValidator.validate("12.345.678-5")
        '12345678-5'
        >>> RutValidator.validate("12345678-0")
        ValueError: Invalid RUT check digit...
    """

    @staticmethod
    def validate(value: Optional[str]) -> Optional[str]:
        """
        Valida RUT chileno con dígito verificador.

        Args:
            value: RUT a validar (puede ser None)

        Returns:
            RUT normalizado en formato 12345678-K o None

        Raises:
            ValueError: Si el RUT es inválido o dígito verificador incorrecto
        """
        if not value:
            return value

        # Eliminar formato (puntos, guiones, espacios)
        rut = re.sub(r"[^\dKk]", "", value)

        if len(rut) < 2:
            raise ValueError(f"RUT too short: {value}")

        # Separar número y dígito verificador
        number = rut[:-1]
        check_digit = rut[-1].upper()

        # Calcular dígito verificador esperado (algoritmo módulo 11)
        reversed_digits = map(int, reversed(number))
        factors = [2, 3, 4, 5, 6, 7]  # Factores cíclicos
        s = sum(d * factors[i % 6] for i, d in enumerate(reversed_digits))
        expected = 11 - (s % 11)

        # Convertir a dígito esperado
        if expected == 11:
            expected_digit = "0"
        elif expected == 10:
            expected_digit = "K"
        else:
            expected_digit = str(expected)

        # Validar dígito verificador
        if check_digit != expected_digit:
            raise ValueError(
                f"Invalid RUT check digit: {value} "
                f"(expected {expected_digit}, got {check_digit})"
            )

        # Retornar RUT normalizado
        return f"{number}-{check_digit}"

    @staticmethod
    def format(value: Optional[str]) -> Optional[str]:
        """
        Formatea un RUT válido con puntos y guión.

        Args:
            value: RUT válido (debe pasar validate primero)

        Returns:
            RUT formateado: 12.345.678-9

        Example:
            >>> RutValidator.format("12345678-5")
            '12.345.678-5'
        """
        if not value:
            return value

        # Separar número y dígito
        parts = value.split("-")
        if len(parts) != 2:
            return value

        number, check = parts

        # Añadir puntos cada 3 dígitos (de derecha a izquierda)
        formatted = ""
        for i, digit in enumerate(reversed(number)):
            if i > 0 and i % 3 == 0:
                formatted = "." + formatted
            formatted = digit + formatted

        return f"{formatted}-{check}"


class UrlValidator:
    """
    Validador de URLs.

    Valida que la URL comience con http:// o https://

    Example:
        >>> UrlValidator.validate("https://example.com")
        'https://example.com'
        >>> UrlValidator.validate("example.com")
        ValueError: URL must start with http:// or https://
    """

    @staticmethod
    def validate(value: Optional[str]) -> Optional[str]:
        """
        Valida formato de URL.

        Args:
            value: URL a validar (puede ser None)

        Returns:
            URL validada o None

        Raises:
            ValueError: Si no comienza con http:// o https://
        """
        if not value:
            return value

        value = value.strip()

        if not re.match(r"^https?://", value, re.IGNORECASE):
            raise ValueError(f"URL must start with http:// or https://. Got: {value}")

        return value


class DecimalValidator:
    """
    Validador de valores decimales.

    Útil para validar precios, cantidades, etc.

    Example:
        >>> DecimalValidator.validate_positive(Decimal("100.50"), "price")
        Decimal('100.50')
        >>> DecimalValidator.validate_positive(Decimal("-10"), "price")
        ValueError: price cannot be negative
    """

    @staticmethod
    def validate_positive(value, field_name: str = "value"):
        """
        Valida que un Decimal sea positivo (>= 0).

        Args:
            value: Decimal a validar
            field_name: Nombre del campo para mensajes de error

        Returns:
            Valor validado

        Raises:
            ValueError: Si el valor es negativo
        """
        if value is not None and value < 0:
            raise ValueError(f"{field_name} cannot be negative. Got: {value}")
        return value

    @staticmethod
    def validate_non_negative(value: Optional[Decimal], field_name: str = "value") -> Optional[Decimal]:
        """
        Valida que un Decimal sea no negativo (>= 0).

        Alias de validate_positive para mayor claridad semántica.

        Args:
            value: Decimal a validar
            field_name: Nombre del campo para mensajes de error

        Returns:
            Valor validado

        Raises:
            ValueError: Si el valor es negativo

        Example:
            >>> DecimalValidator.validate_non_negative(Decimal("0"), "price")
            Decimal('0')
            >>> DecimalValidator.validate_non_negative(Decimal("-10"), "price")
            ValueError: price cannot be negative
        """
        return DecimalValidator.validate_positive(value, field_name)

    @staticmethod
    def validate_non_negative_integer(value: Optional[int], field_name: str = "value") -> Optional[int]:
        """
        Valida que un entero sea no negativo (>= 0).

        Args:
            value: Entero a validar
            field_name: Nombre del campo para mensajes de error

        Returns:
            Valor validado

        Raises:
            ValueError: Si el valor es negativo
        """
        if value is not None and value < 0:
            raise ValueError(f"{field_name} cannot be negative. Got: {value}")
        return value
