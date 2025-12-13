#!/usr/bin/env python3
"""
Script para limpiar la base de datos de clientes, proveedores, artículos y nomenclaturas.

Este script elimina:
- Clientes (empresas tipo CLIENT)
- Proveedores (empresas tipo SUPPLIER)
- Artículos (productos tipo ARTICLE)
- Nomenclaturas (productos tipo NOMENCLATURE)

ADVERTENCIA: Este script es destructivo y eliminará datos permanentemente.
"""

import sys
from pathlib import Path
from typing import Optional

# Agregar el directorio src al path para importar los módulos del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.backend.config import get_settings
from src.backend.models.core.companies import Company, CompanyTypeEnum
from src.backend.models.core.products import Product, ProductType
from src.backend.models.lookups.lookups import CompanyType


def get_session():
    """Crear sesión de base de datos."""
    settings = get_settings()
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    return Session()


def count_records(session) -> dict:
    """Contar registros que serán eliminados."""
    counts = {}
    
    # Contar clientes
    client_type = session.query(CompanyType).filter_by(name="CLIENT").first()
    if client_type:
        counts["clientes"] = session.query(Company).filter_by(company_type_id=client_type.id).count()
    else:
        counts["clientes"] = 0
    
    # Contar proveedores
    supplier_type = session.query(CompanyType).filter_by(name="SUPPLIER").first()
    if supplier_type:
        counts["proveedores"] = session.query(Company).filter_by(company_type_id=supplier_type.id).count()
    else:
        counts["proveedores"] = 0
    
    # Contar artículos
    counts["articulos"] = session.query(Product).filter_by(product_type=ProductType.ARTICLE).count()
    
    # Contar nomenclaturas
    counts["nomenclaturas"] = session.query(Product).filter_by(product_type=ProductType.NOMENCLATURE).count()
    
    return counts


def cleanup_companies(session, company_type_name: str, type_name: str) -> int:
    """
    Eliminar empresas de un tipo específico.
    
    Args:
        session: Sesión de base de datos
        company_type_name: Nombre del tipo de empresa ("CLIENT" o "SUPPLIER")
        type_name: Nombre descriptivo para mostrar ("clientes" o "proveedores")
    
    Returns:
        Número de registros eliminados
    """
    # Obtener el tipo de empresa
    company_type = session.query(CompanyType).filter_by(name=company_type_name).first()
    if not company_type:
        print(f"⚠️  No se encontró el tipo de empresa '{company_type_name}'")
        return 0
    
    # Contar antes de eliminar
    count = session.query(Company).filter_by(company_type_id=company_type.id).count()
    
    if count == 0:
        print(f"✅ No hay {type_name} que eliminar")
        return 0
    
    print(f"🗑️  Eliminando {count} {type_name}...")
    
    # Eliminar en cascada (las tablas relacionadas se eliminarán automáticamente)
    deleted = session.query(Company).filter_by(company_type_id=company_type.id).delete(synchronize_session=False)
    session.commit()
    
    print(f"✅ {deleted} {type_name} eliminados")
    return deleted


def cleanup_products(session, product_type: ProductType, type_name: str) -> int:
    """
    Eliminar productos de un tipo específico.
    
    Args:
        session: Sesión de base de datos
        product_type: Tipo de producto (ARTICLE o NOMENCLATURE)
        type_name: Nombre descriptivo para mostrar
    
    Returns:
        Número de registros eliminados
    """
    # Contar antes de eliminar
    count = session.query(Product).filter_by(product_type=product_type).count()
    
    if count == 0:
        print(f"✅ No hay {type_name} que eliminar")
        return 0
    
    print(f"🗑️  Eliminando {count} {type_name}...")
    
    # Primero eliminar componentes de BOM si existen
    if product_type == ProductType.NOMENCLATURE:
        # Obtener IDs de nomenclaturas
        nomenclature_ids = session.query(Product.id).filter_by(product_type=product_type).all()
        nomenclature_ids = [id[0] for id in nomenclature_ids]
        
        if nomenclature_ids:
            # Eliminar componentes del BOM
            from src.backend.models.core.products import ProductComponent
            deleted_components = session.query(ProductComponent).filter(
                ProductComponent.parent_id.in_(nomenclature_ids)
            ).delete(synchronize_session=False)
            print(f"   📦 Eliminados {deleted_components} componentes de BOM")
    
    # Eliminar productos
    deleted = session.query(Product).filter_by(product_type=product_type).delete(synchronize_session=False)
    session.commit()
    
    print(f"✅ {deleted} {type_name} eliminados")
    return deleted


