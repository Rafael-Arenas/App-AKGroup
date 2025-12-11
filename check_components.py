from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.models.core.products import Product, ProductComponent

engine = create_engine('sqlite:///app_akgroup.db', echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Verificar productos existentes
    products = db.query(Product).all()
    print('=== Productos Existentes ===')
    for p in products:
        print(f'{p.reference}: {p.designation_es} ({p.product_type})')

    # Verificar componentes existentes
    components = db.query(ProductComponent).all()
    print(f'\n=== Componentes Existentes: {len(components)} ===')
    for comp in components:
        parent = db.query(Product).filter(Product.id == comp.parent_id).first()
        component = db.query(Product).filter(Product.id == comp.component_id).first()
        if parent and component:
            print(f'{parent.reference} -> {component.reference} x{comp.quantity}')

finally:
    db.close()
