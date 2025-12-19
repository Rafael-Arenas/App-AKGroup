"""
Script para insertar datos base de Lookups (Monedas, Incoterms, Estados, etc.).
"""

import sys
import os

# Add src to path to ensure imports work if run from seeds/ dir or root
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.models.lookups.lookups import (
    Currency, Incoterm, QuoteStatus, OrderStatus, PaymentStatus,
    FamilyType, Matter, SalesType
)

# Crear engine y sesión
# Asumimos que se ejecuta desde la raíz del proyecto o que la DB está en la raíz
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app_akgroup.db')
engine = create_engine(f'sqlite:///{db_path}', echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def get_or_create(model, **kwargs):
    # Separa los defaults de los filtros de búsqueda
    defaults = kwargs.pop('defaults', {})
    
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    
    # Combina filtros y defaults para crear
    params = {**kwargs, **defaults}
    instance = model(**params)
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance

try:
    print("\n=== Insertando Monedas (Currencies) ===")
    currencies = [
        {"code": "CLP", "name": "Peso Chileno", "symbol": "$", "is_active": True},
        {"code": "USD", "name": "Dólar Estadounidense", "symbol": "US$", "is_active": True},
        {"code": "EUR", "name": "Euro", "symbol": "€", "is_active": True},
    ]
    for c in currencies:
        # Usamos code como criterio de búsqueda único
        get_or_create(Currency, code=c["code"], defaults=c)
        print(f"✅ {c['code']}")

    print("\n=== Insertando Incoterms ===")
    incoterms = [
        {"code": "EXW", "name": "Ex Works", "description": "En fábrica", "is_active": True},
        {"code": "FOB", "name": "Free On Board", "description": "Libre a bordo", "is_active": True},
        {"code": "CIF", "name": "Cost, Insurance and Freight", "description": "Costo, seguro y flete", "is_active": True},
        {"code": "DDP", "name": "Delivered Duty Paid", "description": "Entregado derechos pagados", "is_active": True},
    ]
    for i in incoterms:
        get_or_create(Incoterm, code=i["code"], defaults=i)
        print(f"✅ {i['code']}")

    print("\n=== Insertando Estados de Cotización (QuoteStatus) ===")
    q_statuses = [
        {"code": "draft", "name": "Borrador", "description": "Cotización en preparación"},
        {"code": "sent", "name": "Enviada", "description": "Enviada al cliente"},
        {"code": "accepted", "name": "Aceptada", "description": "Aceptada por el cliente"},
        {"code": "rejected", "name": "Rechazada", "description": "Rechazada por el cliente"},
        {"code": "expired", "name": "Vencida", "description": "Plazo de validez expirado"},
    ]
    for s in q_statuses:
        get_or_create(QuoteStatus, code=s["code"], defaults=s)
        print(f"✅ {s['name']}")

    print("\n=== Insertando Estados de Orden (OrderStatus) ===")
    o_statuses = [
        {"code": "pending", "name": "Pendiente", "description": "Orden recibida"},
        {"code": "confirmed", "name": "Confirmada", "description": "Confirmada internamente"},
        {"code": "shipped", "name": "Enviada", "description": "Productos despachados"},
        {"code": "delivered", "name": "Entregada", "description": "Recibida por cliente"},
        {"code": "cancelled", "name": "Cancelada", "description": "Orden anulada"},
    ]
    for s in o_statuses:
        get_or_create(OrderStatus, code=s["code"], defaults=s)
        print(f"✅ {s['name']}")
    
    print("\n=== Insertando Estados de Pago (PaymentStatus) ===")
    p_statuses = [
        {"code": "pending", "name": "Pendiente", "description": "Pago no recibido"},
        {"code": "partial", "name": "Parcial", "description": "Pago parcial recibido"},
        {"code": "paid", "name": "Pagado", "description": "Totalmente pagado"},
        {"code": "overdue", "name": "Vencido", "description": "Plazo de pago expirado"},
    ]
    for s in p_statuses:
        get_or_create(PaymentStatus, code=s["code"], defaults=s)
        print(f"✅ {s['name']}")

    print("\n=== Insertando Otros Lookups ===")
    # Family Types
    families = ["Mecánico", "Eléctrico", "Hidráulico", "Neumático", "Estructural"]
    for f in families:
        get_or_create(FamilyType, name=f)
    
    # Matters
    matters = ["Acero Inoxidable", "Acero Carbono", "Aluminio", "Bronce", "Polímero"]
    for m in matters:
        get_or_create(Matter, name=m)

    # Sales Types
    sales = ["Venta Nacional", "Exportación", "Servicios"]
    for s in sales:
        get_or_create(SalesType, name=s)
    
    print("✅ Otros lookups creados")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n✅ Proceso completado exitosamente")