def confirm_action(counts: dict) -> bool:
    """
    Solicitar confirmación del usuario antes de proceder.
    
    Args:
        counts: Diccionario con los conteos de registros
    
    Returns:
        True si el usuario confirma, False si cancela
    """
    print("\n" + "="*60)
    print("🚨 ADVERTENCIA: ESTA A PUNTO DE ELIMINAR DATOS 🚨")
    print("="*60)
    print("\nSe eliminarán los siguientes registros:")
    print(f"  • {counts['clientes']} clientes")
    print(f"  • {counts['proveedores']} proveedores")
    print(f"  • {counts['articulos']} artículos")
    print(f"  • {counts['nomenclaturas']} nomenclaturas")
    
    total = sum(counts.values())
    print(f"\nTotal: {total} registros serán eliminados permanentemente.")
    
    print("\n" + "="*60)
    
    # Solicitar confirmación
    response = input("\n¿Está seguro que desea continuar? (escriba 'ELIMINAR' para confirmar): ")
    
    return response.strip().upper() == "ELIMINAR"


def main():
    """Función principal del script."""
    print("🧹 Script de Limpieza de Base de Datos")
    print("=====================================")
    
    # Crear sesión
    session = get_session()
    
    try:
        # Contar registros
        print("\n📊 Contando registros a eliminar...")
        counts = count_records(session)
        
        # Mostrar resumen
        print("\nResumen de registros a eliminar:")
        print(f"  • Clientes: {counts['clientes']}")
        print(f"  • Proveedores: {counts['proveedores']}")
        print(f"  • Artículos: {counts['articulos']}")
        print(f"  • Nomenclaturas: {counts['nomenclaturas']}")
        
        # Verificar si hay algo que eliminar
        total = sum(counts.values())
        if total == 0:
            print("\n✅ No hay registros que eliminar. La base de datos ya está limpia.")
            return
        
        # Solicitar confirmación
        if not confirm_action(counts):
            print("\n❌ Operación cancelada por el usuario.")
            return
        
        # Proceder con la limpieza
        print("\n🚀 Iniciando limpieza de la base de datos...")
        print("-" * 60)
        
        total_deleted = 0
        
        # Eliminar clientes
        total_deleted += cleanup_companies(session, "CLIENT", "clientes")
        
        # Eliminar proveedores
        total_deleted += cleanup_companies(session, "SUPPLIER", "proveedores")
        
        # Eliminar artículos
        total_deleted += cleanup_products(session, ProductType.ARTICLE, "artículos")
        
        # Eliminar nomenclaturas
        total_deleted += cleanup_products(session, ProductType.NOMENCLATURE, "nomenclaturas")
        
        print("-" * 60)
        print(f"\n✅ Limpieza completada. Total eliminados: {total_deleted} registros")
        
        # Verificar que todo fue eliminado
        print("\n🔍 Verificando que no queden registros...")
        remaining = count_records(session)
        remaining_total = sum(remaining.values())
        
        if remaining_total == 0:
            print("✅ Todos los registros fueron eliminados correctamente")
        else:
            print(f"⚠️  Quedaron {remaining_total} registros sin eliminar")
            for key, value in remaining.items():
                if value > 0:
                    print(f"   • {key}: {value}")
    
    except Exception as e:
        print(f"\n❌ Error durante la limpieza: {str(e)}")
        session.rollback()
        raise
    
    finally:
        session.close()


if __name__ == "__main__":
    main()
