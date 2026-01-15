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
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    CheckConstraint,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship, validates

from ..base import ActiveMixin, AuditMixin, Base, DecimalValidator, TimestampMixin

if TYPE_CHECKING:
    from ..lookups.business import SalesType
    from ..lookups.product import FamilyType, Matter
    from .companies import Company


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
        id: Primary key
        product_type: Tipo de producto (ARTICLE, NOMENCLATURE, SERVICE)
        reference: Referencia única del producto
        designation_fr: Designación en francés
        designation_es: Designación en español
        designation_en: Designación en inglés
        short_designation: Designación corta
        revision: Identificador de revisión/versión
    """

    __tablename__ = "products"

    # ========== PRIMARY KEY ==========
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ========== PRODUCT TYPE ==========
    product_type: Mapped[ProductType] = mapped_column(
        SQLEnum(ProductType),
        index=True,
        comment="Product type: article, nomenclature, or service",
    )

    # ========== IDENTIFICATION ==========
    reference: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, comment="Unique product reference code"
    )
    designation_fr: Mapped[str | None] = mapped_column(
        String(200), comment="Product designation in French"
    )
    designation_es: Mapped[str | None] = mapped_column(
        String(200), comment="Product designation in Spanish"
    )
    designation_en: Mapped[str | None] = mapped_column(
        String(200), comment="Product designation in English"
    )
    short_designation: Mapped[str | None] = mapped_column(
        String(100), comment="Short/abbreviated designation"
    )
    revision: Mapped[str | None] = mapped_column(
        String(20), comment="Product revision/version identifier"
    )

    # ========== CLASSIFICATION ==========
    family_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("family_types.id", ondelete="SET NULL"),
        index=True,
        comment="Product family classification",
    )
    matter_id: Mapped[int | None] = mapped_column(
        ForeignKey("matters.id", ondelete="SET NULL"),
        index=True,
        comment="Material/matter type",
    )
    sales_type_id: Mapped[int | None] = mapped_column(
        ForeignKey("sales_types.id", ondelete="SET NULL"),
        index=True,
        comment="Sales type classification",
    )
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"),
        index=True,
        comment="Manufacturer/supplier company",
    )

    # ========== PRICING ==========
    purchase_price: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2), comment="Purchase price from supplier"
    )
    cost_price: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2), comment="Internal cost price"
    )
    sale_price: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2), comment="Sale price (base currency)"
    )
    sale_price_eur: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2), comment="Sale price in EUR"
    )
    price_calculation_mode: Mapped[PriceCalculationMode] = mapped_column(
        SQLEnum(PriceCalculationMode),
        default=PriceCalculationMode.MANUAL,
        comment="How price is calculated: manual, from_components, from_cost_margin",
    )
    margin_percentage: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2), comment="Expected profit margin percentage"
    )

    # ========== STOCK (solo para ARTICLE) ==========
    stock_quantity: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 3),
        default=Decimal("0.000"),
        comment="Current stock quantity (null for SERVICE)",
    )
    minimum_stock: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 3), comment="Minimum stock threshold for alerts"
    )
    stock_location: Mapped[str | None] = mapped_column(
        String(100), comment="Physical location in warehouse"
    )

    # ========== PHYSICAL PROPERTIES ==========
    net_weight: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 3), comment="Net weight in kg"
    )
    gross_weight: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 3), comment="Gross weight in kg (with packaging)"
    )
    length: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), comment="Length in mm"
    )
    width: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), comment="Width in mm"
    )
    height: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), comment="Height in mm"
    )
    volume: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 4), comment="Volume in cubic meters"
    )

    # ========== INTERNATIONAL ==========
    hs_code: Mapped[str | None] = mapped_column(
        String(20), comment="Harmonized System code for customs"
    )
    country_of_origin: Mapped[str | None] = mapped_column(
        String(100), comment="Country where product is manufactured"
    )

    # ========== ADDITIONAL ==========
    image_url: Mapped[str | None] = mapped_column(
        String(500), comment="URL of the product image"
    )
    plan_url: Mapped[str | None] = mapped_column(
        String(500), comment="URL of the product plan/blueprint"
    )
    supplier_reference: Mapped[str | None] = mapped_column(
        String(100), comment="Supplier reference code"
    )
    customs_number: Mapped[str | None] = mapped_column(
        String(50), comment="Customs clearance number"
    )
    notes: Mapped[str | None] = mapped_column(
        Text, comment="Additional notes and observations"
    )

    # ========== RELATIONSHIPS ==========
    family_type: Mapped["FamilyType | None"] = relationship(
        "FamilyType", back_populates="products", lazy="joined"
    )
    matter: Mapped["Matter | None"] = relationship(
        "Matter", back_populates="products", lazy="joined"
    )
    sales_type: Mapped["SalesType | None"] = relationship(
        "SalesType", back_populates="products", lazy="joined"
    )
    company: Mapped["Company | None"] = relationship(
        "Company", back_populates="products", lazy="select"
    )

    # BOM relationships
    components: Mapped[list["ProductComponent"]] = relationship(
        "ProductComponent",
        foreign_keys="ProductComponent.parent_id",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="select",
    )
    parent_components: Mapped[list["ProductComponent"]] = relationship(
        "ProductComponent",
        foreign_keys="ProductComponent.component_id",
        back_populates="component",
        lazy="select",
    )

    # ========== TABLE CONSTRAINTS ==========
    __table_args__ = (
        Index("ix_products_product_type_active", "product_type", "is_active"),
        CheckConstraint("length(trim(reference)) >= 2", name="reference_min_length"),
        CheckConstraint(
            "purchase_price IS NULL OR purchase_price >= 0",
            name="purchase_price_non_negative",
        ),
        CheckConstraint(
            "cost_price IS NULL OR cost_price >= 0", name="cost_price_non_negative"
        ),
        CheckConstraint(
            "sale_price IS NULL OR sale_price >= 0", name="sale_price_non_negative"
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
            "net_weight IS NULL OR net_weight >= 0", name="net_weight_non_negative"
        ),
        CheckConstraint(
            "gross_weight IS NULL OR gross_weight >= 0", name="gross_weight_non_negative"
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
    def validate_prices(self, key: str, value: Decimal | None) -> Decimal | None:
        """Valida que los precios sean no negativos."""
        return DecimalValidator.validate_non_negative(value, field_name=key)

    @validates("stock_quantity", "minimum_stock")
    def validate_stock(self, key: str, value: Decimal | None) -> Decimal | None:
        """Valida stock (solo para ARTICLE)."""
        if value is not None and self.product_type == ProductType.SERVICE:
            raise ValueError(f"{key} should be NULL for SERVICE products")
        return DecimalValidator.validate_non_negative(value, field_name=key)

    @validates("net_weight", "gross_weight")
    def validate_weights(self, key: str, value: Decimal | None) -> Decimal | None:
        """Valida pesos."""
        return DecimalValidator.validate_non_negative(value, field_name=key)

    @validates("margin_percentage")
    def validate_margin(self, key: str, value: Decimal | None) -> Decimal | None:
        """Valida margen de ganancia."""
        if value is not None and (value < -100 or value > 1000):
            raise ValueError("Margin percentage must be between -100% and 1000%")
        return value

    # ========== COMPUTED PROPERTIES ==========
    @property
    def effective_cost(self) -> Decimal | None:
        """Retorna el costo efectivo del producto."""
        if (
            self.product_type == ProductType.NOMENCLATURE
            and self.price_calculation_mode == PriceCalculationMode.FROM_COMPONENTS
        ):
            return self.calculated_cost
        return self.cost_price

    @property
    def effective_price(self) -> Decimal | None:
        """Retorna el precio de venta efectivo."""
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
    def calculated_cost(self) -> Decimal | None:
        """Calcula el costo sumando los costos de todos los componentes."""
        if not self.components:
            return None
        total = Decimal("0.00")
        for comp in self.components:
            if comp.component and comp.component.effective_cost:
                total += comp.component.effective_cost * comp.quantity
        return total if total > 0 else None

    @property
    def calculated_price(self) -> Decimal | None:
        """Calcula el precio sumando los precios de todos los componentes."""
        if not self.components:
            return None
        total = Decimal("0.00")
        for comp in self.components:
            if comp.component and comp.component.effective_price:
                total += comp.component.effective_price * comp.quantity
        return total if total > 0 else None

    @property
    def margin(self) -> Decimal | None:
        """Calcula el margen absoluto (sale_price - cost_price)."""
        if self.effective_price and self.effective_cost:
            return self.effective_price - self.effective_cost
        return None

    @property
    def margin_percent(self) -> Decimal | None:
        """Calcula el margen porcentual."""
        if self.margin and self.effective_cost and self.effective_cost > 0:
            return (self.margin / self.effective_cost) * 100
        return None

    # ========== BOM METHODS ==========
    def get_bom_tree(
        self, level: int = 0, visited: set[int] | None = None
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
        """
        if visited is None:
            visited = set()

        if self.id in visited:
            raise ValueError(
                f"Circular reference detected in BOM: product {self.reference} (id={self.id})"
            )

        visited.add(self.id)

        tree: dict[str, Any] = {
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
                comp_tree["total_price"] = comp_tree["unit_price"] * comp_tree["quantity"]
                tree["components"].append(comp_tree)

        return tree

    def get_flat_bom(self, visited: set[int] | None = None) -> list[dict[str, Any]]:
        """Retorna una lista plana de todos los componentes (todos los niveles)."""
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

    def get_total_weight(self) -> Decimal | None:
        """Calcula el peso total incluyendo todos los componentes."""
        if self.product_type == ProductType.SERVICE:
            return None

        if self.product_type == ProductType.ARTICLE:
            return self.net_weight

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
        self, component_id: int, visited: set[int] | None = None
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

        session = Session.object_session(self)
        if session:
            component = session.get(Product, component_id)
            if component:
                try:
                    component.get_bom_tree(visited=visited)
                except ValueError as e:
                    raise ValueError(
                        f"Adding component {component.reference} would create a cycle: {str(e)}"
                    ) from e

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
    """

    __tablename__ = "product_components"

    # ========== PRIMARY KEY ==========
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ========== FOREIGN KEYS ==========
    parent_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True,
        comment="Parent product (NOMENCLATURE) containing this component",
    )
    component_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        index=True,
        comment="Component product (any type)",
    )

    # ========== QUANTITY ==========
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(15, 3),
        default=Decimal("1.000"),
        comment="Quantity of component required",
    )

    # ========== ADDITIONAL ==========
    notes: Mapped[str | None] = mapped_column(
        Text, comment="Notes about this component usage"
    )

    # ========== RELATIONSHIPS ==========
    parent: Mapped["Product"] = relationship(
        "Product", foreign_keys=[parent_id], back_populates="components"
    )
    component: Mapped["Product"] = relationship(
        "Product",
        foreign_keys=[component_id],
        back_populates="parent_components",
        lazy="joined",
    )

    # ========== TABLE CONSTRAINTS ==========
    __table_args__ = (
        UniqueConstraint("parent_id", "component_id", name="uq_parent_component"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("parent_id != component_id", name="no_self_reference"),
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
