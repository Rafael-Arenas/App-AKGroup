"""
Ejemplos de uso de los servicios API.

Este archivo muestra cómo utilizar los servicios API para interactuar
con el backend FastAPI desde el frontend Flet.
"""

import asyncio
from loguru import logger

# Importar servicios singleton
from . import company_api, product_api, lookup_api

# Importar excepciones para manejo de errores
from . import (
    APIException,
    NetworkException,
    ValidationException,
    NotFoundException,
)


async def example_companies() -> None:
    """Ejemplos de uso del servicio de Companies."""
    logger.info("=== EJEMPLOS DE COMPANIES ===")

    try:
        # 1. Obtener todas las empresas activas
        active_companies = await company_api.get_active()
        logger.info(f"Empresas activas: {len(active_companies)}")

        # 2. Obtener empresas con paginación
        companies = await company_api.get_all(skip=0, limit=10)
        logger.info(f"Primeras 10 empresas: {len(companies)}")

        # 3. Buscar empresas por nombre
        search_results = await company_api.search("AK")
        logger.info(f"Empresas que contienen 'AK': {len(search_results)}")

        # 4. Obtener una empresa específica
        if companies:
            company = await company_api.get_by_id(companies[0]["id"])
            logger.info(f"Empresa: {company['name']}")

        # 5. Crear una nueva empresa
        new_company_data = {
            "name": "AK Group Test",
            "company_type_id": 1,
            "country_id": 1,
            "nit": "900123456-7",
            "email": "test@akgroup.com",
            "phone": "+57 300 1234567",
            "address": "Calle 123 #45-67",
            "is_active": True,
        }
        new_company = await company_api.create(new_company_data)
        logger.info(f"Empresa creada con ID: {new_company['id']}")

        # 6. Actualizar empresa
        updated_company = await company_api.update(
            new_company["id"],
            {"name": "AK Group Test Updated", "phone": "+57 300 9876543"},
        )
        logger.info(f"Empresa actualizada: {updated_company['name']}")

        # 7. Eliminar empresa
        success = await company_api.delete(new_company["id"])
        logger.info(f"Empresa eliminada: {success}")

    except NotFoundException as e:
        logger.error(f"Recurso no encontrado: {e.message}")
    except ValidationException as e:
        logger.error(f"Error de validación: {e.message} | Detalles: {e.details}")
    except NetworkException as e:
        logger.error(f"Error de red: {e.message}")
    except APIException as e:
        logger.error(f"Error de API: {e.message} | Status: {e.status_code}")


async def example_products() -> None:
    """Ejemplos de uso del servicio de Products."""
    logger.info("=== EJEMPLOS DE PRODUCTS ===")

    try:
        # 1. Obtener todos los productos
        products = await product_api.get_all(skip=0, limit=50)
        logger.info(f"Total productos: {len(products)}")

        # 2. Obtener productos por tipo
        articles = await product_api.get_by_type("ARTICLE")
        nomenclatures = await product_api.get_by_type("NOMENCLATURE")
        logger.info(f"Artículos: {len(articles)}, Nomenclaturas: {len(nomenclatures)}")

        # 3. Obtener un producto específico
        if products:
            product = await product_api.get_by_id(products[0]["id"])
            logger.info(f"Producto: {product['code']} - {product['name']}")

        # 4. Crear un nuevo producto (artículo)
        new_article_data = {
            "code": "ART-TEST-001",
            "name": "Artículo de Prueba",
            "product_type": "ARTICLE",
            "unit_id": 1,
            "description": "Descripción del artículo",
            "specifications": "Especificaciones técnicas",
            "is_active": True,
        }
        new_article = await product_api.create(new_article_data)
        logger.info(f"Artículo creado con ID: {new_article['id']}")

        # 5. Crear una nomenclatura
        new_nomenclature_data = {
            "code": "NOM-TEST-001",
            "name": "Nomenclatura de Prueba",
            "product_type": "NOMENCLATURE",
            "unit_id": 1,
            "description": "Descripción de la nomenclatura",
            "is_active": True,
        }
        new_nomenclature = await product_api.create(new_nomenclature_data)
        logger.info(f"Nomenclatura creada con ID: {new_nomenclature['id']}")

        # 6. Añadir componentes a la nomenclatura (BOM)
        component_data = {
            "component_product_id": new_article["id"],
            "quantity": 2.5,
            "unit_id": 1,
        }
        component = await product_api.add_component(
            new_nomenclature["id"], component_data
        )
        logger.info(f"Componente añadido: {component['id']}")

        # 7. Actualizar producto
        updated_product = await product_api.update(
            new_article["id"],
            {"name": "Artículo Actualizado", "description": "Nueva descripción"},
        )
        logger.info(f"Producto actualizado: {updated_product['name']}")

        # 8. Eliminar componente
        success = await product_api.remove_component(
            new_nomenclature["id"], component["id"]
        )
        logger.info(f"Componente eliminado: {success}")

        # 9. Eliminar productos
        await product_api.delete(new_article["id"])
        await product_api.delete(new_nomenclature["id"])
        logger.info("Productos eliminados")

    except NotFoundException as e:
        logger.error(f"Recurso no encontrado: {e.message}")
    except ValidationException as e:
        logger.error(f"Error de validación: {e.message} | Detalles: {e.details}")
    except NetworkException as e:
        logger.error(f"Error de red: {e.message}")
    except APIException as e:
        logger.error(f"Error de API: {e.message} | Status: {e.status_code}")


async def example_lookups() -> None:
    """Ejemplos de uso del servicio de Lookups."""
    logger.info("=== EJEMPLOS DE LOOKUPS ===")

    try:
        # 1. Obtener tipos de empresa
        company_types = await lookup_api.get_company_types()
        logger.info(f"Tipos de empresa: {len(company_types)}")
        for ct in company_types:
            logger.info(f"  - {ct['id']}: {ct['name']}")

        # 2. Obtener países
        countries = await lookup_api.get_countries()
        logger.info(f"Países: {len(countries)}")
        for country in countries[:5]:  # Solo primeros 5
            logger.info(
                f"  - {country['code']}: {country['name']} ({country.get('phone_code', 'N/A')})"
            )

        # 3. Obtener unidades de medida
        units = await lookup_api.get_units()
        logger.info(f"Unidades: {len(units)}")
        for unit in units[:10]:  # Solo primeras 10
            logger.info(
                f"  - {unit['symbol']}: {unit['name']} ({unit.get('unit_type', 'N/A')})"
            )

    except NetworkException as e:
        logger.error(f"Error de red: {e.message}")
    except APIException as e:
        logger.error(f"Error de API: {e.message} | Status: {e.status_code}")


async def example_context_manager() -> None:
    """Ejemplo de uso con context managers."""
    logger.info("=== EJEMPLO DE CONTEXT MANAGER ===")

    # Usar servicios como context managers para asegurar cierre de conexiones
    async with company_api as service:
        companies = await service.get_all(limit=5)
        logger.info(f"Empresas obtenidas: {len(companies)}")

    # El cliente HTTP se cierra automáticamente al salir del contexto


async def main() -> None:
    """Ejecuta todos los ejemplos."""
    logger.info("Iniciando ejemplos de servicios API")

    # Ejecutar ejemplos
    await example_lookups()
    await example_companies()
    await example_products()
    await example_context_manager()

    logger.success("Ejemplos completados exitosamente")


if __name__ == "__main__":
    # Configurar logger
    logger.remove()
    logger.add(
        lambda msg: print(msg, end=""),
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True,
    )

    # Ejecutar ejemplos
    asyncio.run(main())
