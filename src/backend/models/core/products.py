"""
Product models - Unified product system.

Sistema unificado que maneja 3 tipos de productos:
- ARTICLE: Productos terminados para venta
- NOMENCLATURE: Conjuntos/kits con BOM (Bill of Materials)
- SERVICE: Servicios sin stock

Características:
- Tabla única polimórfica
- BOM jerárquico ilimitado (solo para NOMENCLATURE)
- Prevención de ciclos en BOM
- Cálculo automático de precios desde componentes
- Gestión de stock (solo ARTICLE)
- Dimensiones y pesos
- Múltiples precios (cost, purchase, sale)
"""

import enum
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, validates

from ..base import ActiveMixin, AuditMixin, Base, DecimalValidator, TimestampMixin

if TYPE_CHECKING:
    from ..lookups import FamilyType, Matter, SalesType


class ProductType(str, enum.Enum):
    """
    Tipos de producto en el sistema unificado.

    Values:
        ARTICLE: Producto terminado para venta (con stock)
        NOMENCLATURE: Conjunto/kit con BOM (puede tener stock calculado)
        SERVICE: Servicio sin stock físico
    """

    ARTICLE = "article"
    NOMENCLATURE = "nomenclature"
    SERVICE = "service"


class PriceCalculationMode(str, enum.Enum):
    """
    Modo de cálculo de precio para productos.

    Values:
        MANUAL: Precio definido manualmente
        FROM_COMPONENTS: Precio calculado desde componentes del BOM
        FROM_COST_MARGIN: Precio calculado desde costo + margen
    """

    MANUAL = "manual"
    FROM_COMPONENTS = "from_components"
    FROM_COST_MARGIN = "from_cost_margin"


