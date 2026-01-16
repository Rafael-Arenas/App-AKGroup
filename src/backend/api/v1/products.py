"""
Endpoints REST para Product.

Proporciona operaciones CRUD sobre productos y gestión de BOM.
"""


from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from src.backend.api.dependencies import get_database, get_current_user_id
from src.backend.services.core.product_service import ProductService
from src.backend.repositories.core.product_repository import (
    ProductRepository,
    ProductComponentRepository,
)
from src.shared.schemas.core.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductComponentCreate,
    ProductComponentUpdate,
    ProductComponentResponse,
)
from src.shared.schemas.base import MessageResponse
from src.backend.utils.logger import logger

router = APIRouter(prefix="/products", tags=["products"])


def get_product_service(db: Session = Depends(get_database)) -> ProductService:
    """
    Dependency para obtener instancia de ProductService.

    Args:
        db: Sesión de base de datos

    Returns:
        Instancia configurada de ProductService
    """
    product_repository = ProductRepository(db)
    component_repository = ProductComponentRepository(db)
    return ProductService(
        product_repository=product_repository,
        component_repository=component_repository,
        session=db
    )


@router.get("/", response_model=list[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    service: ProductService = Depends(get_product_service),
):
    """
    Obtiene todos los productos con paginación.

    Args:
        skip: Número de registros a saltar (default: 0)
        limit: Número máximo de registros (default: 100)
        db: Sesión de base de datos

    Returns:
        Lista de productos

    Example:
        GET /api/v1/products?skip=0&limit=50
    """
    logger.info(f"GET /products - skip={skip}, limit={limit}")

    # Service injected via dependency
    products = service.get_all(skip=skip, limit=limit)

    logger.info(f"Retornando {len(products)} producto(s)")
    return products


@router.get("/search", response_model=list[ProductResponse])
def search_products(
    q: str = Query(..., description="Texto a buscar en código o nombre"),
    service: ProductService = Depends(get_product_service),
):
    """
    Busca productos por código o nombre (búsqueda parcial).

    Args:
        q: Texto a buscar
        db: Sesión de base de datos

    Returns:
        Lista de productos que coinciden

    Example:
        GET /api/v1/products/search?q=torn
    """
    logger.info(f"GET /products/search?q={q}")

    # Service injected via dependency
    products = service.search(q)

    logger.info(f"Búsqueda '{q}' retornó {len(products)} producto(s)")
    return products


@router.get("/type/{product_type}", response_model=list[ProductResponse])
def get_products_by_type(
    product_type: str,
    skip: int = 0,
    limit: int = 100,
    service: ProductService = Depends(get_product_service),
):
    """
    Obtiene productos por tipo (ARTICLE o NOMENCLATURE).

    Args:
        product_type: Tipo de producto (ARTICLE o NOMENCLATURE)
        skip: Número de registros a saltar
        limit: Número máximo de registros
        db: Sesión de base de datos

    Returns:
        Lista de productos del tipo especificado

    Example:
        GET /api/v1/products/type/ARTICLE
        GET /api/v1/products/type/NOMENCLATURE
    """
    logger.info(f"GET /products/type/{product_type}")

    # Service injected via dependency
    products = service.get_by_type(product_type, skip, limit)

    logger.info(f"Retornando {len(products)} producto(s) tipo {product_type}")
    return products


@router.get("/reference/{reference}", response_model=ProductResponse)
def get_product_by_reference(
    reference: str,
    service: ProductService = Depends(get_product_service),
):
    """
    Obtiene un producto por su referencia.

    Args:
        reference: Referencia del producto (ej: "PROD-001")
        db: Sesión de base de datos

    Returns:
        Producto encontrado

    Raises:
        404: Si no se encuentra el producto

    Example:
        GET /api/v1/products/reference/PROD-001
    """
    logger.info(f"GET /products/reference/{reference}")

    # Service injected via dependency
    product = service.get_by_reference(reference)

    logger.info(f"Producto encontrado: {product.reference}")
    return product


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    """
    Obtiene un producto por ID.

    Args:
        product_id: ID del producto
        db: Sesión de base de datos

    Returns:
        Producto encontrado

    Raises:
        404: Si no se encuentra el producto

    Example:
        GET /api/v1/products/123
    """
    logger.info(f"GET /products/{product_id}")

    # Service injected via dependency
    product = service.get_by_id(product_id)

    logger.info(f"Producto encontrado: {product.reference}")
    return product


@router.get("/{product_id}/with-components", response_model=ProductResponse)
def get_product_with_components(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    """
    Obtiene un producto con sus componentes (BOM) cargados.

    Args:
        product_id: ID del producto
        db: Sesión de base de datos

    Returns:
        Producto con componentes

    Raises:
        404: Si no se encuentra el producto

    Example:
        GET /api/v1/products/123/with-components
    """
    logger.info(f"GET /products/{product_id}/with-components")

    # Service injected via dependency
    product = service.get_with_components(product_id)

    logger.info(f"Producto encontrado con {len(product.components)} componente(s)")
    return product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    service: ProductService = Depends(get_product_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Crea un nuevo producto.

    Args:
        product_data: Datos del producto a crear
        db: Sesión de base de datos
        user_id: ID del usuario que crea

    Returns:
        Producto creado

    Raises:
        400: Si los datos no son válidos
        409: Si el código ya existe

    Example:
        POST /api/v1/products
        Body (ARTICLE):
        {
            "code": "PROD-001",
            "name": "Tornillo M6",
            "product_type": "ARTICLE",
            "cost_price": 100.00,
            "sale_price": 150.00,
            "unit_id": 1
        }

        Body (NOMENCLATURE):
        {
            "code": "ASSEM-001",
            "name": "Ensamble Completo",
            "product_type": "NOMENCLATURE",
            "unit_id": 1
        }
    """
    logger.info(f"POST /products - reference={product_data.reference}")

    # Service injected via dependency
    product = service.create(product_data, user_id)

    logger.success(f"Producto creado: id={product.id}, reference={product.reference}")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    service: ProductService = Depends(get_product_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Actualiza un producto existente.

    Args:
        product_id: ID del producto a actualizar
        product_data: Datos a actualizar
        db: Sesión de base de datos
        user_id: ID del usuario que actualiza

    Returns:
        Producto actualizado

    Raises:
        404: Si no se encuentra el producto
        400: Si los datos no son válidos

    Example:
        PUT /api/v1/products/123
        Body:
        {
            "name": "Nuevo Nombre",
            "sale_price": 200.00
        }
    """
    logger.info(f"PUT /products/{product_id}")

    # Service injected via dependency
    product = service.update(product_id, product_data, user_id)

    logger.success(f"Producto actualizado: id={product_id}")
    return product


@router.delete("/{product_id}", response_model=MessageResponse)
def delete_product(
    product_id: int,
    soft: bool = True,
    service: ProductService = Depends(get_product_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Elimina un producto.

    Args:
        product_id: ID del producto a eliminar
        soft: Si True, soft delete; si False, hard delete (default: True)
        db: Sesión de base de datos
        user_id: ID del usuario que elimina

    Returns:
        Mensaje de confirmación

    Raises:
        404: Si no se encuentra el producto

    Example:
        DELETE /api/v1/products/123?soft=true
    """
    logger.info(f"DELETE /products/{product_id} (soft={soft})")

    # Service injected via dependency
    service.delete(product_id, user_id, soft=soft)

    delete_type = "marcado como eliminado" if soft else "eliminado permanentemente"
    logger.success(f"Producto {delete_type}: id={product_id}")

    return MessageResponse(
        message=f"Producto {delete_type} exitosamente",
        details={"product_id": product_id, "soft_delete": soft}
    )


# ============================================================================
# BOM (Bill of Materials) ENDPOINTS
# ============================================================================

@router.post("/{product_id}/components", response_model=ProductComponentResponse, status_code=status.HTTP_201_CREATED)
def add_component(
    product_id: int,
    component_data: ProductComponentCreate,
    service: ProductService = Depends(get_product_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Agrega un componente a un producto (BOM).

    El producto debe ser de tipo NOMENCLATURE.

    Args:
        product_id: ID del producto padre (debe coincidir con component_data.parent_id)
        component_data: Datos del componente a agregar
        db: Sesión de base de datos
        user_id: ID del usuario

    Returns:
        Componente creado

    Raises:
        422: Si el producto no es NOMENCLATURE
        422: Si se detecta un ciclo en el BOM
        400: Si los datos no son válidos

    Example:
        POST /api/v1/products/1/components
        Body:
        {
            "parent_id": 1,
            "component_id": 5,
            "quantity": 4.000
        }
    """
    logger.info(f"POST /products/{product_id}/components")

    # Service injected via dependency
    component = service.add_component(
        parent_id=component_data.parent_id,
        component_id=component_data.component_id,
        quantity=float(component_data.quantity),
        user_id=user_id
    )

    logger.success(f"Componente agregado: parent_id={component_data.parent_id}, component_id={component_data.component_id}")
    return component


@router.put("/{product_id}/components/{component_id}", response_model=ProductComponentResponse)
def update_component(
    product_id: int,
    component_id: int,
    component_data: ProductComponentUpdate,
    service: ProductService = Depends(get_product_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Actualiza la cantidad de un componente.

    Args:
        product_id: ID del producto padre
        component_id: ID del componente
        component_data: Nueva cantidad
        db: Sesión de base de datos
        user_id: ID del usuario

    Returns:
        Componente actualizado

    Raises:
        404: Si el componente no existe

    Example:
        PUT /api/v1/products/1/components/5
        Body:
        {
            "quantity": 6.000
        }
    """
    logger.info(f"PUT /products/{product_id}/components/{component_id}")

    # Service injected via dependency
    component = service.update_component(
        parent_id=product_id,
        component_id=component_id,
        quantity=float(component_data.quantity),
        user_id=user_id
    )

    logger.success(f"Componente actualizado: parent_id={product_id}, component_id={component_id}")
    return component


@router.delete("/{product_id}/components/{component_id}", response_model=MessageResponse)
def remove_component(
    product_id: int,
    component_id: int,
    service: ProductService = Depends(get_product_service),
    user_id: int = Depends(get_current_user_id),
):
    """
    Elimina un componente de un producto.

    Args:
        product_id: ID del producto padre
        component_id: ID del componente a eliminar
        db: Sesión de base de datos
        user_id: ID del usuario

    Returns:
        Mensaje de confirmación

    Raises:
        404: Si el componente no existe

    Example:
        DELETE /api/v1/products/1/components/5
    """
    logger.info(f"DELETE /products/{product_id}/components/{component_id}")

    # Service injected via dependency
    service.remove_component(product_id, component_id, user_id)

    logger.success(f"Componente eliminado: parent_id={product_id}, component_id={component_id}")

    return MessageResponse(
        message="Componente eliminado exitosamente",
        details={"parent_id": product_id, "component_id": component_id}
    )


@router.get("/{product_id}/bom-cost")
def calculate_bom_cost(
    product_id: int,
    service: ProductService = Depends(get_product_service),
):
    """
    Calcula el costo total de un producto incluyendo su BOM (recursivo).

    Args:
        product_id: ID del producto
        db: Sesión de base de datos

    Returns:
        Costo total calculado

    Example:
        GET /api/v1/products/1/bom-cost
        Response:
        {
            "product_id": 1,
            "total_cost": 1250.50
        }
    """
    logger.info(f"GET /products/{product_id}/bom-cost")

    # Service injected via dependency
    cost = service.calculate_bom_cost(product_id)

    logger.info(f"Costo BOM calculado para product_id={product_id}: {cost}")

    return {
        "product_id": product_id,
        "total_cost": cost
    }
