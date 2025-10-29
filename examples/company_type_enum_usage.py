"""
Ejemplos de uso del CompanyTypeEnum.

Este archivo muestra cómo usar el CompanyTypeEnum para trabajar
con tipos de empresa de forma type-safe.
"""

from src.models import Company, CompanyTypeEnum


def example_basic_usage():
    """Ejemplo básico de uso del enum."""
    # Acceder a los valores del enum
    print("=== Valores del Enum ===")
    print(f"CLIENT: {CompanyTypeEnum.CLIENT}")
    print(f"SUPPLIER: {CompanyTypeEnum.SUPPLIER}")
    print()

    # Acceder a propiedades
    print("=== Propiedades del Enum ===")
    print(f"Display name CLIENT: {CompanyTypeEnum.CLIENT.display_name}")
    print(f"Description CLIENT: {CompanyTypeEnum.CLIENT.description}")
    print()
    print(f"Display name SUPPLIER: {CompanyTypeEnum.SUPPLIER.display_name}")
    print(f"Description SUPPLIER: {CompanyTypeEnum.SUPPLIER.description}")
    print()


def example_with_company(company: Company):
    """
    Ejemplo de uso con un objeto Company.

    Args:
        company: Instancia de Company con company_type cargado
    """
    print("=== Uso con Company ===")

    # Acceder al enum desde la company
    company_type_enum = company.company_type_enum

    if company_type_enum:
        print(f"Tipo: {company_type_enum.value}")
        print(f"Nombre: {company_type_enum.display_name}")
        print(f"Descripción: {company_type_enum.description}")
        print()

    # Comparaciones type-safe
    if company_type_enum == CompanyTypeEnum.CLIENT:
        print("✓ Esta empresa es un CLIENTE")
        # Lógica específica para clientes
    elif company_type_enum == CompanyTypeEnum.SUPPLIER:
        print("✓ Esta empresa es un PROVEEDOR")
        # Lógica específica para proveedores
    print()


def example_filtering():
    """Ejemplo de cómo filtrar empresas por tipo usando el enum."""
    from sqlalchemy.orm import Session

    print("=== Filtrado de Empresas ===")

    # Nota: Esto es pseudocódigo - necesitas una sesión real
    # session: Session = get_session()

    # Filtrar clientes
    # clients = session.query(Company).join(CompanyType).filter(
    #     CompanyType.name == CompanyTypeEnum.CLIENT.value
    # ).all()

    # Filtrar proveedores
    # suppliers = session.query(Company).join(CompanyType).filter(
    #     CompanyType.name == CompanyTypeEnum.SUPPLIER.value
    # ).all()

    print("Ver código fuente para ejemplos de queries")
    print()


def example_validation():
    """Ejemplo de validación usando el enum."""
    print("=== Validación con Enum ===")

    # Validar que un string es un tipo válido
    company_type_str = "CLIENT"

    try:
        company_type = CompanyTypeEnum[company_type_str]
        print(f"✓ '{company_type_str}' es válido: {company_type.display_name}")
    except KeyError:
        print(f"✗ '{company_type_str}' no es un tipo válido")

    # Intentar con valor inválido
    invalid_type = "PARTNER"
    try:
        company_type = CompanyTypeEnum[invalid_type]
        print(f"✓ '{invalid_type}' es válido: {company_type.display_name}")
    except KeyError:
        print(f"✗ '{invalid_type}' no es un tipo válido")
    print()


def example_iteration():
    """Ejemplo de iteración sobre todos los tipos."""
    print("=== Todos los Tipos de Empresa ===")

    for company_type in CompanyTypeEnum:
        print(f"- {company_type.value}: {company_type.display_name}")
        print(f"  Descripción: {company_type.description}")
    print()


def main():
    """Ejecutar todos los ejemplos."""
    print("=" * 60)
    print("EJEMPLOS DE USO: CompanyTypeEnum")
    print("=" * 60)
    print()

    example_basic_usage()
    example_validation()
    example_iteration()
    example_filtering()

    print("=" * 60)
    print("NOTA: Para usar example_with_company(), necesitas una")
    print("instancia de Company con company_type cargado")
    print("=" * 60)


if __name__ == "__main__":
    main()