class Product(Base, TimestampMixin, AuditMixin, ActiveMixin):
    """
    Producto unificado (ARTICLE, NOMENCLATURE, SERVICE).

    Sistema de tabla única que maneja tres tipos de productos:
    - ARTICLE: Productos físicos terminados
    - NOMENCLATURE: Conjuntos con lista de materiales (BOM)
    - SERVICE: Servicios sin inventario

    Attributes:
        # Identification
        id: Primary key
        product_type: Tipo de producto (ARTICLE, NOMENCLATURE, SERVICE)
        reference: Referencia única del producto
        designation_fr: Designación en francés
        designation_es: Designación en español
        designation_en: Designación en inglés
        short_designation: Designación corta
        revision: Identificador de revisión/versión del producto

        # Classification
        family_type_id: FK a family_types
        matter_id: FK a matters
        sales_type_id: FK a sales_types
        company_id: FK a companies (fabricante/proveedor)

        # Pricing
        purchase_price: Precio de compra
        cost_price: Precio de costo
        sale_price: Precio de venta
        sale_price_eur: Precio en euros
        price_calculation_mode: Modo de cálculo de precio
        margin_percentage: Margen esperado (%)

        # Stock (solo ARTICLE)
        stock_quantity: Cantidad en stock
        minimum_stock: Stock mínimo
        stock_location: Ubicación en almacén

        # Physical properties
        net_weight: Peso neto (kg)
        gross_weight: Peso bruto (kg)
        length: Longitud (mm)
        width: Ancho (mm)
        height: Altura (mm)
        volume: Volumen (m³)

        # Additional
        hs_code: Código arancelario
        country_of_origin: País de origen
        image_url: URL de la imagen del producto
        plan_url: URL del plano/diseño del producto
        supplier_reference: Referencia del proveedor
        customs_number: Número de aduana
        notes: Notas adicionales

    Relationships:
        family_type: Tipo de familia
        matter: Materia
        sales_type: Tipo de venta
        company: Empresa fabricante
        components: Componentes del BOM (si es NOMENCLATURE)
        parent_components: Productos donde este es componente
        quote_products: Productos en cotizaciones

    Example:
        >>> # Crear artículo simple
        >>> article = Product(
        ...     product_type=ProductType.ARTICLE,
        ...     reference="ART-001",
        ...     designation_es="Producto terminado",
        ...     cost_price=Decimal("100.00"),
        ...     sale_price=Decimal("150.00"),
        ...     stock_quantity=50
        ... )
        >>>
        >>> # Crear nomenclatura con BOM
        >>> nomenclature = Product(
        ...     product_type=ProductType.NOMENCLATURE,
        ...     reference="NOM-001",
        ...     designation_es="Kit completo",
        ...     price_calculation_mode=PriceCalculationMode.FROM_COMPONENTS
        ... )
        >>> # Agregar componentes
        >>> component = ProductComponent(
        ...     parent_id=nomenclature.id,
        ...     component_id=article.id,
        ...     quantity=2
        ... )
    """

    __tablename__ = "products"

    # ========== PRIMARY KEY ==========
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ========== PRODUCT TYPE ==========
    product_type = Column(
        SQLEnum(ProductType),
        nullable=False,
        index=True,
        comment="Product type: article, nomenclature, or service",
    )

    # ========== IDENTIFICATION ==========
    reference = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique product reference code",
    )

    designation_fr = Column(
        String(200),
        nullable=True,
        comment="Product designation in French",
    )

    designation_es = Column(
        String(200),
        nullable=True,
        comment="Product designation in Spanish",
    )

    designation_en = Column(
        String(200),
        nullable=True,
        comment="Product designation in English",
    )

    short_designation = Column(
        String(100),
        nullable=True,
        comment="Short/abbreviated designation",
    )

    revision = Column(
        String(20),
        nullable=True,
        comment="Product revision/version identifier",
    )

    # ========== CLASSIFICATION ==========
    family_type_id = Column(
        Integer,
        ForeignKey("family_types.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Product family classification",
    )

    matter_id = Column(
        Integer,
        ForeignKey("matters.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Material/matter type",
    )

    sales_type_id = Column(
        Integer,
        ForeignKey("sales_types.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Sales type classification",
    )

    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Manufacturer/supplier company",
    )

    # ========== PRICING ==========
    purchase_price = Column(
        Numeric(15, 2),
        nullable=True,
        comment="Purchase price from supplier",
    )

    cost_price = Column(
        Numeric(15, 2),
        nullable=True,
        comment="Internal cost price",
    )

    sale_price = Column(
        Numeric(15, 2),
        nullable=True,
        comment="Sale price (base currency)",
    )

    sale_price_eur = Column(
        Numeric(15, 2),
        nullable=True,
        comment="Sale price in EUR",
    )

    price_calculation_mode = Column(
        SQLEnum(PriceCalculationMode),
        nullable=False,
        default=PriceCalculationMode.MANUAL,
        comment="How price is calculated: manual, from_components, from_cost_margin",
    )

    margin_percentage = Column(
        Numeric(5, 2),
        nullable=True,
        comment="Expected profit margin percentage",
    )

    # ========== STOCK (solo para ARTICLE) ==========
    stock_quantity = Column(
        Numeric(15, 3),
        nullable=True,
        default=Decimal("0.000"),
        comment="Current stock quantity (null for SERVICE)",
    )

    minimum_stock = Column(
        Numeric(15, 3),
        nullable=True,
        comment="Minimum stock threshold for alerts",
    )

    stock_location = Column(
        String(100),
        nullable=True,
        comment="Physical location in warehouse",
    )

    # ========== PHYSICAL PROPERTIES ==========
    net_weight = Column(
        Numeric(10, 3),
        nullable=True,
        comment="Net weight in kg",
    )

    gross_weight = Column(
        Numeric(10, 3),
        nullable=True,
        comment="Gross weight in kg (with packaging)",
    )

    length = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Length in mm",
    )

    width = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Width in mm",
    )

    height = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Height in mm",
    )

    volume = Column(
        Numeric(10, 4),
        nullable=True,
        comment="Volume in cubic meters",
    )

    # ========== INTERNATIONAL ==========
    hs_code = Column(
        String(20),
        nullable=True,
        comment="Harmonized System code for customs",
    )

    country_of_origin = Column(
        String(100),
        nullable=True,
        comment="Country where product is manufactured",
    )

    # ========== ADDITIONAL ==========
    image_url = Column(
        String(500),
        nullable=True,
        comment="URL of the product image",
    )

    plan_url = Column(
        String(500),
        nullable=True,
        comment="URL of the product plan/blueprint",
    )

    supplier_reference = Column(
        String(100),
        nullable=True,
        comment="Supplier reference code",
    )

    customs_number = Column(
        String(50),
        nullable=True,
        comment="Customs clearance number",
    )

    notes = Column(
        Text,
        nullable=True,
        comment="Additional notes and observations",
    )

    # ========== RELATIONSHIPS ==========
    family_type = relationship(
        "FamilyType",
        back_populates="products",
        lazy="joined",
    )

    matter = relationship(
        "Matter",
        back_populates="products",
        lazy="joined",
    )

    sales_type = relationship(
        "SalesType",
        back_populates="products",
        lazy="joined",
    )

    company = relationship(
        "Company",
        back_populates="products",
        lazy="select",
    )

    # BOM relationships
    components = relationship(
        "ProductComponent",
        foreign_keys="ProductComponent.parent_id",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="select",
    )

    parent_components = relationship(
        "ProductComponent",
        foreign_keys="ProductComponent.component_id",
        back_populates="component",
        lazy="select",
    )

    # Business relationships (Fase 4)
    # quote_products = relationship("QuoteProduct", back_populates="product", lazy="select")

    # ========== TABLE CONSTRAINTS ==========
    __table_args__ = (
        # Indexes
        Index("ix_products_product_type_active", "product_type", "is_active"),
        # Note: reference already has index=True in column definition (line 180)
        # Note: family_type_id already has index=True in column definition (line 219)
        # Check constraints
        CheckConstraint(
            "length(trim(reference)) >= 2",
            name="reference_min_length",
        ),
        CheckConstraint(
            "purchase_price IS NULL OR purchase_price >= 0",
            name="purchase_price_non_negative",
        ),
        CheckConstraint(
            "cost_price IS NULL OR cost_price >= 0",
            name="cost_price_non_negative",
        ),
        CheckConstraint(
            "sale_price IS NULL OR sale_price >= 0",
            name="sale_price_non_negative",
        ),
        CheckConstraint(
            "stock_quantity IS NULL OR stock_quantity >= 0",
            name="stock_quantity_non_negative",
        ),
        CheckConstraint(
            "margin_percentage IS NULL OR (margin_percentage >= -100 AND margin_percentage <= 1000)",
            name="margin_percentage_range",
        ),
        CheckConstraint(
            "net_weight IS NULL OR net_weight >= 0",
            name="net_weight_non_negative",
        ),
        CheckConstraint(
            "gross_weight IS NULL OR gross_weight >= 0",
            name="gross_weight_non_negative",
        ),
    )

    # ========== VALIDATORS ==========
    @validates("reference")
    def validate_reference(self, key: str, value: str) -> str:
        """Valida y normaliza la referencia del producto."""
        if not value or len(value.strip()) < 2:
            raise ValueError("Product reference must be at least 2 characters long")
        return value.strip().upper()

    @validates("purchase_price", "cost_price", "sale_price", "sale_price_eur")
    def validate_prices(self, key: str, value: Optional[Decimal]) -> Optional[Decimal]:
        """Valida que los precios sean no negativos."""
        return DecimalValidator.validate_non_negative(value, field_name=key)

    @validates("stock_quantity", "minimum_stock")
    def validate_stock(self, key: str, value: Optional[Decimal]) -> Optional[Decimal]:
        """Valida stock (solo para ARTICLE)."""
        if value is not None and self.product_type == ProductType.SERVICE:
            raise ValueError(f"{key} should be NULL for SERVICE products")
        return DecimalValidator.validate_non_negative(value, field_name=key)

    @validates("net_weight", "gross_weight")
    def validate_weights(self, key: str, value: Optional[Decimal]) -> Optional[Decimal]:
        """Valida pesos."""
        return DecimalValidator.validate_non_negative(value, field_name=key)

    @validates("margin_percentage")
    def validate_margin(self, key: str, value: Optional[Decimal]) -> Optional[Decimal]:
        """Valida margen de ganancia."""
        if value is not None and (value < -100 or value > 1000):
            raise ValueError("Margin percentage must be between -100% and 1000%")
        return value

    # ========== COMPUTED PROPERTIES ==========
    @property
    def effective_cost(self) -> Optional[Decimal]:
        """
        Retorna el costo efectivo del producto.

        Para NOMENCLATURE con FROM_COMPONENTS: suma costos de componentes.
        Para otros: retorna cost_price.

        Returns:
            Costo efectivo o None
        """
        if (
            self.product_type == ProductType.NOMENCLATURE
            and self.price_calculation_mode == PriceCalculationMode.FROM_COMPONENTS
        ):
            return self.calculated_cost
        return self.cost_price

    @property
    def effective_price(self) -> Optional[Decimal]:
        """
        Retorna el precio de venta efectivo.

        Según price_calculation_mode:
        - MANUAL: sale_price
        - FROM_COMPONENTS: suma precios de componentes
        - FROM_COST_MARGIN: cost_price + margin

        Returns:
            Precio efectivo o None
        """
        if self.price_calculation_mode == PriceCalculationMode.MANUAL:
            return self.sale_price

        elif self.price_calculation_mode == PriceCalculationMode.FROM_COMPONENTS:
            return self.calculated_price

        elif self.price_calculation_mode == PriceCalculationMode.FROM_COST_MARGIN:
            if self.cost_price and self.margin_percentage:
                return self.cost_price * (1 + self.margin_percentage / 100)
            return self.sale_price

        return self.sale_price

    @property
    def calculated_cost(self) -> Optional[Decimal]:
        """
        Calcula el costo sumando los costos de todos los componentes.

        Returns:
            Costo total calculado o None si no hay componentes
        """
        if not self.components:
            return None

        total = Decimal("0.00")
        for comp in self.components:
            if comp.component and comp.component.effective_cost:
                total += comp.component.effective_cost * comp.quantity
        return total if total > 0 else None

    @property
    def calculated_price(self) -> Optional[Decimal]:
        """
        Calcula el precio sumando los precios de todos los componentes.

        Returns:
            Precio total calculado o None si no hay componentes
        """
        if not self.components:
            return None

        total = Decimal("0.00")
        for comp in self.components:
            if comp.component and comp.component.effective_price:
                total += comp.component.effective_price * comp.quantity
        return total if total > 0 else None

    @property
    def margin(self) -> Optional[Decimal]:
        """
        Calcula el margen absoluto (sale_price - cost_price).

        Returns:
            Margen en unidades monetarias o None
        """
        if self.effective_price and self.effective_cost:
            return self.effective_price - self.effective_cost
        return None

    @property
    def margin_percent(self) -> Optional[Decimal]:
        """
        Calcula el margen porcentual ((sale_price - cost_price) / cost_price * 100).

        Returns:
            Margen en porcentaje o None
        """
        if self.margin and self.effective_cost and self.effective_cost > 0:
            return (self.margin / self.effective_cost) * 100
        return None

    # ========== BOM METHODS ==========
    def get_bom_tree(
        self, level: int = 0, visited: Optional[set] = None
    ) -> dict[str, Any]:
        """
        Retorna el árbol jerárquico completo del BOM.

        Args:
            level: Nivel de profundidad actual
            visited: Set de IDs visitados para prevenir ciclos

        Returns:
            Dict con estructura jerárquica del BOM

        Raises:
            ValueError: Si se detecta un ciclo en el BOM

        Example:
            >>> product.get_bom_tree()
            {
                'id': 1,
                'reference': 'NOM-001',
                'designation': 'Kit',
                'level': 0,
                'components': [
                    {
                        'id': 2,
                        'reference': 'ART-001',
                        'quantity': 2,
                        'level': 1,
                        'components': []
                    }
                ]
            }
        """
        if visited is None:
            visited = set()

        if self.id in visited:
            raise ValueError(
                f"Circular reference detected in BOM: product {self.reference} (id={self.id})"
            )

        visited.add(self.id)

        tree = {
            "id": self.id,
            "reference": self.reference,
            "designation": self.designation_es
            or self.designation_en
            or self.designation_fr,
            "product_type": self.product_type.value,
            "level": level,
            "components": [],
        }

        for comp in self.components:
            if comp.component:
                comp_tree = comp.component.get_bom_tree(level + 1, visited.copy())
                comp_tree["quantity"] = float(comp.quantity)
                comp_tree["unit_cost"] = float(comp.component.effective_cost or 0)
                comp_tree["unit_price"] = float(comp.component.effective_price or 0)
                comp_tree["total_cost"] = comp_tree["unit_cost"] * comp_tree["quantity"]
                comp_tree["total_price"] = (
                    comp_tree["unit_price"] * comp_tree["quantity"]
                )
                tree["components"].append(comp_tree)

        return tree

    def get_flat_bom(self, visited: Optional[set] = None) -> list[dict[str, Any]]:
        """
        Retorna una lista plana de todos los componentes (todos los niveles).

        Args:
            visited: Set de IDs visitados para prevenir ciclos

        Returns:
            Lista de componentes con cantidades consolidadas

        Example:
            >>> product.get_flat_bom()
            [
                {'product_id': 2, 'reference': 'ART-001', 'quantity': 2},
                {'product_id': 3, 'reference': 'ART-002', 'quantity': 4}
            ]
        """
        if visited is None:
            visited = set()

        if self.id in visited:
            return []

        visited.add(self.id)

        flat_list: dict[int, dict[str, Any]] = {}

        for comp in self.components:
            if not comp.component:
                continue

            component_id = comp.component.id
            quantity = comp.quantity

            # Agregar componente directo
            if component_id in flat_list:
                flat_list[component_id]["quantity"] += quantity
            else:
                flat_list[component_id] = {
                    "product_id": component_id,
                    "reference": comp.component.reference,
                    "designation": (
                        comp.component.designation_es
                        or comp.component.designation_en
                        or comp.component.designation_fr
                    ),
                    "quantity": quantity,
                    "unit_cost": comp.component.effective_cost,
                    "unit_price": comp.component.effective_price,
                }

            # Agregar sub-componentes recursivamente
            sub_components = comp.component.get_flat_bom(visited.copy())
            for sub_comp in sub_components:
                sub_id = sub_comp["product_id"]
                sub_qty = sub_comp["quantity"] * quantity

                if sub_id in flat_list:
                    flat_list[sub_id]["quantity"] += sub_qty
                else:
                    flat_list[sub_id] = sub_comp.copy()
                    flat_list[sub_id]["quantity"] = sub_qty

        return list(flat_list.values())

    def get_total_weight(self) -> Optional[Decimal]:
        """
        Calcula el peso total incluyendo todos los componentes.

        Returns:
            Peso total neto en kg o None
        """
        if self.product_type == ProductType.SERVICE:
            return None

        if self.product_type == ProductType.ARTICLE:
            return self.net_weight

        # NOMENCLATURE: sumar pesos de componentes
        if not self.components:
            return self.net_weight

        total = Decimal("0.000")
        for comp in self.components:
            if comp.component:
                comp_weight = comp.component.get_total_weight()
                if comp_weight:
                    total += comp_weight * comp.quantity

        return total if total > 0 else self.net_weight

    def validate_no_cycles(
        self, component_id: int, visited: Optional[set] = None
    ) -> None:
        """
        Valida que agregar un componente no cree ciclos en el BOM.

        Args:
            component_id: ID del componente a agregar
            visited: Set de IDs visitados

        Raises:
            ValueError: Si se detecta un ciclo
        """
        if visited is None:
            visited = set()

        if component_id == self.id:
            raise ValueError(
                f"Cannot add product {self.reference} as component of itself"
            )

        visited.add(self.id)

        # Verificar si el componente a agregar contiene este producto en su BOM
        from sqlalchemy.orm import Session

        session = Session.object_session(self)
        if session:
            component = session.get(Product, component_id)
            if component:
                try:
                    component.get_bom_tree(visited=visited)
                except ValueError as e:
                    raise ValueError(
                        f"Adding component {component.reference} would create a cycle: {str(e)}"
                    )

    def __repr__(self) -> str:
        return (
            f"<Product(id={self.id}, type={self.product_type.value}, "
            f"reference='{self.reference}')>"
        )


