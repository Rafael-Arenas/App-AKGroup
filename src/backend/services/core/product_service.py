"""
Servicio de lógica de negocio para Product.

Implementa validaciones y reglas de negocio para productos,
incluyendo gestión de BOM (Bill of Materials) con detección de ciclos.
"""

from decimal import Decimal


from sqlalchemy.orm import Session

from src.backend.models.core.products import Product, ProductComponent
from src.backend.repositories.core.product_repository import (
    ProductRepository,
    ProductComponentRepository
)
from src.shared.schemas.core.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductComponentCreate,
    ProductComponentUpdate,
    ProductComponentResponse,
)
from src.backend.services.base import BaseService
from src.backend.exceptions.service import ValidationException, BusinessRuleException
from src.backend.config.constants import PRODUCT_TYPE_ARTICLE, PRODUCT_TYPE_NOMENCLATURE
from src.backend.utils.logger import logger


class ProductService(BaseService[Product, ProductCreate, ProductUpdate, ProductResponse]):
    """
    Servicio para Product con validaciones de negocio.

    Maneja la lógica de negocio para productos, incluyendo:
    - Validación de código único
    - Gestión de BOM con detección de ciclos
    - Cálculo de costos recursivos
    - Validaciones de stock

    Example:
        service = ProductService(product_repo, component_repo, session)
        product = service.create(ProductCreate(...), user_id=1)
        service.add_component(parent_id=1, component_id=5, quantity=4, user_id=1)
    """

    def __init__(
        self,
        product_repository: ProductRepository,
        component_repository: ProductComponentRepository,
        session: Session,
    ):
        """
        Inicializa el servicio de Product.

        Args:
            product_repository: Repositorio de Product
            component_repository: Repositorio de ProductComponent
            session: Sesión de SQLAlchemy
        """
        super().__init__(
            repository=product_repository,
            session=session,
            model=Product,
            response_schema=ProductResponse,
        )
        self.product_repo: ProductRepository = product_repository
        self.component_repo: ProductComponentRepository = component_repository

    def validate_create(self, entity: Product) -> None:
        """
        Valida reglas de negocio antes de crear un producto.

        Args:
            entity: Producto a validar

        Raises:
            ValidationException: Si el código ya existe
        """
        logger.debug(f"Validando creación de producto: reference={entity.reference}")

        # Validar que la referencia sea única
        existing = self.product_repo.get_by_reference(entity.reference)
        if existing:
            raise ValidationException(
                f"Ya existe un producto con la referencia '{entity.reference}'",
                details={
                    "reference": entity.reference,
                    "existing_product_id": existing.id,
                    "existing_product_designation": existing.designation_es or existing.designation_fr or existing.designation_en,
                }
            )

        logger.debug("Validación de creación exitosa")

    def validate_update(self, entity: Product) -> None:
        """
        Valida reglas de negocio antes de actualizar un producto.

        Args:
            entity: Producto a validar

        Raises:
            ValidationException: Si el código ya existe en otro producto
        """
        logger.debug(f"Validando actualización de producto id={entity.id}")

        # Validar que la referencia sea única (excluyendo el mismo producto)
        existing = self.product_repo.get_by_reference(entity.reference)
        if existing and existing.id != entity.id:
            raise ValidationException(
                f"Ya existe otro producto con la referencia '{entity.reference}'",
                details={
                    "reference": entity.reference,
                    "current_product_id": entity.id,
                    "existing_product_id": existing.id,
                    "existing_product_designation": existing.designation_es or existing.designation_fr or existing.designation_en,
                }
            )

        logger.debug("Validación de actualización exitosa")

    def get_by_reference(self, reference: str) -> ProductResponse:
        """
        Obtiene un producto por su referencia.

        Args:
            reference: Referencia del producto

        Returns:
            Producto encontrado

        Raises:
            NotFoundException: Si no se encuentra el producto

        Example:
            product = service.get_by_reference("PROD-001")
        """
        logger.info(f"Servicio: buscando producto por reference={reference}")

        product = self.product_repo.get_by_reference(reference)
        if not product:
            from src.backend.exceptions.repository import NotFoundException
            raise NotFoundException(
                f"No se encontró producto con referencia '{reference}'",
                details={"reference": reference}
            )

        return self.response_schema.model_validate(product)

    def search(self, query: str) -> list[ProductResponse]:
        """
        Busca productos por código o nombre.

        Args:
            query: Texto a buscar

        Returns:
            Lista de productos encontrados

        Example:
            products = service.search("torn")
        """
        logger.info(f"Servicio: buscando productos query='{query}'")

        products = self.product_repo.search(query)
        return [self.response_schema.model_validate(p) for p in products]

    def get_with_components(self, product_id: int) -> ProductResponse:
        """
        Obtiene un producto con sus componentes (BOM).

        Args:
            product_id: ID del producto

        Returns:
            Producto con componentes cargados

        Raises:
            NotFoundException: Si no se encuentra el producto

        Example:
            product = service.get_with_components(123)
            for comp in product.components:
                print(comp.component_name)
        """
        logger.info(f"Servicio: obteniendo producto id={product_id} con componentes")

        product = self.product_repo.get_with_components(product_id)
        if not product:
            from src.backend.exceptions.repository import NotFoundException
            raise NotFoundException(
                f"No se encontró producto con id={product_id}",
                details={"product_id": product_id}
            )

        return self.response_schema.model_validate(product)

    def get_by_type(self, product_type: str, skip: int = 0, limit: int = 100) -> list[ProductResponse]:
        """
        Obtiene productos por tipo.

        Args:
            product_type: ARTICLE o NOMENCLATURE
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de productos del tipo especificado

        Example:
            articles = service.get_by_type("ARTICLE")
        """
        logger.info(f"Servicio: obteniendo productos tipo={product_type}")

        products = self.product_repo.get_by_type(product_type, skip, limit)
        return [self.response_schema.model_validate(p) for p in products]

    # ========================================================================
    # BOM MANAGEMENT (Bill of Materials)
    # ========================================================================

    def add_component(
        self,
        parent_id: int,
        component_id: int,
        quantity: Decimal,
        user_id: int
    ) -> ProductComponentResponse:
        """
        Agrega un componente a un producto (BOM).

        Args:
            parent_id: ID del producto padre
            component_id: ID del componente a agregar
            quantity: Cantidad del componente
            user_id: ID del usuario

        Returns:
            Componente creado

        Raises:
            BusinessRuleException: Si el padre no es NOMENCLATURE
            BusinessRuleException: Si se detecta un ciclo
            ValidationException: Si los IDs no existen

        Example:
            # Agregar 4 tornillos al ensamble
            comp = service.add_component(
                parent_id=1,
                component_id=5,
                quantity=Decimal("4.000"),
                user_id=1
            )
        """
        logger.info(f"Servicio: agregando componente parent_id={parent_id}, component_id={component_id}")

        # Validar que el padre existe y es NOMENCLATURE
        parent = self.product_repo.get_by_id(parent_id)
        if not parent:
            raise ValidationException(
                f"Producto padre no encontrado",
                details={"parent_id": parent_id}
            )

        if parent.product_type != PRODUCT_TYPE_NOMENCLATURE:
            raise BusinessRuleException(
                f"Solo productos NOMENCLATURE pueden tener componentes",
                details={
                    "parent_id": parent_id,
                    "parent_type": parent.product_type,
                    "required_type": PRODUCT_TYPE_NOMENCLATURE
                }
            )

        # Validar que el componente existe
        component = self.product_repo.get_by_id(component_id)
        if not component:
            raise ValidationException(
                f"Componente no encontrado",
                details={"component_id": component_id}
            )

        # Validar que no crea un ciclo
        if self._would_create_cycle(parent_id, component_id):
            raise BusinessRuleException(
                f"Agregar este componente crearía un ciclo en el BOM",
                details={
                    "parent_id": parent_id,
                    "component_id": component_id,
                    "parent_designation": parent.designation_es or parent.designation_fr or parent.designation_en,
                    "component_designation": component.designation_es or component.designation_fr or component.designation_en
                }
            )

        # Crear el componente
        self.session.info["user_id"] = user_id

        product_component = ProductComponent(
            parent_id=parent_id,
            component_id=component_id,
            quantity=quantity
        )

        created = self.component_repo.create(product_component)
        logger.success(f"Componente agregado: id={created.id}")

        return ProductComponentResponse.model_validate(created)

    def update_component(
        self,
        parent_id: int,
        component_id: int,
        quantity: Decimal,
        user_id: int
    ) -> ProductComponentResponse:
        """
        Actualiza la cantidad de un componente.

        Args:
            parent_id: ID del producto padre
            component_id: ID del componente
            quantity: Nueva cantidad
            user_id: ID del usuario

        Returns:
            Componente actualizado

        Raises:
            NotFoundException: Si el componente no existe

        Example:
            comp = service.update_component(
                parent_id=1,
                component_id=5,
                quantity=Decimal("6.000"),
                user_id=1
            )
        """
        logger.info(f"Servicio: actualizando componente parent_id={parent_id}, component_id={component_id}")

        component = self.component_repo.get_component(parent_id, component_id)
        if not component:
            from src.backend.exceptions.repository import NotFoundException
            raise NotFoundException(
                "Componente no encontrado",
                details={"parent_id": parent_id, "component_id": component_id}
            )

        self.session.info["user_id"] = user_id
        component.quantity = quantity

        updated = self.component_repo.update(component)
        logger.success(f"Componente actualizado: parent_id={parent_id}, component_id={component_id}")

        return ProductComponentResponse.model_validate(updated)

    def remove_component(
        self,
        parent_id: int,
        component_id: int,
        user_id: int
    ) -> None:
        """
        Elimina un componente de un producto.

        Args:
            parent_id: ID del producto padre
            component_id: ID del componente
            user_id: ID del usuario

        Example:
            service.remove_component(parent_id=1, component_id=5, user_id=1)
        """
        logger.info(f"Servicio: eliminando componente parent_id={parent_id}, component_id={component_id}")

        self.session.info["user_id"] = user_id
        self.component_repo.delete_component(parent_id, component_id)
        logger.success(f"Componente eliminado")

    def _would_create_cycle(self, parent_id: int, component_id: int) -> bool:
        """
        Verifica si agregar un componente crearía un ciclo en el BOM.

        Un ciclo ocurre cuando:
        - El componente es el mismo que el padre (A contiene A)
        - El componente ya contiene al padre en su BOM (A contiene B, B contiene A)

        Args:
            parent_id: ID del producto padre
            component_id: ID del componente a agregar

        Returns:
            True si crearía un ciclo, False en caso contrario

        Example:
            # Evitar ciclo: A → B → A
            if service._would_create_cycle(parent_id=1, component_id=2):
                raise BusinessRuleException("Ciclo detectado")
        """
        # Caso 1: Componente es el mismo que el padre
        if parent_id == component_id:
            logger.warning(f"Ciclo directo detectado: producto se contiene a sí mismo")
            return True

        # Caso 2: Buscar ciclos recursivamente
        visited: set[int] = set()

        def has_cycle_recursive(current_id: int) -> bool:
            """Búsqueda recursiva de ciclos."""
            if current_id == parent_id:
                return True  # Encontramos el padre = ciclo

            if current_id in visited:
                return False  # Ya visitado, no hay ciclo por esta rama

            visited.add(current_id)

            # Obtener componentes del producto actual
            components = self.component_repo.get_by_parent(current_id)

            for comp in components:
                if has_cycle_recursive(comp.component_id):
                    return True

            return False

        # Buscar ciclos desde el componente
        cycle_detected = has_cycle_recursive(component_id)

        if cycle_detected:
            logger.warning(f"Ciclo indirecto detectado: parent_id={parent_id}, component_id={component_id}")

        return cycle_detected

    def calculate_bom_cost(self, product_id: int) -> Decimal:
        """
        Calcula el costo total de un producto incluyendo su BOM (recursivo).

        Args:
            product_id: ID del producto

        Returns:
            Costo total calculado

        Example:
            cost = service.calculate_bom_cost(product_id=1)
            print(f"Costo total: ${cost}")
        """
        logger.info(f"Servicio: calculando costo BOM para product_id={product_id}")

        product = self.product_repo.get_with_components(product_id)
        if not product:
            return Decimal("0.00")

        # Si es ARTICLE, retornar su costo directo
        if product.product_type == PRODUCT_TYPE_ARTICLE:
            return product.cost_price or Decimal("0.00")

        # Si es NOMENCLATURE, calcular recursivamente
        total_cost = Decimal("0.00")

        for comp in product.components:
            component_cost = self.calculate_bom_cost(comp.component_id)
            total_cost += component_cost * comp.quantity

        logger.debug(f"Costo BOM calculado para product_id={product_id}: {total_cost}")
        return total_cost
