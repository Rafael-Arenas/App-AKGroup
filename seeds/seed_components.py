"""
Script para crear componentes de los kits (BOM).
"""

from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.models.core.products import Product, ProductComponent

# Crear engine y sesión
engine = create_engine('sqlite:///app_akgroup.db', echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    print("=== Creando Componentes de Kits ===")
    
    # Obtener productos necesarios
    tor_m6 = db.query(Product).filter(Product.reference == 'TOR-001').first()
    ara_m6 = db.query(Product).filter(Product.reference == 'AR-002').first()
    tuerca_m6 = db.query(Product).filter(Product.reference == 'TOR-005').first()
    tor_m4 = db.query(Product).filter(Product.reference == 'TOR-006').first()
    
    kit_m6 = db.query(Product).filter(Product.reference == 'KIT-005').first()
    kit_elec = db.query(Product).filter(Product.reference == 'KIT-006').first()
    kit_elec_inst = db.query(Product).filter(Product.reference == 'KIT-007').first()
    
    # Verificar si ya existen componentes
    existing_components = db.query(ProductComponent).count()
    if existing_components > 0:
        print(f"✅ OK - Ya existen {existing_components} componentes")
        components = db.query(ProductComponent).all()
        for comp in components:
            parent = db.query(Product).filter(Product.id == comp.parent_id).first()
            component = db.query(Product).filter(Product.id == comp.component_id).first()
            if parent and component:
                print(f"  - {parent.reference} -> {component.reference} x{comp.quantity}")
    else:
        # Componentes para Kit M6 Completo (KIT-005)
        if kit_m6 and tor_m6 and ara_m6 and tuerca_m6:
            components_m6 = [
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
            db.add_all(components_m6)
            print(f"✅ OK - {len(components_m6)} componentes para Kit M6 creados")
        
        # Componentes para Kit Electrónico (KIT-006)
        if kit_elec and tor_m4:
            # Obtener componentes electrónicos
            res_1k = db.query(Product).filter(Product.reference == 'ELEC-001').first()
            led_red = db.query(Product).filter(Product.reference == 'ELEC-002').first()
            
            if res_1k and led_red:
                components_elec = [
                    ProductComponent(
                        parent_id=kit_elec.id,
                        component_id=res_1k.id,
                        quantity=Decimal('50.000'),
                        created_by_id=1,
                        updated_by_id=1
                    ),
                    ProductComponent(
                        parent_id=kit_elec.id,
                        component_id=led_red.id,
                        quantity=Decimal('20.000'),
                        created_by_id=1,
                        updated_by_id=1
                    ),
                    ProductComponent(
                        parent_id=kit_elec.id,
                        component_id=tor_m4.id,
                        quantity=Decimal('100.000'),
                        created_by_id=1,
                        updated_by_id=1
                    ),
                ]
                db.add_all(components_elec)
                print(f"✅ OK - {len(components_elec)} componentes para Kit Electrónico creados")
        
        # Componentes para Kit Instalación Eléctrica (KIT-007)
        if kit_elec_inst:
            # Obtener componentes eléctricos
            cable_25 = db.query(Product).filter(Product.reference == 'PLAS-002').first()
            tubo_pvc = db.query(Product).filter(Product.reference == 'PLAS-001').first()
            
            if cable_25 and tubo_pvc:
                components_inst = [
                    ProductComponent(
                        parent_id=kit_elec_inst.id,
                        component_id=cable_25.id,
                        quantity=Decimal('10.000'),
                        created_by_id=1,
                        updated_by_id=1
                    ),
                    ProductComponent(
                        parent_id=kit_elec_inst.id,
                        component_id=tubo_pvc.id,
                        quantity=Decimal('5.000'),
                        created_by_id=1,
                        updated_by_id=1
                    ),
                ]
                db.add_all(components_inst)
                print(f"✅ OK - {len(components_inst)} componentes para Kit Instalación creados")
        
        db.commit()
        
        # Mostrar todos los componentes creados
        print("\n=== Componentes Creados ===")
        all_components = db.query(ProductComponent).all()
        for comp in all_components:
            parent = db.query(Product).filter(Product.id == comp.parent_id).first()
            component = db.query(Product).filter(Product.id == comp.component_id).first()
            if parent and component:
                print(f"  - {parent.reference} -> {component.reference} x{comp.quantity}")

    # Resumen final
    print(f"\n=== Resumen ===")
    total_components = db.query(ProductComponent).count()
    total_products = db.query(Product).count()
    total_kits = db.query(Product).filter(Product.product_type == 'NOMENCLATURE').count()
    
    print(f"Total productos: {total_products}")
    print(f"Total kits/nomenclaturas: {total_kits}")
    print(f"Total componentes: {total_components}")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n✅ OK - Proceso completado")