class ProductComponent(Base, TimestampMixin, AuditMixin):
    """
    Componente de un producto (BOM - Bill of Materials).

    Representa la relación padre-componente para NOMENCLATURE.
    Permite crear estructuras jerárquicas ilimitadas.

    Attributes:
        id: Primary key
        parent_id: FK al producto padre (NOMENCLATURE)
        component_id: FK al producto componente
        quantity: Cantidad del componente necesaria
        notes: Notas sobre el componente

    Relationships:
        parent: Producto padre (NOMENCLATURE)
        component: Producto componente

    Example:
        >>> # Kit que contiene 2 unidades de ART-001
        >>> bom = ProductComponent(
        ...     parent_id=1,  # NOM-001 (Kit)
        ...     component_id=2,  # ART-001
        ...     quantity=Decimal("2.000")
        ... )
    """

    __tablename__ = "product_components"

    # ========== PRIMARY KEY ==========
    id = Column(Integer, primary_key=True, autoincrement=True)

    # ========== FOREIGN KEYS ==========
    parent_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Parent product (NOMENCLATURE) containing this component",
    )

    component_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Component product (any type)",
    )

    # ========== QUANTITY ==========
    quantity = Column(
        Numeric(15, 3),
        nullable=False,
        default=Decimal("1.000"),
        comment="Quantity of component required",
    )

    # ========== ADDITIONAL ==========
    notes = Column(
        Text,
        nullable=True,
        comment="Notes about this component usage",
    )

    # ========== RELATIONSHIPS ==========
    parent = relationship(
        "Product",
        foreign_keys=[parent_id],
        back_populates="components",
    )

    component = relationship(
        "Product",
        foreign_keys=[component_id],
        back_populates="parent_components",
        lazy="joined",
    )

    # ========== TABLE CONSTRAINTS ==========
    __table_args__ = (
        # Un producto no puede tener el mismo componente dos veces
        UniqueConstraint("parent_id", "component_id", name="uq_parent_component"),
        # Índices
        # Note: parent_id and component_id already have index=True in column definitions (lines 824, 832)
        # Index("ix_product_components_parent_id", "parent_id"),
        # Index("ix_product_components_component_id", "component_id"),
        # Constraints
        CheckConstraint(
            "quantity > 0",
            name="quantity_positive",
        ),
        CheckConstraint(
            "parent_id != component_id",
            name="no_self_reference",
        ),
    )

    # ========== VALIDATORS ==========
    @validates("quantity")
    def validate_quantity(self, key: str, value: Decimal) -> Decimal:
        """Valida que la cantidad sea positiva."""
        if value <= 0:
            raise ValueError("Component quantity must be positive")
        return value

    @validates("parent_id", "component_id")
    def validate_no_self_reference(self, key: str, value: int) -> int:
        """Valida que un producto no sea componente de sí mismo."""
        if key == "component_id" and hasattr(self, "parent_id"):
            if self.parent_id == value:
                raise ValueError("Product cannot be a component of itself")
        elif key == "parent_id" and hasattr(self, "component_id"):
            if self.component_id == value:
                raise ValueError("Product cannot be a component of itself")
        return value

    def __repr__(self) -> str:
        return (
            f"<ProductComponent(id={self.id}, parent_id={self.parent_id}, "
            f"component_id={self.component_id}, quantity={self.quantity})>"
        )
