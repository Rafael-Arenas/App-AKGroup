"""
Script para insertar más empresas (clientes y proveedores) en la base de datos.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.models.core.companies import Company
try:
    from src.backend.models.lookups import CompanyType, City, Country
except ImportError:
    # Fallback por si acaso
    from src.backend.models.lookups.lookups import CompanyType, City, Country

# Crear engine y sesión
engine = create_engine('sqlite:///app_akgroup.db', echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Verificar tipos de empresa
    client_type = db.query(CompanyType).filter(CompanyType.name == 'Cliente').first()
    supplier_type = db.query(CompanyType).filter(CompanyType.name == 'Proveedor').first()
    both_type = db.query(CompanyType).filter(CompanyType.name == 'Ambos').first()
    
    if not client_type or not supplier_type or not both_type:
        print("❌ Tipos de empresa no encontrados. Ejecuta seed_data.py primero.")
        exit(1)

    # Obtener ciudades chilenas
    santiago = db.query(City).filter(City.name == 'Santiago').first()
    providencia = db.query(City).filter(City.name == 'Providencia').first()
    las_condes = db.query(City).filter(City.name == 'Las Condes').first()
    vitacura = db.query(City).filter(City.name == 'Vitacura').first()
    valparaiso = db.query(City).filter(City.name == 'Valparaíso').first()
    vina = db.query(City).filter(City.name == 'Viña del Mar').first()
    concepcion = db.query(City).filter(City.name == 'Concepción').first()
    antofagasta = db.query(City).filter(City.name == 'Antofagasta').first()

    print(f"\n=== Insertando Empresas Clientes ===")
    existing_clients = db.query(Company).filter(Company.company_type_id == client_type.id).count()
    
    if existing_clients <= 1:  # Solo AK Group existe
        clients = [
            Company(
                name='Constructora Inmobiliaria Ltda.',
                trigram='CIL',
                phone='+56228765432',
                website='https://constructorainmobiliaria.cl',
                main_address='Av. Providencia 1234',
                city_id=santiago.id if santiago else None,
                company_type_id=client_type.id,
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Company(
                name='Minera Los Andes SpA',
                trigram='MLA',
                phone='+56223456789',
                website='https://mineralosandes.cl',
                main_address='Av. Apoquindo 4567',
                city_id=las_condes.id if las_condes else None,
                company_type_id=client_type.id,
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Company(
                name='Retail Chile S.A.',
                trigram='RCH',
                phone='+56234567890',
                website='https://retailchile.cl',
                main_address='Av. Kennedy 5678',
                city_id=vitacura.id if vitacura else None,
                company_type_id=client_type.id,
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Company(
                name='Industrias Metálicas del Sur',
                trigram='IMS',
                phone='+56412234567',
                website='https://ims.cl',
                main_address='Camino a Lirquén 123',
                city_id=concepcion.id if concepcion else None,
                company_type_id=client_type.id,
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Company(
                name='Servicios Portuarios Valparaíso',
                trigram='SPV',
                phone='+56322345678',
                website='https://spv.cl',
                main_address='Errázuriz 890',
                city_id=valparaiso.id if valparaiso else None,
                company_type_id=client_type.id,
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
        ]
        
        db.add_all(clients)
        db.commit()
        print(f"✅ OK - {len(clients)} clientes insertados")
        
        for client in clients:
            print(f"  - {client.name} ({client.trigram})")
    else:
        print(f"✅ OK - Ya existen {existing_clients} clientes")

    print(f"\n=== Insertando Empresas Proveedores ===")
    existing_suppliers = db.query(Company).filter(Company.company_type_id == supplier_type.id).count()
    
    if existing_suppliers == 0:
        suppliers = [
            Company(
                name='Steel Import China Ltd.',
                trigram='SIC',
                phone='+862112345678',
                website='https://steelimport.cn',
                main_address='Shanghai Business District, Building A',
                company_type_id=supplier_type.id,
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Company(
                name='Fasteners Taiwan Co.',
                trigram='FTC',
                phone='+886223456789',
                website='https://fastenerstaiwan.com',
                main_address='Taipei Industrial Park, Zone 3',
                company_type_id=supplier_type.id,
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Company(
                name='Materiales Industriales SpA',
                trigram='MIS',
                phone='+56228765431',
                website='https://materialesindustriales.cl',
                main_address='Américo Vespucio 2345',
                city_id=santiago.id if santiago else None,
                company_type_id=supplier_type.id,
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Company(
                name='Herramientas Pro Sur Ltda.',
                trigram='HPS',
                phone='+56998765432',
                website='https://herramientasprosur.cl',
                main_address='Av. Argentina 1234',
                city_id=valparaiso.id if valparaiso else None,
                company_type_id=supplier_type.id,
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Company(
                name='Componentes Electrónicos Andes',
                trigram='CEA',
                phone='+56234567891',
                website='https://componentesandes.cl',
                main_address='Av. Las Condes 6789',
                city_id=las_condes.id if las_condes else None,
                company_type_id=supplier_type.id,
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
        ]
        
        db.add_all(suppliers)
        db.commit()
        print(f"✅ OK - {len(suppliers)} proveedores insertados")
        
        for supplier in suppliers:
            print(f"  - {supplier.name} ({supplier.trigram})")
    else:
        print(f"✅ OK - Ya existen {existing_suppliers} proveedores")

    print(f"\n=== Insertando Empresas Mixtas (Cliente/Proveedor) ===")
    existing_both = db.query(Company).filter(Company.company_type_id == both_type.id).count()
    
    if existing_both == 0:
        both_companies = [
            Company(
                name='Distribuidora Nacional SpA',
                trigram='DNS',
                phone='+56221234567',
                website='https://distribuidoranacional.cl',
                main_address='Av. Matta 3456',
                city_id=santiago.id if santiago else None,
                company_type_id=both_type.id,
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Company(
                name='Soluciones Integradas Ltda.',
                trigram='SIL',
                phone='+56987654321',
                website='https://solucionesintegradas.cl',
                main_address='Av. Vitacura 1234',
                city_id=vitacura.id if vitacura else None,
                company_type_id=both_type.id,
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
        ]
        
        db.add_all(both_companies)
        db.commit()
        print(f"✅ OK - {len(both_companies)} empresas mixtas insertadas")
        
        for company in both_companies:
            print(f"  - {company.name} ({company.trigram})")
    else:
        print(f"✅ OK - Ya existen {existing_both} empresas mixtas")

    # Resumen final
    print(f"\n=== Resumen de Empresas ===")
    total_clients = db.query(Company).filter(Company.company_type_id == client_type.id).count()
    total_suppliers = db.query(Company).filter(Company.company_type_id == supplier_type.id).count()
    total_both = db.query(Company).filter(Company.company_type_id == both_type.id).count()
    total_companies = db.query(Company).count()
    
    print(f"Clientes: {total_clients}")
    print(f"Proveedores: {total_suppliers}")
    print(f"Mixtas: {total_both}")
    print(f"Total empresas: {total_companies}")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n✅ OK - Proceso completado")
