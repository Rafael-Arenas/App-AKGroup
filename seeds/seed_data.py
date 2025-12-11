"""
Script para insertar datos iniciales en la base de datos.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.models.core.companies import Company
from src.backend.models.lookups.lookups import CompanyType, Unit

# Crear engine y sesión
engine = create_engine('sqlite:///app_akgroup.db', echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # 1. Insertar tipos de empresa
    print("\n=== Insertando Company Types ===")
    existing_types = db.query(CompanyType).count()
    if existing_types == 0:
        company_types = [
            CompanyType(name='Cliente', description='Empresa cliente'),
            CompanyType(name='Proveedor', description='Empresa proveedora'),
            CompanyType(name='Ambos', description='Cliente y proveedor'),
        ]
        db.add_all(company_types)
        db.commit()
        print(f"OK - {len(company_types)} tipos de empresa insertados")
    else:
        print(f"OK - Ya existen {existing_types} tipos de empresa")

    # 2. Insertar unidades
    print("\n=== Insertando Units ===")
    existing_units = db.query(Unit).count()
    if existing_units == 0:
        units = [
            Unit(name='Unidad', code='UN', description='Unidad individual'),
            Unit(name='Kilogramo', code='KG', description='Kilogramo'),
            Unit(name='Metro', code='M', description='Metro lineal'),
            Unit(name='Litro', code='L', description='Litro'),
        ]
        db.add_all(units)
        db.commit()
        print(f"OK - {len(units)} unidades insertadas")
    else:
        print(f"OK - Ya existen {existing_units} unidades")

    # 3. Insertar empresa de ejemplo
    print("\n=== Insertando Company ===")
    existing_companies = db.query(Company).count()
    if existing_companies == 0:
        company = Company(
            name='AK Group SpA',
            trigram='AKG',
            phone='+56912345678',
            website='https://akgroup.cl',
            company_type_id=1,
            created_by_id=1,
            updated_by_id=1,
            is_active=True
        )
        db.add(company)
        db.commit()
        db.refresh(company)
        print(f"OK - Empresa creada: ID={company.id}, Nombre={company.name}, Trigram={company.trigram}")
    else:
        print(f"OK - Ya existen {existing_companies} empresas")
        companies = db.query(Company).all()
        for c in companies:
            print(f"  - [{c.id}] {c.name} ({c.trigram})")

    # 4. Verificar datos insertados
    print("\n=== Resumen ===")
    print(f"Company Types: {db.query(CompanyType).count()}")
    print(f"Units: {db.query(Unit).count()}")
    print(f"Companies: {db.query(Company).count()}")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\nOK - Proceso completado")
