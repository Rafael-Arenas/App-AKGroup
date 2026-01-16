"""
Repositorio para Product y ProductComponent.

Maneja el acceso a datos para productos y sus componentes (BOM).
"""

from collections.abc import Sequence

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from src.backend.models.core.products import Product, ProductComponent
from src.backend.repositories.base import BaseRepository
from src.backend.utils.logger import logger


class ProductRepository(BaseRepository[Product]):
    """
    Repositorio para Product con métodos específicos.

    Maneja productos simples (ARTICLE) y productos con BOM (NOMENCLATURE).

    Example:
        repo = ProductRepository(session)
        product = repo.get_by_reference("PROD-001")
        products = repo.search("tornillo")
    """

    def __init__(self, session: Session):
        """
        Inicializa el repositorio de Product.

        Args:
            session: Sesión de SQLAlchemy
        """
        super().__init__(session, Product)

    def get_by_reference(self, reference: str) -> Product | None:
        """
        Busca un producto por su referencia.

        Args:
            reference: Referencia del producto

        Returns:
            Product si existe, None en caso contrario

        Example:
            product = repo.get_by_reference("PROD-001")
        """
        logger.debug(f"Buscando producto por referencia: {reference}")
        stmt = select(Product).filter(Product.reference == reference.upper())
        product = self.session.execute(stmt).scalar_one_or_none()

        if product:
            logger.debug(f"Producto encontrado: {product.designation_es or product.designation_fr or product.designation_en} (reference={reference})")
        else:
            logger.debug(f"No se encontró producto con reference={reference}")

        return product

    def search(self, query: str) -> Sequence[Product]:
        """
        Busca productos por referencia o designación en cualquier idioma (búsqueda parcial).

        Args:
            query: Texto a buscar

        Returns:
            Lista de productos que coinciden

        Example:
            products = repo.search("torn")
            # Encuentra "Tornillo M6", "Tornillo M8", etc.
        """
        logger.debug(f"Buscando productos: query='{query}'")
        search_pattern = f"%{query}%"
        stmt = (
            select(Product)
            .filter(
                or_(
                    Product.reference.ilike(search_pattern),
                    Product.designation_es.ilike(search_pattern),
                    Product.designation_en.ilike(search_pattern),
                    Product.designation_fr.ilike(search_pattern),
                    Product.short_designation.ilike(search_pattern)
                )
            )
            .order_by(Product.reference)
        )
        products = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontrados {len(products)} producto(s) con '{query}'")
        return products

    def get_with_components(self, product_id: int) -> Product | None:
        """
        Obtiene un producto con sus componentes (BOM) cargados.

        Args:
            product_id: ID del producto

        Returns:
            Product con components cargados, None si no existe

        Example:
            product = repo.get_with_components(123)
            if product and product.product_type == "NOMENCLATURE":
                for comp in product.components:
                    print(f"{comp.component.designation_es}: {comp.quantity}")
        """
        logger.debug(f"Obteniendo producto id={product_id} con componentes")
        stmt = (
            select(Product)
            .options(
                selectinload(Product.components).selectinload(ProductComponent.component)
            )
            .filter(Product.id == product_id)
        )
        product = self.session.execute(stmt).scalar_one_or_none()

        if product:
            logger.debug(f"Producto encontrado con {len(product.components)} componente(s)")

        return product

    def get_active_products(self, skip: int = 0, limit: int = 100) -> Sequence[Product]:
        """
        Obtiene solo los productos activos.

        Args:
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de productos activos

        Example:
            active_products = repo.get_active_products()
        """
        logger.debug(f"Obteniendo productos activos - skip={skip}, limit={limit}")
        stmt = (
            select(Product)
            .filter(Product.is_active.is_(True))
            .order_by(Product.reference)
            .offset(skip)
            .limit(limit)
        )
        products = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontrados {len(products)} producto(s) activo(s)")
        return products

    def get_by_type(self, product_type: str, skip: int = 0, limit: int = 100) -> Sequence[Product]:
        """
        Obtiene productos por tipo (ARTICLE o NOMENCLATURE).

        Args:
            product_type: Tipo de producto
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de productos del tipo especificado

        Example:
            articles = repo.get_by_type("ARTICLE")
            nomenclatures = repo.get_by_type("NOMENCLATURE")
        """
        logger.debug(f"Obteniendo productos tipo={product_type}")
        stmt = (
            select(Product)
            .filter(Product.product_type == product_type.lower())  # Convert to lowercase for comparison
            .order_by(Product.reference)
            .offset(skip)
            .limit(limit)
        )
        products = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontrados {len(products)} producto(s) tipo {product_type}")
        return products

    def get_low_stock(self, skip: int = 0, limit: int = 100) -> Sequence[Product]:
        """
        Obtiene productos con stock bajo (stock_quantity < min_stock).

        Args:
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de productos con stock bajo

        Example:
            low_stock = repo.get_low_stock()
            for product in low_stock:
                print(f"{product.designation_es}: {product.stock_quantity} < {product.minimum_stock}")
        """
        logger.debug(f"Obteniendo productos con stock bajo")
        stmt = (
            select(Product)
            .filter(
                Product.stock_quantity < Product.minimum_stock,
                Product.minimum_stock.isnot(None),
                Product.is_active.is_(True)
            )
            .order_by(Product.reference)
            .offset(skip)
            .limit(limit)
        )
        products = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontrados {len(products)} producto(s) con stock bajo")
        return products

    def get_by_family(self, family_type_id: int, skip: int = 0, limit: int = 100) -> Sequence[Product]:
        """
        Obtiene productos por familia.

        Args:
            family_type_id: ID de la familia
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de productos de la familia

        Example:
            products = repo.get_by_family(family_type_id=1)
        """
        logger.debug(f"Obteniendo productos familia={family_type_id}")
        stmt = (
            select(Product)
            .filter(Product.family_type_id == family_type_id)
            .order_by(Product.reference)
            .offset(skip)
            .limit(limit)
        )
        products = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontrados {len(products)} producto(s) familia {family_type_id}")
        return products


