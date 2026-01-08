"""
Script para insertar tipos de pago (PaymentType).

Crea tipos de pago estándar: 15, 30, 60, 90 días, contado, etc.
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.models.lookups.business import PaymentType

# Crear engine y sesión
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app_akgroup.db')
engine = create_engine(f'sqlite:///{db_path}', echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def get_or_create(model, **kwargs):
    """Get or create instance."""
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
    print("\n=== Insertando Tipos de Pago (PaymentType) ===")
    
    payment_types = [
        {
            "code": "CASH",
            "name": "Contado",
            "days": 0,
            "description": "Pago inmediato al contado",
            "is_active": True
        },
        {
            "code": "15D",
            "name": "15 días",
            "days": 15,
            "description": "Pago a 15 días desde la fecha de factura",
            "is_active": True
        },
        {
            "code": "30D",
            "name": "30 días",
            "days": 30,
            "description": "Pago a 30 días desde la fecha de factura",
            "is_active": True
        },
        {
            "code": "45D",
            "name": "45 días",
            "days": 45,
            "description": "Pago a 45 días desde la fecha de factura",
            "is_active": True
        },
        {
            "code": "60D",
            "name": "60 días",
            "days": 60,
            "description": "Pago a 60 días desde la fecha de factura",
            "is_active": True
        },
        {
            "code": "90D",
            "name": "90 días",
            "days": 90,
            "description": "Pago a 90 días desde la fecha de factura",
            "is_active": True
        },
        {
            "code": "120D",
            "name": "120 días",
            "days": 120,
            "description": "Pago a 120 días desde la fecha de factura",
            "is_active": True
        },
    ]
    
    for pt in payment_types:
        get_or_create(PaymentType, code=pt["code"], defaults=pt)
        print(f"✅ {pt['code']} - {pt['name']} ({pt['days']} días)")
    
    print(f"\n✅ Total: {len(payment_types)} tipos de pago insertados")
    print("✅ Seed de tipos de pago completado exitosamente")

except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
    raise
finally:
    db.close()
