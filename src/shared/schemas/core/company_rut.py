"""
Schemas de Pydantic para CompanyRut.

Define los schemas de validación para operaciones CRUD sobre RUTs de empresas.
"""

import re
from typing import Optional

from pydantic import Field, field_validator

from src.shared.schemas.base import BaseSchema, BaseResponse


def validate_rut(value: str) -> str:
    """
    Valida RUT chileno con dígito verificador.
    
    Args:
        value: RUT a validar
        
    Returns:
        RUT normalizado (sin puntos, con guión)
        
    Raises:
        ValueError: Si el RUT es inválido
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


# ============================================================================
# COMPANY RUT SCHEMAS
# ============================================================================

class CompanyRutCreate(BaseSchema):
    """
    Schema para crear un nuevo RUT de empresa.

    Example:
        data = CompanyRutCreate(
            rut="76.123.456-7",
            is_main=True,
            company_id=1
        )
    """

    rut: str = Field(
        ...,
        min_length=8,  # Minimum for normalized format (e.g., 1-9)
        max_length=12,  # Maximum for input format with dots
        description="RUT chileno (formato: 12345678-9 o 76.123.456-7)"
    )
    is_main: Optional[bool] = Field(
        False,
        description="Si es el RUT principal de la empresa"
    )
    company_id: int = Field(
        ...,
        gt=0,
        description="ID de la empresa"
    )

    @field_validator('rut')
    @classmethod
    def validate_rut_field(cls, v: str) -> str:
        """Valida y normaliza el RUT chileno."""
        return validate_rut(v)


class CompanyRutUpdate(BaseSchema):
    """
    Schema para actualizar un RUT de empresa.

    Example:
        data = CompanyRutUpdate(
            is_main=False
        )
    """

    rut: Optional[str] = Field(None, min_length=8, max_length=12)
    is_main: Optional[bool] = None

    @field_validator('rut')
    @classmethod
    def validate_rut_field(cls, v: Optional[str]) -> Optional[str]:
        """Valida y normaliza el RUT chileno si se proporciona."""
        if v is not None:
            return validate_rut(v)
        return v


class CompanyRutResponse(BaseResponse):
    """
    Schema para respuesta de RUT de empresa.

    Example:
        rut = CompanyRutResponse.model_validate(rut_orm)
        print(rut.rut)
        print(rut.is_main)
    """

    rut: str
    is_main: bool
    company_id: int
