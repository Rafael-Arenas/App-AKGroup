"""
Script para verificar y poblar detalles de empresas (RUTs, Contactos, Plantas).
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.models.core.companies import Company, CompanyRut, Plant
from src.backend.models.core.contacts import Contact, Service
from src.backend.models.lookups.lookups import City

# Crear engine y sesión
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app_akgroup.db')
engine = create_engine(f'sqlite:///{db_path}', echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def get_or_create(model, **kwargs):
    defaults = kwargs.pop('defaults', {})
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    
    params = {**kwargs, **defaults}
    instance = model(**params)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance

try:
    print("\n=== Verificando Empresas ===")
    companies = db.query(Company).all()
    if not companies:
        print("❌ No hay empresas. Ejecuta seed_data.py primero.")
        exit(1)
    
    print(f"Encontradas {len(companies)} empresas.")
    
    # Tomamos la primera empresa (generalmente AK Group o la primera creada)
    main_company = companies[0]
    print(f"Empresa Principal: {main_company.name} (ID: {main_company.id})")

    # 1. Insertar RUTs
    print("\n=== Insertando RUTs ===")
    # Rut ficticio para AK Group (Validado)
    rut_ak = get_or_create(
        CompanyRut, 
        company_id=main_company.id, 
        rut="76.086.428-5",  # RUT Válido
        defaults={"is_main": True}
    )
    print(f"✅ RUT creado/existente: {rut_ak.rut} (ID: {rut_ak.id})")

    # Rut para otra empresa si existe
    if len(companies) > 1:
        other_company = companies[1]
        rut_other = get_or_create(
            CompanyRut,
            company_id=other_company.id,
            rut="12.345.678-5", # RUT Válido
            defaults={"is_main": True}
        )
        print(f"✅ RUT creado/existente: {rut_other.rut} (ID: {rut_other.id})")

    # 2. Insertar Plantas (Sucursales)
    print("\n=== Insertando Plantas ===")
    # Buscar ciudad Santiago
    santiago = db.query(City).filter(City.name == "Santiago").first()
    city_id = santiago.id if santiago else None

    plant_main = get_or_create(
        Plant,
        company_id=main_company.id,
        name="Casa Matriz",
        defaults={
            "address": "Av. Principal 1234",
            "phone": "+56222222222",
            "email": "contacto@akgroup.cl",
            "city_id": city_id,
            "is_active": True
        }
    )
    print(f"✅ Planta creada/existente: {plant_main.name} (ID: {plant_main.id})")

    # 3. Insertar Servicios (Departamentos)
    print("\n=== Insertando Servicios ===")
    services_data = ["Ventas", "Adquisiciones", "Gerencia"]
    services = {}
    for s_name in services_data:
        svc = get_or_create(Service, name=s_name, defaults={"description": f"Departamento de {s_name}"})
        services[s_name] = svc
        print(f"✅ Servicio: {svc.name} (ID: {svc.id})")

    # 4. Insertar Contactos
    print("\n=== Insertando Contactos ===")
    contact_main = get_or_create(
        Contact,
        email="contacto@cliente.cl",
        defaults={
            "first_name": "Contacto",
            "last_name": "Principal",
            "phone": "+56911111111",
            "position": "Gerente Adquisiciones",
            "company_id": main_company.id,
            "service_id": services["Adquisiciones"].id,
            "is_active": True
        }
    )
    print(f"✅ Contacto creado/existente: {contact_main.full_name} (ID: {contact_main.id})")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n✅ Proceso completado exitosamente")
