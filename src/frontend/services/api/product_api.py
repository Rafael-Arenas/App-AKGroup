"""
Servicio API para gestión de Products (Productos).

Este módulo proporciona métodos para interactuar con los endpoints de productos
del backend FastAPI, incluyendo gestión de componentes BOM (Bill of Materials).
"""

from typing import Any
from loguru import logger

from .base_api_client import BaseAPIClient


class ProductAPIService:
    """
    Servicio para operaciones CRUD de Products.

    Proporciona métodos asíncronos para listar, crear, actualizar, eliminar
    productos, y gestionar sus componentes (BOM).
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/api/v1",
        timeout: float = 30.0,
    ) -> None:
        """
        Inicializa el servicio de Product API.

        Args:
            base_url: URL base del backend
            timeout: Timeout en segundos para las peticiones

        Example:
            >>> service = ProductAPIService()
        """
        self._client = BaseAPIClient(base_url=base_url, timeout=timeout)
        logger.debug("ProductAPIService inicializado | base_url={}", base_url)

    async def get_all(
        self,
        skip: int | None = None,
        limit: int | None = None,
        page: int | None = None,
        page_size: int | None = None,
        **filters: Any,
    ) -> dict[str, Any]:
        """
        Obtiene todos los productos con paginación.

        Args:
            skip: Número de registros a omitir
            limit: Número máximo de registros a retornar
            page: Número de página (1-indexed, alternativa a skip)
            page_size: Tamaño de página (alternativa a limit)
            **filters: Filtros adicionales (product_type, is_active, etc.)

        Returns:
            Diccionario con 'items' (lista de productos) y 'total' (total de registros)

        Raises:
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> result = await service.get_all(page=1, page_size=20)
            >>> print(f"Total productos: {result['total']}")
        """
        # Convertir page/page_size a skip/limit si se proporcionan
        if page is not None and page_size is not None:
            skip = (page - 1) * page_size
            limit = page_size
        elif skip is None:
            skip = 0
        if limit is None:
            limit = 100

        logger.info(
            "Obteniendo todos los productos | skip={} limit={} filters={}",
            skip,
            limit,
            filters,
        )

        try:
            # Preparar parámetros de consulta
            params = {"skip": skip, "limit": limit}
            params.update(filters)

            products = await self._client.get("/products/", params=params)

            # Retornar en formato esperado por las vistas
            result = {
                "items": products if isinstance(products, list) else [],
                "total": len(products) if isinstance(products, list) else 0,
            }

            logger.success(
                "Productos obtenidos exitosamente | total={}", result["total"]
            )
            return result

        except Exception as e:
            logger.error("Error al obtener productos | error={}", str(e))
            raise

    async def get_by_id(self, product_id: int) -> dict[str, Any]:
        """
        Obtiene un producto por su ID.

        Args:
            product_id: ID del producto

        Returns:
            Datos del producto en formato diccionario

        Raises:
            NotFoundException: Si el producto no existe
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> product = await service.get_by_id(1)
            >>> print(f"Producto: {product['name']} ({product['code']})")
        """
        logger.info("Obteniendo producto por ID | product_id={}", product_id)

        try:
            product = await self._client.get(f"/products/{product_id}")

            logger.success(
                "Producto obtenido exitosamente | id={} reference={} designation_es={}",
                product_id,
                product.get("reference"),
                product.get("designation_es"),
            )
            return product

        except Exception as e:
            logger.error(
                "Error al obtener producto | product_id={} error={}", product_id, str(e)
            )
            raise

    async def get_by_type(self, product_type: str, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
        """
        Obtiene productos filtrados por tipo.

        Args:
            product_type: Tipo de producto ("article" o "nomenclature")
            skip: Número de registros a omitir (default: 0)
            limit: Número máximo de registros (default: 100)

        Returns:
            Lista de productos del tipo especificado

        Raises:
            ValidationException: Si el tipo de producto es inválido
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> articles = await service.get_by_type("article", skip=0, limit=20)
            >>> nomenclatures = await service.get_by_type("nomenclature", skip=0, limit=20)
            >>> print(f"Artículos: {len(articles)}, Nomenclaturas: {len(nomenclatures)}")
        """
        logger.info("Obteniendo productos por tipo | product_type={} skip={} limit={}", product_type, skip, limit)

        # Validar tipo de producto
        valid_types = ["article", "nomenclature"]
        if product_type not in valid_types:
            logger.error("Tipo de producto inválido | product_type={}", product_type)
            raise ValueError(
                f"Tipo de producto inválido. Debe ser uno de: {', '.join(valid_types)}"
            )

        try:
            products = await self._client.get(
                "/products/type/{}".format(product_type.upper()),
                params={"skip": skip, "limit": limit},
            )

            logger.success(
                "Productos obtenidos por tipo | product_type={} total={}",
                product_type,
                len(products),
            )
            return products

        except Exception as e:
            logger.error(
                "Error al obtener productos por tipo | product_type={} error={}",
                product_type,
                str(e),
            )
            raise

    async def search(
        self,
        query: str,
        page: int | None = None,
        page_size: int | None = None,
        **params: Any,
    ) -> dict[str, Any]:
        """
        Busca productos por código o nombre (búsqueda parcial).

        Args:
            query: Texto de búsqueda (código o nombre)
            page: Número de página (1-indexed)
            page_size: Tamaño de página
            **params: Parámetros adicionales

        Returns:
            Diccionario con 'items' (lista de productos) y 'total' (total de registros)

        Raises:
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> result = await service.search("ART-", page=1, page_size=20)
            >>> for product in result['items']:
            ...     print(product["name"])
        """
        # Convertir page/page_size a skip/limit
        skip = 0
        limit = 100
        if page is not None and page_size is not None:
            skip = (page - 1) * page_size
            limit = page_size

        logger.info(
            "Buscando productos | query={} skip={} limit={}", query, skip, limit
        )

        try:
            # Preparar parámetros
            search_params = {"skip": skip, "limit": limit}
            search_params.update(params)

            products = await self._client.get(
                f"/products/search/{query}",
                params=search_params,
            )

            # Retornar en formato esperado
            result = {
                "items": products if isinstance(products, list) else [],
                "total": len(products) if isinstance(products, list) else 0,
            }

            logger.success(
                "Búsqueda completada | query={} results={}", query, result["total"]
            )
            return result

        except Exception as e:
            logger.error("Error al buscar productos | query={} error={}", query, str(e))
            raise

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Crea un nuevo producto.

        Args:
            data: Datos del producto a crear. Debe incluir:
                - code: str (requerido, código único)
                - name: str (requerido)
                - product_type: str (requerido, "ARTICLE" o "NOMENCLATURE")
                - unit_id: int (requerido)
                - description: str (opcional)
                - specifications: str (opcional)
                - is_active: bool (opcional, default: True)

        Returns:
            Datos del producto creado con su ID asignado

        Raises:
            ValidationException: Si los datos son inválidos (422)
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> new_product = await service.create({
            ...     "code": "ART-001",
            ...     "name": "Producto Ejemplo",
            ...     "product_type": "ARTICLE",
            ...     "unit_id": 1,
            ...     "description": "Descripción del producto",
            ...     "specifications": "Especificaciones técnicas",
            ...     "is_active": True
            ... })
            >>> print(f"Producto creado con ID: {new_product['id']}")
        """
        logger.info(
            "Creando nuevo producto | reference={} designation_es={}",
            data.get("reference"),
            data.get("designation_es"),
        )

        try:
            product = await self._client.post("/products/", json=data)

            logger.success(
                "Producto creado exitosamente | id={} reference={} designation_es={}",
                product.get("id"),
                product.get("reference"),
                product.get("designation_es"),
            )
            return product

        except Exception as e:
            logger.error("Error al crear producto | data={} error={}", data, str(e))
            raise

    async def update(
        self,
        product_id: int,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Actualiza un producto existente.

        Args:
            product_id: ID del producto a actualizar
            data: Datos a actualizar (campos opcionales):
                - code: str
                - name: str
                - product_type: str
                - unit_id: int
                - description: str
                - specifications: str
                - is_active: bool

        Returns:
            Datos del producto actualizado

        Raises:
            NotFoundException: Si el producto no existe
            ValidationException: Si los datos son inválidos (422)
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> updated_product = await service.update(1, {
            ...     "name": "Producto Actualizado",
            ...     "description": "Nueva descripción"
            ... })
            >>> print(f"Producto actualizado: {updated_product['name']}")
        """
        logger.info("Actualizando producto | product_id={} data={}", product_id, data)

        try:
            product = await self._client.put(f"/products/{product_id}", json=data)

            logger.success(
                "Producto actualizado exitosamente | id={} reference={} designation_es={}",
                product_id,
                product.get("reference"),
                product.get("designation_es"),
            )
            return product

        except Exception as e:
            logger.error(
                "Error al actualizar producto | product_id={} data={} error={}",
                product_id,
                data,
                str(e),
            )
            raise

    async def delete(self, product_id: int) -> bool:
        """
        Elimina un producto.

        Args:
            product_id: ID del producto a eliminar

        Returns:
            True si la eliminación fue exitosa

        Raises:
            NotFoundException: Si el producto no existe
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> success = await service.delete(1)
            >>> if success:
            ...     print("Producto eliminado exitosamente")
        """
        logger.info("Eliminando producto | product_id={}", product_id)

        try:
            result = await self._client.delete(f"/products/{product_id}")

            logger.success(
                "Producto eliminado exitosamente | product_id={}", product_id
            )
            return result

        except Exception as e:
            logger.error(
                "Error al eliminar producto | product_id={} error={}",
                product_id,
                str(e),
            )
            raise

    async def add_component(
        self,
        product_id: int,
        component_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Añade un componente a la lista de materiales (BOM) de un producto.

        Args:
            product_id: ID del producto padre
            component_data: Datos del componente. Debe incluir:
                - component_product_id: int (requerido, ID del producto componente)
                - quantity: float (requerido, cantidad requerida)
                - unit_id: int (requerido, unidad de medida)

        Returns:
            Datos del componente añadido con su ID asignado

        Raises:
            NotFoundException: Si el producto no existe
            ValidationException: Si los datos son inválidos (422)
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> component = await service.add_component(1, {
            ...     "component_product_id": 5,
            ...     "quantity": 2.5,
            ...     "unit_id": 1
            ... })
            >>> print(f"Componente añadido: {component['component_product_id']}")
        """
        logger.info(
            "Añadiendo componente a producto | product_id={} component_data={}",
            product_id,
            component_data,
        )

        try:
            component = await self._client.post(
                f"/products/{product_id}/components",
                json=component_data,
            )

            logger.success(
                "Componente añadido exitosamente | product_id={} component_id={}",
                product_id,
                component.get("id"),
            )
            return component

        except Exception as e:
            logger.error(
                "Error al añadir componente | product_id={} component_data={} error={}",
                product_id,
                component_data,
                str(e),
            )
            raise

    async def remove_component(
        self,
        product_id: int,
        component_id: int,
    ) -> bool:
        """
        Elimina un componente de la lista de materiales (BOM) de un producto.

        Args:
            product_id: ID del producto padre
            component_id: ID del componente a eliminar

        Returns:
            True si la eliminación fue exitosa

        Raises:
            NotFoundException: Si el producto o componente no existe
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> success = await service.remove_component(1, 5)
            >>> if success:
            ...     print("Componente eliminado exitosamente")
        """
        logger.info(
            "Eliminando componente de producto | product_id={} component_id={}",
            product_id,
            component_id,
        )

        try:
            result = await self._client.delete(
                f"/products/{product_id}/components/{component_id}"
            )

            logger.success(
                "Componente eliminado exitosamente | product_id={} component_id={}",
                product_id,
                component_id,
            )
            return result

        except Exception as e:
            logger.error(
                "Error al eliminar componente | product_id={} component_id={} error={}",
                product_id,
                component_id,
                str(e),
            )
            raise

    async def get_bom_components(
        self,
        product_id: int,
    ) -> list[dict[str, Any]]:
        """
        Obtiene los componentes BOM de un producto (nomenclatura).

        Args:
            product_id: ID del producto padre

        Returns:
            Lista de componentes con sus datos

        Raises:
            NotFoundException: Si el producto no existe
            NetworkException: Error de red/conexión
            APIException: Error de API

        Example:
            >>> components = await service.get_bom_components(1)
            >>> for comp in components:
            ...     print(f"{comp['component']['reference']}: {comp['quantity']}")
        """
        logger.info(
            "Obteniendo componentes BOM | product_id={}",
            product_id,
        )

        try:
            components = await self._client.get(
                f"/products/{product_id}/components"
            )

            logger.debug(f"Raw components data from API for product {product_id}: {components}")

            if components is None:
                logger.warning(f"API returned None for components of product {product_id}")
                return []
                
            if not isinstance(components, list):
                logger.warning(f"API returned non-list for components of product {product_id}: {type(components)}")
                return []

            logger.success(
                "Componentes BOM obtenidos exitosamente | product_id={} total={}",
                product_id,
                len(components),
            )
            return components

        except Exception as e:
            logger.error(
                "Error al obtener componentes BOM | product_id={} error={}",
                product_id,
                str(e),
            )
            raise

    async def close(self) -> None:
        """
        Cierra el cliente HTTP y libera recursos.

        Example:
            >>> await service.close()
        """
        await self._client.close()

    async def __aenter__(self) -> "ProductAPIService":
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        await self.close()
