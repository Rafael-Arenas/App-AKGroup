"""
Script para insertar países sudamericanos en la base de datos.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.backend.models.lookups.lookups import Country

# Crear engine y sesión
engine = create_engine('sqlite:///app_akgroup.db', echo=False)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Insertar países sudamericanos
    print("\n=== Insertando Países Sudamericanos ===")
    existing_countries = db.query(Country).count()

    if existing_countries == 0:
        countries = [
            Country(name='Argentina', iso_code_alpha2='AR', iso_code_alpha3='ARG'),
            Country(name='Bolivia', iso_code_alpha2='BO', iso_code_alpha3='BOL'),
            Country(name='Brasil', iso_code_alpha2='BR', iso_code_alpha3='BRA'),
            Country(name='Chile', iso_code_alpha2='CL', iso_code_alpha3='CHL'),
            Country(name='Colombia', iso_code_alpha2='CO', iso_code_alpha3='COL'),
            Country(name='Ecuador', iso_code_alpha2='EC', iso_code_alpha3='ECU'),
            Country(name='Guyana', iso_code_alpha2='GY', iso_code_alpha3='GUY'),
            Country(name='Paraguay', iso_code_alpha2='PY', iso_code_alpha3='PRY'),
            Country(name='Perú', iso_code_alpha2='PE', iso_code_alpha3='PER'),
            Country(name='Surinam', iso_code_alpha2='SR', iso_code_alpha3='SUR'),
            Country(name='Uruguay', iso_code_alpha2='UY', iso_code_alpha3='URY'),
            Country(name='Venezuela', iso_code_alpha2='VE', iso_code_alpha3='VEN'),
        ]

        db.add_all(countries)
        db.commit()
        print(f"OK - {len(countries)} países sudamericanos insertados")

        # Mostrar países insertados
        for country in countries:
            db.refresh(country)
            print(f"  - [{country.id}] {country.name} ({country.iso_code_alpha2}/{country.iso_code_alpha3})")
    else:
        print(f"OK - Ya existen {existing_countries} países en la base de datos")
        countries = db.query(Country).all()
        for country in countries:
            print(f"  - [{country.id}] {country.name} ({country.iso_code_alpha2}/{country.iso_code_alpha3})")

    # Resumen
    print(f"\n=== Resumen ===")
    print(f"Total países: {db.query(Country).count()}")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

print("\nOK - Proceso completado")
