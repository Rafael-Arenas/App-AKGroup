"""
Script para insertar usuarios (Staff) de ejemplo en la base de datos.
"""

import sys
import os

# Add src to path to ensure imports work if run from seeds/ dir or root
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.models.core.staff import Staff

# Crear engine y sesión
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app_akgroup.db')
engine = create_engine(f'sqlite:///{db_path}', echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def get_or_create_staff(username, email, **kwargs):
    staff = db.query(Staff).filter((Staff.username == username) | (Staff.email == email)).first()
    if staff:
        return staff
    
    staff = Staff(username=username, email=email, **kwargs)
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff

try:
    print("\n=== Insertando Staff (Usuarios) ===")
    
    users = [
        {
            "username": "admin",
            "email": "admin@akgroup.cl",
            "first_name": "Admin",
            "last_name": "System",
            "trigram": "ADM",
            "position": "Administrador del Sistema",
            "is_admin": True,
            "is_active": True
        },
        {
            "username": "jperez",
            "email": "juan.perez@akgroup.cl",
            "first_name": "Juan",
            "last_name": "Perez",
            "trigram": "JPE",
            "position": "Ejecutivo de Ventas",
            "is_admin": False,
            "is_active": True
        },
        {
            "username": "mlopez",
            "email": "maria.lopez@akgroup.cl",
            "first_name": "Maria",
            "last_name": "Lopez",
            "trigram": "MLO",
            "position": "Gerente Comercial",
            "is_admin": False,
            "is_active": True
        }
    ]

    for user_data in users:
        staff = get_or_create_staff(**user_data)
        print(f"✅ Staff: {staff.full_name} ({staff.username}) - ID: {staff.id}")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n✅ Proceso completado exitosamente")
