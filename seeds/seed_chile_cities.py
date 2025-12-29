"""
Script para insertar ciudades chilenas en la base de datos.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.models.lookups import City, Country

# Crear engine y sesión
engine = create_engine('sqlite:///app_akgroup.db', echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Verificar que Chile existe
    chile = db.query(Country).filter(Country.iso_code_alpha2 == 'CL').first()
    if not chile:
        print("❌ Chile no encontrado en la base de datos. Ejecuta seed_countries.py primero.")
        exit(1)

    print(f"\n=== Insertando Ciudades de Chile ===")
    existing_cities = db.query(City).filter(City.country_id == chile.id).count()
    
    if existing_cities == 0:
        cities = [
            # Región Metropolitana
            City(name='Santiago', country_id=chile.id),
            City(name='Providencia', country_id=chile.id),
            City(name='Las Condes', country_id=chile.id),
            City(name='Vitacura', country_id=chile.id),
            City(name='La Reina', country_id=chile.id),
            City(name='Puente Alto', country_id=chile.id),
            City(name='Maipú', country_id=chile.id),
            City(name='San Bernardo', country_id=chile.id),
            
            # Región de Valparaíso
            City(name='Valparaíso', country_id=chile.id),
            City(name='Viña del Mar', country_id=chile.id),
            City(name='Quilpué', country_id=chile.id),
            City(name='Villa Alemana', country_id=chile.id),
            City(name='Quillota', country_id=chile.id),
            
            # Región del Biobío
            City(name='Concepción', country_id=chile.id),
            City(name='Talcahuano', country_id=chile.id),
            City(name='Chillán', country_id=chile.id),
            City(name='Los Ángeles', country_id=chile.id),
            
            # Región de Antofagasta
            City(name='Antofagasta', country_id=chile.id),
            City(name='Calama', country_id=chile.id),
            City(name='Tocopilla', country_id=chile.id),
            
            # Región del Maule
            City(name='Talca', country_id=chile.id),
            City(name='Curicó', country_id=chile.id),
            City(name='Linares', country_id=chile.id),
            
            # Región de la Araucanía
            City(name='Temuco', country_id=chile.id),
            City(name='Angol', country_id=chile.id),
            City(name='Villarrica', country_id=chile.id),
            
            # Región de Los Lagos
            City(name='Puerto Montt', country_id=chile.id),
            City(name='Puerto Varas', country_id=chile.id),
            City(name='Osorno', country_id=chile.id),
            City(name='Castro', country_id=chile.id),
            
            # Región de Coquimbo
            City(name='La Serena', country_id=chile.id),
            City(name='Coquimbo', country_id=chile.id),
            City(name='Ovalle', country_id=chile.id),
            
            # Región de Arica y Parinacota
            City(name='Arica', country_id=chile.id),
            
            # Región de Tarapacá
            City(name='Iquique', country_id=chile.id),
            
            # Región de Los Ríos
            City(name='Valdivia', country_id=chile.id),
            City(name='Río Bueno', country_id=chile.id),
            
            # Región de Aysén
            City(name='Coyhaique', country_id=chile.id),
            
            # Región de Magallanes
            City(name='Punta Arenas', country_id=chile.id),
            City(name='Puerto Natales', country_id=chile.id),
        ]
        
        db.add_all(cities)
        db.commit()
        print(f"✅ OK - {len(cities)} ciudades chilenas insertadas")
        
        # Mostrar ciudades insertadas
        print("\n=== Ciudades Insertadas ===")
        for i, city in enumerate(cities[:15], 1):  # Mostrar primeras 15
            print(f"{i:2d}. {city.name}")
        if len(cities) > 15:
            print(f"... y {len(cities) - 15} ciudades más")
            
    else:
        print(f"✅ OK - Ya existen {existing_cities} ciudades chilenas")
        cities = db.query(City).filter(City.country_id == chile.id).limit(10).all()
        print("Primeras 10 ciudades:")
        for city in cities:
            print(f"  - {city.name}")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\n✅ OK - Proceso completado")