class ProductComponentRepository(BaseRepository[ProductComponent]):
    """
    Repositorio para ProductComponent (BOM).

    Maneja los componentes de productos.

    Example:
        repo = ProductComponentRepository(session)
        components = repo.get_by_parent(parent_id=1)
    """

    def __init__(self, session: Session):
        super().__init__(session, ProductComponent)

    def get_by_parent(self, parent_id: int) -> Sequence[ProductComponent]:
        """
        Obtiene todos los componentes de un producto padre.

        Args:
            parent_id: ID del producto padre

        Returns:
            Lista de componentes

        Example:
            components = repo.get_by_parent(parent_id=1)
            for comp in components:
                print(f"{comp.component.designation_es}: {comp.quantity}")
        """
        logger.debug(f"Obteniendo componentes de producto parent_id={parent_id}")
        stmt = (
            select(ProductComponent)
            .options(selectinload(ProductComponent.component))
            .filter(ProductComponent.parent_id == parent_id)
        )
        components = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontrados {len(components)} componente(s)")
        return components

    def get_by_component(self, component_id: int) -> Sequence[ProductComponent]:
        """
        Obtiene todos los productos que usan este componente.

        Args:
            component_id: ID del componente

        Returns:
            Lista de usos del componente

        Example:
            # ¿Dónde se usa el tornillo M6?
            uses = repo.get_by_component(component_id=5)
            for use in uses:
                print(f"Se usa en: {use.parent.designation_es}")
        """
        logger.debug(f"Obteniendo usos del componente component_id={component_id}")
        stmt = (
            select(ProductComponent)
            .options(selectinload(ProductComponent.parent))
            .filter(ProductComponent.component_id == component_id)
        )
        uses = self.session.execute(stmt).scalars().all()

        logger.debug(f"Componente usado en {len(uses)} producto(s)")
        return uses

    def get_component(self, parent_id: int, component_id: int) -> ProductComponent | None:
        """
        Obtiene un componente específico de un producto.

        Args:
            parent_id: ID del producto padre
            component_id: ID del componente

        Returns:
            ProductComponent si existe, None en caso contrario

        Example:
            comp = repo.get_component(parent_id=1, component_id=5)
            if comp:
                print(f"Cantidad: {comp.quantity}")
        """
        logger.debug(f"Obteniendo componente parent_id={parent_id}, component_id={component_id}")
        stmt = select(ProductComponent).filter(
            ProductComponent.parent_id == parent_id,
            ProductComponent.component_id == component_id
        )
        component = self.session.execute(stmt).scalar_one_or_none()

        return component

    def delete_component(self, parent_id: int, component_id: int) -> None:
        """
        Elimina un componente específico de un producto.

        Args:
            parent_id: ID del producto padre
            component_id: ID del componente

        Raises:
            NotFoundException: Si el componente no existe

        Example:
            repo.delete_component(parent_id=1, component_id=5)
        """
        logger.debug(f"Eliminando componente parent_id={parent_id}, component_id={component_id}")

        component = self.get_component(parent_id, component_id)
        if not component:
            from src.backend.exceptions.repository import NotFoundException
            raise NotFoundException(
                "Componente no encontrado",
                details={"parent_id": parent_id, "component_id": component_id}
            )

        self.session.delete(component)
        self.session.flush()
        logger.info(f"Componente eliminado: parent_id={parent_id}, component_id={component_id}")
