"""
Script para limpiar datos de negocio de la base de datos.

Borra en orden correcto respetando dependencias:
1. Facturas (invoice_sii, invoice_export)
2. Entregas (delivery_dates, delivery_orders)
3. Órdenes (order_products, orders)
4. Cotizaciones (quote_products, quotes)
5. Productos (product_components, products)
6. Clientes/Empresas (company_ruts, plants, contacts, addresses, notes, companies)
7. Secuencias (reinicia a 0)

⚠️ PRECAUCIÓN: Este script borra datos permanentemente.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from src.backend.database import engine


def clear_all_business_data():
    """Borra todos los datos de negocio en orden correcto."""
    
    # Orden de tablas a limpiar (respetando dependencias FK)
    tables_to_clear = [
        # 1. Facturas (dependen de orders, companies)
        "invoice_sii",
        "invoice_export",
        
        # 2. Entregas (dependen de orders)
        "delivery_dates",
        "delivery_orders",
        
        # 3. Órdenes (dependen de quotes, companies, products)
        "order_products",
        "orders",
        
        # 4. Cotizaciones (dependen de companies, products)
        "quote_products",
        "quotes",
        
        # 5. Productos (product_components depende de products)
        "product_components",
        "products",
        
        # 6. Empresas y relacionados
        "notes",           # depende de companies
        "contacts",        # depende de companies
        "addresses",       # depende de plants/companies
        "plants",          # depende de companies
        "company_ruts",    # depende de companies
        "companies",       # tabla principal de empresas
        
        # 7. Secuencias
        "sequences",
    ]
    
    print("=" * 60)
    print("🗑️  LIMPIEZA DE DATOS DE NEGOCIO")
    print("=" * 60)
    print()
    
    with engine.begin() as conn:
        # Desactivar verificación de FK temporalmente (SQLite)
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        
        total_deleted = 0
        
        for table in tables_to_clear:
            try:
                # Contar registros antes de borrar
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                
                if count > 0:
                    # Borrar todos los registros
                    conn.execute(text(f"DELETE FROM {table}"))
                    print(f"  ✅ {table}: {count} registros eliminados")
                    total_deleted += count
                else:
                    print(f"  ⏭️  {table}: (vacía)")
                    
            except Exception as e:
                print(f"  ⏭️  {table}: (no existe)")
        
        # Reactivar verificación de FK
        conn.execute(text("PRAGMA foreign_keys = ON"))
        
        print()
        print("-" * 60)
        print(f"📊 Total de registros eliminados: {total_deleted}")
        print("-" * 60)
    
    print()
    print("✅ Limpieza completada exitosamente.")
    print("   Las secuencias han sido reiniciadas a 0.")
    print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Limpia datos de negocio")
    parser.add_argument("--force", "-f", action="store_true", help="Ejecutar sin confirmación")
    args = parser.parse_args()
    
    if args.force:
        clear_all_business_data()
    else:
        print()
        print("⚠️  ADVERTENCIA: Este script eliminará TODOS los datos de:")
        print("   - Facturas (SII y Exportación)")
        print("   - Entregas")
        print("   - Órdenes y sus productos")
        print("   - Cotizaciones y sus productos")
        print("   - Productos y componentes")
        print("   - Empresas (clientes, proveedores, etc.)")
        print("   - Secuencias de numeración")
        print()
        
        confirm = input("¿Estás seguro de que deseas continuar? (escribe 'SI' para confirmar): ")
        
        if confirm.strip().upper() == "SI":
            clear_all_business_data()
        else:
            print("\n❌ Operación cancelada.")
