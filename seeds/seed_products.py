"""
Script para insertar productos de ejemplo en la base de datos.
"""

from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.models.core.products import Product, ProductType
from src.backend.models.lookups import FamilyType, Matter, SalesType

# Crear engine y sesión
engine = create_engine('sqlite:///app_akgroup.db', echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # 1. Verificar/insertar datos base necesarios
    print("\n=== Verificando datos base ===")
    
    # Family Types
    existing_families = db.query(FamilyType).count()
    if existing_families == 0:
        families = [
            FamilyType(name='Herramientas', description='Herramientas y equipamiento'),
            FamilyType(name='Materiales', description='Materiales de construcción'),
            FamilyType(name='Componentes', description='Componentes electrónicos'),
        ]
        db.add_all(families)
        db.commit()
        print(f"OK - {len(families)} tipos de familia creados")
    
    # Matters
    existing_matters = db.query(Matter).count()
    if existing_matters == 0:
        matters = [
            Matter(name='Metal', description='Componentes metálicos'),
            Matter(name='Plástico', description='Componentes plásticos'),
            Matter(name='Electrónico', description='Componentes electrónicos'),
        ]
        db.add_all(matters)
        db.commit()
        print(f"OK - {len(matters)} tipos de materia creados")
    
    # Sales Types
    existing_sales_types = db.query(SalesType).count()
    if existing_sales_types == 0:
        sales_types = [
            SalesType(name='Venta Directa', description='Venta directa al cliente'),
            SalesType(name='Distribución', description='Venta a través de distribuidores'),
        ]
        db.add_all(sales_types)
        db.commit()
        print(f"OK - {len(sales_types)} tipos de venta creados")

    # 2. Insertar productos de ejemplo
    print("\n=== Insertando Productos ===")
    existing_products = db.query(Product).count()
    
    if existing_products == 0:
        # Obtener IDs de datos base
        family = db.query(FamilyType).first()
        matter = db.query(Matter).first()
        sales_type = db.query(SalesType).first()
        
        products = [
            Product(
                product_type=ProductType.ARTICLE,
                reference='TOR-001',
                designation_es='Tornillo Hexagonal M6x20',
                designation_en='Hex Screw M6x20',
                short_designation='Tornillo M6',
                revision='A',
                family_type_id=family.id if family else None,
                matter_id=matter.id if matter else None,
                sales_type_id=sales_type.id if sales_type else None,
                purchase_price=Decimal('50.00'),
                cost_price=Decimal('75.00'),
                sale_price=Decimal('120.00'),
                stock_quantity=Decimal('1000.000'),
                minimum_stock=Decimal('100.000'),
                net_weight=Decimal('0.025'),
                gross_weight=Decimal('0.030'),
                length=Decimal('20.00'),
                hs_code='7318.15.00',
                country_of_origin='CHINA',
                supplier_reference='TOR-M6-20-CN',
                customs_number='CN2024-001234',
                image_url='https://example.com/images/tor-m6-20.jpg',
                plan_url='https://example.com/plans/tor-m6-20.pdf',
                notes='Tornillo de acero inoxidable calidad 304',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Product(
                product_type=ProductType.ARTICLE,
                reference='AR-002',
                designation_es='Arandela Plana M6',
                designation_en='Flat Washer M6',
                short_designation='Arandela M6',
                revision='B',
                family_type_id=family.id if family else None,
                matter_id=matter.id if matter else None,
                sales_type_id=sales_type.id if sales_type else None,
                purchase_price=Decimal('15.00'),
                cost_price=Decimal('20.00'),
                sale_price=Decimal('35.00'),
                stock_quantity=Decimal('2000.000'),
                minimum_stock=Decimal('200.000'),
                net_weight=Decimal('0.010'),
                gross_weight=Decimal('0.012'),
                hs_code='7318.21.00',
                country_of_origin='TAIWAN',
                supplier_reference='ARA-M6-TW',
                customs_number='TW2024-005678',
                image_url='https://example.com/images/ara-m6.jpg',
                plan_url='https://example.com/plans/ara-m6.pdf',
                notes='Arandela de acero al carbón',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Product(
                product_type=ProductType.NOMENCLATURE,
                reference='KIT-003',
                designation_es='Kit de Fijación Completo',
                designation_en='Complete Fastening Kit',
                short_designation='Kit Fijación',
                revision='1.0',
                family_type_id=family.id if family else None,
                matter_id=matter.id if matter else None,
                sales_type_id=sales_type.id if sales_type else None,
                cost_price=Decimal('150.00'),
                sale_price=Decimal('250.00'),
                hs_code='7318.00.00',
                country_of_origin='CHILE',
                supplier_reference='KIT-FIX-CL',
                customs_number='CL2024-009012',
                image_url='https://example.com/images/kit-fijacion.jpg',
                plan_url='https://example.com/plans/kit-fijacion.pdf',
                notes='Kit completo con tornillos, arandelas y tuercas',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Product(
                product_type=ProductType.SERVICE,
                reference='SER-004',
                designation_es='Servicio de Montaje',
                designation_en='Assembly Service',
                short_designation='Montaje',
                revision='A',
                family_type_id=family.id if family else None,
                sales_type_id=sales_type.id if sales_type else None,
                cost_price=Decimal('500.00'),
                sale_price=Decimal('800.00'),
                supplier_reference='SVC-MOUNT-01',
                image_url='https://example.com/images/servicio-montaje.jpg',
                notes='Servicio profesional de montaje de estructuras',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
        ]
        
        db.add_all(products)
        db.commit()
        
        # Refresh para obtener los IDs
        for product in products:
            db.refresh(product)
        
        print(f"OK - {len(products)} productos insertados:")
        for product in products:
            print(f"  - [{product.id}] {product.reference} - {product.designation_es}")
            print(f"    Image: {product.image_url}")
            print(f"    Plan: {product.plan_url}")
            print(f"    Supplier Ref: {product.supplier_reference}")
            print(f"    Customs: {product.customs_number}")
    else:
        print(f"OK - Ya existen {existing_products} productos")
        products = db.query(Product).limit(5).all()
        for product in products:
            print(f"  - [{product.id}] {product.reference} - {product.designation_es}")

    # 3. Resumen
    print("\n=== Resumen ===")
    print(f"Family Types: {db.query(FamilyType).count()}")
    print(f"Matters: {db.query(Matter).count()}")
    print(f"Sales Types: {db.query(SalesType).count()}")
    print(f"Products: {db.query(Product).count()}")
    
    # Verificar campos nuevos
    print("\n=== Verificación de campos nuevos ===")
    sample_product = db.query(Product).first()
    if sample_product:
        print(f"Sample Product: {sample_product.reference}")
        print(f"  image_url: {sample_product.image_url}")
        print(f"  plan_url: {sample_product.plan_url}")
        print(f"  supplier_reference: {sample_product.supplier_reference}")
        print(f"  customs_number: {sample_product.customs_number}")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\nOK - Proceso completado")
