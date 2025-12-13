import re

def calculate_dv(rut_number: str) -> str:
    """
    Calcula el dígito verificador para un número de RUT.
    
    Args:
        rut_number: Parte numérica del RUT (sin puntos ni guión)
        
    Returns:
        Dígito verificador ('0'-'9' o 'K')
    """
    try:
        rut = int(rut_number)
    except ValueError:
        return ""
        
    factors = [2, 3, 4, 5, 6, 7]
    s = 0
    for i, digit in enumerate(reversed(str(rut))):
        s += int(digit) * factors[i % 6]
    
    expected = 11 - (s % 11)
    if expected == 11:
        return "0"
    elif expected == 10:
        return "K"
    else:
        return str(expected)

def format_rut(value: str) -> str:
    """
    Formatea un RUT agregando puntos y guión.
    Ej: 123456789 -> 12.345.678-9
    
    Args:
        value: RUT a formatear
        
    Returns:
        RUT formateado
    """
    if not value:
        return ""
        
    # Limpiar caracteres no alfanuméricos
    clean_value = re.sub(r"[^0-9Kk]", "", value).upper()
    
    if len(clean_value) < 2:
        return clean_value
        
    rut_number = clean_value[:-1]
    dv = clean_value[-1]
    
    # Formatear número con puntos
    formatted_number = ""
    for i, digit in enumerate(reversed(rut_number)):
        if i > 0 and i % 3 == 0:
            formatted_number = "." + formatted_number
        formatted_number = digit + formatted_number
        
    return f"{formatted_number}-{dv}"

def validate_rut(value: str) -> tuple[bool, str]:
    """
    Valida un RUT chileno.
    
    Args:
        value: RUT a validar
        
    Returns:
        Tuple (es_valido, mensaje_error)
    """
    if not value:
        return False, "El RUT es obligatorio"
        
    clean_value = re.sub(r"[^0-9Kk]", "", value).upper()
    
    if len(clean_value) < 2:
        return False, "El RUT es muy corto"
        
    if len(clean_value) > 9:  # 99.999.999-K (8 digits + 1 dv = 9 chars unformatted)
        return False, "El RUT es muy largo"
        
    rut_number = clean_value[:-1]
    dv = clean_value[-1]
    
    if not rut_number.isdigit():
        return False, "La parte numérica debe contener solo dígitos"
        
    expected_dv = calculate_dv(rut_number)
    
    if dv != expected_dv:
        return False, f"Dígito verificador incorrecto (se esperaba {expected_dv})"
        
    return True, ""
