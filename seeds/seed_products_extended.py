"""
Script para insertar más artículos y nomenclaturas en la base de datos.
"""

from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.models.core.products import Product, ProductType, ProductComponent
from src.backend.models.lookups.lookups import FamilyType, Matter, SalesType

# Crear engine y sesión
engine = create_engine('sqlite:///app_akgroup.db', echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Obtener datos base
    family_metal = db.query(FamilyType).filter(FamilyType.name == 'Herramientas').first()
    family_material = db.query(FamilyType).filter(FamilyType.name == 'Materiales').first()
    family_electronic = db.query(FamilyType).filter(FamilyType.name == 'Componentes').first()
    
    matter_metal = db.query(Matter).filter(Matter.name == 'Metal').first()
    matter_plastic = db.query(Matter).filter(Matter.name == 'Plástico').first()
    matter_electronic = db.query(Matter).filter(Matter.name == 'Electrónico').first()
    
    sales_direct = db.query(SalesType).filter(SalesType.name == 'Venta Directa').first()
    sales_distribution = db.query(SalesType).filter(SalesType.name == 'Distribución').first()

    print(f"\n=== Insertando Más Artículos ===")
    existing_articles = db.query(Product).filter(Product.product_type == ProductType.ARTICLE).count()
    
    if existing_articles <= 4:  # Solo los 4 iniciales existen
        articles = [
            # Tornillería adicional
            Product(
                product_type=ProductType.ARTICLE,
                reference='TOR-005',
                designation_es='Tuerca Hexagonal M6',
                designation_en='Hex Nut M6',
                short_designation='Tuerca M6',
                revision='B',
                family_type_id=family_metal.id if family_metal else None,
                matter_id=matter_metal.id if matter_metal else None,
                sales_type_id=sales_direct.id if sales_direct else None,
                purchase_price=Decimal('30.00'),
                cost_price=Decimal('45.00'),
                sale_price=Decimal('85.00'),
                stock_quantity=Decimal('2000.000'),
                minimum_stock=Decimal('300.000'),
                net_weight=Decimal('0.015'),
                gross_weight=Decimal('0.018'),
                hs_code='7318.16.00',
                country_of_origin='TAIWAN',
                supplier_reference='NUT-M6-TW',
                customs_number='TW2024-002345',
                image_url='https://example.com/images/tuerca-m6.jpg',
                plan_url='https://example.com/plans/tuerca-m6.pdf',
                notes='Tuerca de acero inoxidable calidad 304',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Product(
                product_type=ProductType.ARTICLE,
                reference='TOR-006',
                designation_es='Tornillo Phillips M4x15',
                designation_en='Phillips Screw M4x15',
                short_designation='Tornillo M4',
                revision='A',
                family_type_id=family_metal.id if family_metal else None,
                matter_id=matter_metal.id if matter_metal else None,
                sales_type_id=sales_direct.id if sales_direct else None,
                purchase_price=Decimal('25.00'),
                cost_price=Decimal('35.00'),
                sale_price=Decimal('65.00'),
                stock_quantity=Decimal('3000.000'),
                minimum_stock=Decimal('400.000'),
                net_weight=Decimal('0.008'),
                gross_weight=Decimal('0.010'),
                hs_code='7318.15.00',
                country_of_origin='CHINA',
                supplier_reference='TOR-PH-M4-CN',
                customs_number='CN2024-003456',
                image_url='https://example.com/images/tornillo-ph-m4.jpg',
                plan_url='https://example.com/plans/tornillo-ph-m4.pdf',
                notes='Tornillo cabeza Phillips acero zincado',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            # Componentes electrónicos
            Product(
                product_type=ProductType.ARTICLE,
                reference='ELEC-001',
                designation_es='Resistencia 1K Ohm 1/4W',
                designation_en='Resistor 1K Ohm 1/4W',
                short_designation='Resistencia 1K',
                revision='C',
                family_type_id=family_electronic.id if family_electronic else None,
                matter_id=matter_electronic.id if matter_electronic else None,
                sales_type_id=sales_distribution.id if sales_distribution else None,
                purchase_price=Decimal('5.00'),
                cost_price=Decimal('8.00'),
                sale_price=Decimal('15.00'),
                stock_quantity=Decimal('5000.000'),
                minimum_stock=Decimal('1000.000'),
                net_weight=Decimal('0.001'),
                gross_weight=Decimal('0.002'),
                hs_code='8542.31.00',
                country_of_origin='MALAYSIA',
                supplier_reference='RES-1K-251-MY',
                customs_number='MY2024-004567',
                image_url='https://example.com/images/resistencia-1k.jpg',
                plan_url='https://example.com/plans/resistencia-1k.pdf',
                notes='Resistencia carbón 5% tolerancia',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Product(
                product_type=ProductType.ARTICLE,
                reference='ELEC-002',
                designation_es='LED Rojo 5mm',
                designation_en='Red LED 5mm',
                short_designation='LED Rojo 5mm',
                revision='A',
                family_type_id=family_electronic.id if family_electronic else None,
                matter_id=matter_electronic.id if matter_electronic else None,
                sales_type_id=sales_distribution.id if sales_distribution else None,
                purchase_price=Decimal('12.00'),
                cost_price=Decimal('18.00'),
                sale_price=Decimal('32.00'),
                stock_quantity=Decimal('2000.000'),
                minimum_stock=Decimal('500.000'),
                net_weight=Decimal('0.002'),
                gross_weight=Decimal('0.003'),
                hs_code='8541.41.00',
                country_of_origin='SINGAPORE',
                supplier_reference='LED-RED-5MM-SG',
                customs_number='SG2024-005678',
                image_url='https://example.com/images/led-rojo-5mm.jpg',
                plan_url='https://example.com/plans/led-rojo-5mm.pdf',
                notes='LED difuso 20mA 2V',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            # Materiales plásticos
            Product(
                product_type=ProductType.ARTICLE,
                reference='PLAS-001',
                designation_es='Tubo PVC 1/2" 3m',
                designation_en='PVC Pipe 1/2" 3m',
                short_designation='Tubo PVC 1/2',
                revision='B',
                family_type_id=family_material.id if family_material else None,
                matter_id=matter_plastic.id if matter_plastic else None,
                sales_type_id=sales_direct.id if sales_direct else None,
                purchase_price=Decimal('850.00'),
                cost_price=Decimal('1200.00'),
                sale_price=Decimal('1850.00'),
                stock_quantity=Decimal('150.000'),
                minimum_stock=Decimal('30.000'),
                net_weight=Decimal('1.200'),
                gross_weight=Decimal('1.350'),
                length=Decimal('3000.00'),
                hs_code='3917.21.00',
                country_of_origin='CHILE',
                supplier_reference='TUBO-PVC-12-CL',
                customs_number='CL2024-006789',
                image_url='https://example.com/images/tubo-pvc-12.jpg',
                plan_url='https://example.com/plans/tubo-pvc-12.pdf',
                notes='Tubo PVC Schedule 40 agua potable',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Product(
                product_type=ProductType.ARTICLE,
                reference='PLAS-002',
                designation_es='Cable Eléctrico 2.5mm',
                designation_en='Electric Cable 2.5mm',
                short_designation='Cable 2.5mm',
                revision='A',
                family_type_id=family_material.id if family_material else None,
                matter_id=matter_plastic.id if matter_plastic else None,
                sales_type_id=sales_direct.id if sales_direct else None,
                purchase_price=Decimal('450.00'),
                cost_price=Decimal('650.00'),
                sale_price=Decimal('950.00'),
                stock_quantity=Decimal('200.000'),
                minimum_stock=Decimal('50.000'),
                net_weight=Decimal('0.800'),
                gross_weight=Decimal('0.900'),
                hs_code='8544.42.00',
                country_of_origin='ARGENTINA',
                supplier_reference='CABLE-25-AR',
                customs_number='AR2024-007890',
                image_url='https://example.com/images/cable-25mm.jpg',
                plan_url='https://example.com/plans/cable-25mm.pdf',
                notes='Cable unipolar THHN 750V',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
        ]
        
        db.add_all(articles)
        db.commit()
        print(f"✅ OK - {len(articles)} artículos insertados")
        
        for article in articles:
            print(f"  - {article.reference}: {article.designation_es}")
    else:
        print(f"✅ OK - Ya existen {existing_articles} artículos")

    print(f"\n=== Insertando Nomenclaturas (Kits/BOM) ===")
    existing_nomenclatures = db.query(Product).filter(Product.product_type == ProductType.NOMENCLATURE).count()
    
    if existing_nomenclatures <= 1:  # Solo el inicial existe
        # Obtener artículos para usar en kits
        tor_m6 = db.query(Product).filter(Product.reference == 'TOR-001').first()
        ara_m6 = db.query(Product).filter(Product.reference == 'AR-002').first()
        tuerca_m6 = db.query(Product).filter(Product.reference == 'TOR-005').first()
        tor_m4 = db.query(Product).filter(Product.reference == 'TOR-006').first()
        
        nomenclatures = [
            Product(
                product_type=ProductType.NOMENCLATURE,
                reference='KIT-005',
                designation_es='Kit Fijación M6 Completo',
                designation_en='M6 Complete Fastening Kit',
                short_designation='Kit M6 Completo',
                revision='2.0',
                family_type_id=family_metal.id if family_metal else None,
                matter_id=matter_metal.id if matter_metal else None,
                sales_type_id=sales_direct.id if sales_direct else None,
                cost_price=Decimal('180.00'),
                sale_price=Decimal('320.00'),
                hs_code='7318.00.00',
                country_of_origin='CHILE',
                supplier_reference='KIT-M6-COMP-CL',
                customs_number='CL2024-008901',
                image_url='https://example.com/images/kit-m6-completo.jpg',
                plan_url='https://example.com/plans/kit-m6-completo.pdf',
                notes='Kit completo con tornillos, arandelas y tuercas M6 (20 unidades)',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Product(
                product_type=ProductType.NOMENCLATURE,
                reference='KIT-006',
                designation_es='Kit Montaje Electrónico Básico',
                designation_en='Basic Electronics Assembly Kit',
                short_designation='Kit Electrónico',
                revision='1.1',
                family_type_id=family_electronic.id if family_electronic else None,
                matter_id=matter_electronic.id if matter_electronic else None,
                sales_type_id=sales_distribution.id if sales_distribution else None,
                cost_price=Decimal('250.00'),
                sale_price=Decimal('450.00'),
                hs_code='8543.70.00',
                country_of_origin='CHILE',
                supplier_reference='KIT-ELEC-BASIC-CL',
                customs_number='CL2024-009012',
                image_url='https://example.com/images/kit-electronico.jpg',
                plan_url='https://example.com/plans/kit-electronico.pdf',
                notes='Kit básico con resistencias, LEDs y tornillería para montaje',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Product(
                product_type=ProductType.NOMENCLATURE,
                reference='KIT-007',
                designation_es='Kit Instalación Eléctrica',
                designation_en='Electrical Installation Kit',
                short_designation='Kit Eléctrico',
                revision='1.0',
                family_type_id=family_material.id if family_material else None,
                matter_id=matter_plastic.id if matter_plastic else None,
                sales_type_id=sales_direct.id if sales_direct else None,
                cost_price=Decimal('3500.00'),
                sale_price=Decimal('5800.00'),
                hs_code='8544.49.00',
                country_of_origin='CHILE',
                supplier_reference='KIT-ELEC-INST-CL',
                customs_number='CL2024-010123',
                image_url='https://example.com/images/kit-instalacion.jpg',
                plan_url='https://example.com/plans/kit-instalacion.pdf',
                notes='Kit completo para instalaciones eléctricas residenciales',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
        ]
        
        db.add_all(nomenclatures)
        db.commit()
        
        # Crear componentes para los kits
        if tor_m6 and ara_m6 and tuerca_m6:
            # Kit M6 Completo
            kit_m6 = db.query(Product).filter(Product.reference == 'KIT-005').first()
            if kit_m6:
                components = [
                    ProductComponent(
                        parent_id=kit_m6.id,
                        component_id=tor_m6.id,
                        quantity=Decimal('20.000'),
                        created_by_id=1,
                        updated_by_id=1
                    ),
                    ProductComponent(
                        parent_id=kit_m6.id,
                        component_id=ara_m6.id,
                        quantity=Decimal('20.000'),
                        created_by_id=1,
                        updated_by_id=1
                    ),
                    ProductComponent(
                        parent_id=kit_m6.id,
                        component_id=tuerca_m6.id,
                        quantity=Decimal('20.000'),
                        created_by_id=1,
                        updated_by_id=1
                    ),
                ]
                db.add_all(components)
                db.commit()
                print(f"✅ OK - {len(components)} componentes agregados al Kit M6")
        
        # Agregar más servicios
        services = [
            Product(
                product_type=ProductType.SERVICE,
                reference='SER-005',
                designation_es='Servicio de Corte Laser',
                designation_en='Laser Cutting Service',
                short_designation='Corte Laser',
                revision='A',
                family_type_id=family_metal.id if family_metal else None,
                sales_type_id=sales_direct.id if sales_direct else None,
                cost_price=Decimal('2500.00'),
                sale_price=Decimal('4500.00'),
                supplier_reference='SVC-LASER-01',
                image_url='https://example.com/images/servicio-corte-laser.jpg',
                notes='Servicio de corte laser para metales y plásticos',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
            Product(
                product_type=ProductType.SERVICE,
                reference='SER-006',
                designation_es='Servicio de Impresión 3D',
                designation_en='3D Printing Service',
                short_designation='Impresión 3D',
                revision='B',
                family_type_id=family_material.id if family_material else None,
                sales_type_id=sales_direct.id if sales_direct else None,
                cost_price=Decimal('800.00'),
                sale_price=Decimal('1500.00'),
                supplier_reference='SVC-3DPRINT-01',
                image_url='https://example.com/images/servicio-impresion-3d.jpg',
                notes='Servicio de impresión 3D FDM y SLA',
                created_by_id=1,
                updated_by_id=1,
                is_active=True
            ),
        ]
        
        db.add_all(services)
        db.commit()
        print(f"✅ OK - {len(nomenclatures)} nomenclaturas y {len(services)} servicios insertados")
        
        for nomenclature in nomenclatures:
            print(f"  - {nomenclature.reference}: {nomenclature.designation_es}")
        
        for service in services:
            print(f"  - {service.reference}: {service.designation_es}")
    else:
        print(f"✅ OK - Ya existen {existing_nomenclatures} nomenclaturas")

    # Resumen final
    print(f"\n=== Resumen de Productos ===")
    total_articles = db.query(Product).filter(Product.product_type == ProductType.ARTICLE).count()
    total_nomenclatures = db.query(Product).filter(Product.product_type == ProductType.NOMENCLATURE).count()
    total_services = db.query(Product).filter(Product.product_type == ProductType.SERVICE).count()
    total_products = db.query(Product).count()
    total_components = db.query(ProductComponent).count()
    
    print(f"Artículos: {total_articles}")
    print(f"Nomenclaturas: {total_nomenclatures}")
    print(f"Servicios: {total_services}")
    print(f"Total productos: {total_products}")
    print(f"Componentes de kits: {total_components}")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n✅ OK - Proceso completado")
