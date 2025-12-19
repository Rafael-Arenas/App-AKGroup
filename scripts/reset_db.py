"""
Script para reinicializar la base de datos completamente.
Borra la DB existente, aplica migraciones y ejecuta todos los seeds.
"""
import os
import sys
import subprocess
from pathlib import Path

# Configuración
PROJECT_ROOT = Path(__file__).parent.parent
DB_FILE = PROJECT_ROOT / "app_akgroup.db"

def run_command(cmd, cwd=PROJECT_ROOT):
    print(f"\n> Ejecutando: {cmd}")
    # En Windows con Poetry, usamos shell=True para comandos compuestos o directos
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Error al ejecutar: {cmd}")
        sys.exit(1)

def main():
    print("=== REINICIALIZANDO BASE DE DATOS AK GROUP ===")
    
    # 1. Borrar base de datos existente
    if DB_FILE.exists():
        print(f"\nDeleting existing database: {DB_FILE}")
        try:
            os.remove(DB_FILE)
            print("✅ Database deleted")
        except Exception as e:
            print(f"❌ Error deleting database: {e}")
            sys.exit(1)
    else:
        print(f"\nDatabase file {DB_FILE} does not exist, clean start.")

    # 2. Ejecutar Migraciones (Crear tablas)
    print("\n--- Running Migrations ---")
    run_command("poetry run alembic upgrade head")

    # 3. Ejecutar Seeds (Poblar datos)
    print("\n--- Running Seeds ---")
    seeds = [
        "seeds/seed_lookups.py",       # Monedas, Estados, etc.
        "seeds/seed_countries.py",     # Países
        "seeds/seed_chile_cities.py",  # Ciudades
        "seeds/seed_data.py",          # Empresas base
        "seeds/seed_staff.py",         # Usuarios
        "seeds/seed_company_details.py", # RUTs, Contactos, Plantas
        "seeds/seed_products.py",      # Productos
        "seeds/seed_products_extended.py", # Más productos
        "seeds/seed_components.py"     # Componentes
    ]

    for seed in seeds:
        print(f"\nRunning seed: {seed}")
        run_command(f"poetry run python {seed}")

    print("\n\n✅✅✅ BASE DE DATOS REINICIALIZADA Y POBLADA CON ÉXITO ✅✅✅")
    print("Ya puedes ejecutar la aplicación.")

if __name__ == "__main__":
    main()
