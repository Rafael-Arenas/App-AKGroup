"""
Tests for Product, ProductComponent, ProductType, and PriceCalculationMode from core.products.

This module contains comprehensive tests for the unified product system,
including CRUD operations, validators, BOM relationships, pricing calculations, and edge cases.

Test Coverage:
    ProductType:
        - Enum values (ARTICLE, NOMENCLATURE, SERVICE)

    PriceCalculationMode:
        - Enum values (MANUAL, FROM_COMPONENTS, FROM_COST_MARGIN)

    Product:
        - Basic CRUD operations
        - Field validation (reference, prices, stock, weights, margins)
        - Product types (ARTICLE, NOMENCLATURE, SERVICE)
        - Pricing modes and calculations
        - Computed properties (effective_cost, effective_price, margins)
        - Stock management
        - Physical properties
        - Mixins (Timestamp, Audit, Active)
        - Relationships (family_type, matter, sales_type, company)

    ProductComponent:
        - BOM (Bill of Materials) structure
        - Hierarchical relationships
        - Quantity validation
        - Self-reference prevention
        - Cycle detection
        - BOM tree generation
        - Flat BOM calculation
        - Weight calculations
"""

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.core.products import (
    PriceCalculationMode,
    Product,
    ProductComponent,
    ProductType,
)


# ============= PRODUCT TYPE ENUM TESTS =============


class TestProductTypeEnum:
    """Tests for ProductType enum."""

    def test_product_type_enum_values(self):
        """Test that ProductType has all expected values."""
        assert ProductType.ARTICLE == "article"
        assert ProductType.NOMENCLATURE == "nomenclature"
        assert ProductType.SERVICE == "service"

    def test_product_type_enum_members(self):
        """Test enum members list."""
        product_types = list(ProductType)
        assert len(product_types) == 3
        assert ProductType.ARTICLE in product_types
        assert ProductType.NOMENCLATURE in product_types
        assert ProductType.SERVICE in product_types


class TestPriceCalculationModeEnum:
    """Tests for PriceCalculationMode enum."""

    def test_price_calculation_mode_enum_values(self):
        """Test that PriceCalculationMode has all expected values."""
        assert PriceCalculationMode.MANUAL == "manual"
        assert PriceCalculationMode.FROM_COMPONENTS == "from_components"
        assert PriceCalculationMode.FROM_COST_MARGIN == "from_cost_margin"

    def test_price_calculation_mode_enum_members(self):
        """Test enum members list."""
        modes = list(PriceCalculationMode)
        assert len(modes) == 3


# ============= PRODUCT MODEL TESTS =============


class TestProductCreation:
    """Tests for Product model instantiation and creation."""

    def test_create_article_with_valid_data(self, session):
        """Test creating an ARTICLE product with complete data."""
        # Arrange & Act
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-001",
            designation_es="Producto terminado",
            designation_en="Finished product",
            cost_price=Decimal("100.00"),
            sale_price=Decimal("150.00"),
            stock_quantity=Decimal("50.000"),
            minimum_stock=Decimal("10.000"),
            net_weight=Decimal("2.500"),
        )
        session.add(product)
        session.commit()
        session.refresh(product)

        # Assert
        assert product.id is not None
        assert product.product_type == ProductType.ARTICLE
        assert product.reference == "ART-001"
        assert product.designation_es == "Producto terminado"
        assert product.cost_price == Decimal("100.00")
        assert product.sale_price == Decimal("150.00")
        assert product.stock_quantity == Decimal("50.000")

    def test_create_nomenclature_with_valid_data(self, session):
        """Test creating a NOMENCLATURE product (kit/assembly)."""
        # Arrange & Act
        product = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="NOM-001",
            designation_es="Kit completo",
            price_calculation_mode=PriceCalculationMode.FROM_COMPONENTS,
        )
        session.add(product)
        session.commit()
        session.refresh(product)

        # Assert
        assert product.product_type == ProductType.NOMENCLATURE
        assert product.reference == "NOM-001"
        assert product.price_calculation_mode == PriceCalculationMode.FROM_COMPONENTS

    def test_create_service_with_valid_data(self, session):
        """Test creating a SERVICE product."""
        # Arrange & Act
        product = Product(
            product_type=ProductType.SERVICE,
            reference="SRV-001",
            designation_es="Servicio de instalación",
            sale_price=Decimal("200.00"),
            # Don't set stock_quantity for SERVICE - it should be None or 0 by default
        )
        session.add(product)
        session.commit()
        session.refresh(product)

        # Assert
        assert product.product_type == ProductType.SERVICE
        # Services can have None or default 0.000 stock_quantity
        assert product.stock_quantity is None or product.stock_quantity == Decimal("0.000")

    def test_create_product_minimal_fields(self, session):
        """Test creating product with only required fields."""
        # Arrange & Act
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="MIN-001",
        )
        session.add(product)
        session.commit()
        session.refresh(product)

        # Assert
        assert product.id is not None
        assert product.reference == "MIN-001"
        assert product.is_active is True  # Default from ActiveMixin


class TestProductValidation:
    """Tests for Product field validators."""

    def test_reference_validator_converts_to_uppercase(self, session):
        """Test that reference is automatically converted to uppercase."""
        # Arrange & Act
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="art-001",  # lowercase
        )
        session.add(product)
        session.commit()
        session.refresh(product)

        # Assert
        assert product.reference == "ART-001"  # Uppercase

    def test_reference_validator_strips_whitespace(self, session):
        """Test that reference strips whitespace."""
        # Arrange & Act
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="  ART-001  ",
        )
        session.add(product)
        session.commit()
        session.refresh(product)

        # Assert
        assert product.reference == "ART-001"

    def test_reference_validator_minimum_length(self, session):
        """Test that reference must be at least 2 characters."""
        with pytest.raises(ValueError, match="at least 2 characters"):
            product = Product(
                product_type=ProductType.ARTICLE,
                reference="A",
            )
            session.add(product)
            session.flush()

    def test_reference_must_be_unique(self, session):
        """Test that reference must be unique."""
        # Arrange - Create first product
        product1 = Product(
            product_type=ProductType.ARTICLE,
            reference="DUP-001",
        )
        session.add(product1)
        session.commit()

        # Act & Assert - Try to create duplicate
        with pytest.raises(IntegrityError):
            product2 = Product(
                product_type=ProductType.ARTICLE,
                reference="DUP-001",  # Duplicate
            )
            session.add(product2)
            session.commit()

    def test_price_validators_reject_negative(self, session):
        """Test that price validators reject negative values."""
        # Test purchase_price
        with pytest.raises(ValueError, match="cannot be negative"):
            product = Product(
                product_type=ProductType.ARTICLE,
                reference="TEST-001",
                purchase_price=Decimal("-10.00"),
            )
            session.add(product)
            session.flush()

        session.rollback()

        # Test cost_price
        with pytest.raises(ValueError, match="cannot be negative"):
            product = Product(
                product_type=ProductType.ARTICLE,
                reference="TEST-002",
                cost_price=Decimal("-10.00"),
            )
            session.add(product)
            session.flush()

    def test_stock_validator_service_cannot_have_stock(self, session):
        """Test that SERVICE products cannot have stock."""
        with pytest.raises(ValueError, match="should be NULL for SERVICE"):
            product = Product(
                product_type=ProductType.SERVICE,
                reference="SRV-001",
                stock_quantity=Decimal("10.000"),
            )
            session.add(product)
            session.flush()

    def test_stock_validator_rejects_negative(self, session):
        """Test that stock cannot be negative."""
        with pytest.raises(ValueError, match="cannot be negative"):
            product = Product(
                product_type=ProductType.ARTICLE,
                reference="TEST-001",
                stock_quantity=Decimal("-5.000"),
            )
            session.add(product)
            session.flush()

    def test_weight_validators_reject_negative(self, session):
        """Test that weight validators reject negative values."""
        with pytest.raises(ValueError, match="cannot be negative"):
            product = Product(
                product_type=ProductType.ARTICLE,
                reference="TEST-001",
                net_weight=Decimal("-1.000"),
            )
            session.add(product)
            session.flush()

    def test_margin_validator_range(self, session):
        """Test that margin_percentage is within valid range."""
        # Valid margins
        for margin in [Decimal("0"), Decimal("50.00"), Decimal("100.00")]:
            product = Product(
                product_type=ProductType.ARTICLE,
                reference=f"MAR-{int(margin)}",
                margin_percentage=margin,
            )
            session.add(product)
            session.commit()
            session.rollback()

        # Invalid margin (too high)
        with pytest.raises(ValueError, match="between -100% and 1000%"):
            product = Product(
                product_type=ProductType.ARTICLE,
                reference="MAR-HIGH",
                margin_percentage=Decimal("1500.00"),
            )
            session.add(product)
            session.flush()


class TestProductTypes:
    """Tests for different product types."""

    def test_article_can_have_stock(self, session):
        """Test that ARTICLE can have stock."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-001",
            stock_quantity=Decimal("100.000"),
        )
        session.add(product)
        session.commit()

        assert product.stock_quantity == Decimal("100.000")

    def test_nomenclature_can_have_components(self, session):
        """Test that NOMENCLATURE can have BOM components."""
        # Arrange - Create parent and component
        parent = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="NOM-001",
        )
        component = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-001",
        )
        session.add_all([parent, component])
        session.commit()

        # Act - Add component to BOM
        bom = ProductComponent(
            parent_id=parent.id,
            component_id=component.id,
            quantity=Decimal("2.000"),
        )
        session.add(bom)
        session.commit()

        # Assert
        session.refresh(parent)
        assert len(parent.components) == 1
        assert parent.components[0].component.reference == "ART-001"

    def test_service_has_no_physical_properties(self, session):
        """Test that SERVICE typically has no stock or weight."""
        product = Product(
            product_type=ProductType.SERVICE,
            reference="SRV-001",
            # Don't explicitly set stock_quantity or net_weight - should be None by default
        )
        session.add(product)
        session.commit()

        assert product.stock_quantity is None or product.stock_quantity == Decimal("0.000")
        assert product.net_weight is None


class TestProductPricing:
    """Tests for product pricing and calculation modes."""

    def test_manual_pricing_mode(self, session):
        """Test MANUAL pricing mode uses sale_price directly."""
        # Arrange & Act
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="MAN-001",
            sale_price=Decimal("100.00"),
            price_calculation_mode=PriceCalculationMode.MANUAL,
        )
        session.add(product)
        session.commit()

        # Assert
        assert product.effective_price == Decimal("100.00")

    def test_from_cost_margin_pricing_mode(self, session):
        """Test FROM_COST_MARGIN calculates price from cost + margin."""
        # Arrange & Act
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="MAR-001",
            cost_price=Decimal("100.00"),
            margin_percentage=Decimal("50.00"),  # 50%
            price_calculation_mode=PriceCalculationMode.FROM_COST_MARGIN,
        )
        session.add(product)
        session.commit()

        # Assert - 100 + 50% = 150
        assert product.effective_price == Decimal("150.00")

    def test_from_components_pricing_mode(self, session):
        """Test FROM_COMPONENTS calculates price from BOM components."""
        # Arrange - Create components
        comp1 = Product(
            product_type=ProductType.ARTICLE,
            reference="COMP-001",
            sale_price=Decimal("50.00"),
        )
        comp2 = Product(
            product_type=ProductType.ARTICLE,
            reference="COMP-002",
            sale_price=Decimal("30.00"),
        )

        # Create nomenclature
        parent = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="NOM-001",
            price_calculation_mode=PriceCalculationMode.FROM_COMPONENTS,
        )
        session.add_all([comp1, comp2, parent])
        session.commit()

        # Act - Add components to BOM
        bom1 = ProductComponent(parent_id=parent.id, component_id=comp1.id, quantity=Decimal("2.000"))
        bom2 = ProductComponent(parent_id=parent.id, component_id=comp2.id, quantity=Decimal("1.000"))
        session.add_all([bom1, bom2])
        session.commit()
        session.refresh(parent)

        # Assert - (50 * 2) + (30 * 1) = 130
        assert parent.calculated_price == Decimal("130.00")
        assert parent.effective_price == Decimal("130.00")


class TestProductComputedProperties:
    """Tests for computed properties."""

    def test_margin_calculation(self, session):
        """Test margin property calculates correctly."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TEST-001",
            cost_price=Decimal("100.00"),
            sale_price=Decimal("150.00"),
        )
        session.add(product)
        session.commit()

        # Assert - margin = sale - cost = 50
        assert product.margin == Decimal("50.00")

    def test_margin_percent_calculation(self, session):
        """Test margin_percent property calculates correctly."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TEST-001",
            cost_price=Decimal("100.00"),
            sale_price=Decimal("150.00"),
        )
        session.add(product)
        session.commit()

        # Assert - margin % = (50 / 100) * 100 = 50%
        assert product.margin_percent == Decimal("50.00")

    def test_effective_cost_for_nomenclature(self, session):
        """Test effective_cost for NOMENCLATURE sums component costs."""
        # Arrange
        comp = Product(
            product_type=ProductType.ARTICLE,
            reference="COMP-001",
            cost_price=Decimal("20.00"),
        )
        parent = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="NOM-001",
            price_calculation_mode=PriceCalculationMode.FROM_COMPONENTS,
        )
        session.add_all([comp, parent])
        session.commit()

        bom = ProductComponent(parent_id=parent.id, component_id=comp.id, quantity=Decimal("3.000"))
        session.add(bom)
        session.commit()
        session.refresh(parent)

        # Assert - 20 * 3 = 60
        assert parent.effective_cost == Decimal("60.00")


class TestProductBOM:
    """Tests for Bill of Materials (BOM) functionality."""

    def test_add_component_to_bom(self, session):
        """Test adding a component to product BOM."""
        # Arrange
        parent = Product(product_type=ProductType.NOMENCLATURE, reference="PAR-001")
        component = Product(product_type=ProductType.ARTICLE, reference="COM-001")
        session.add_all([parent, component])
        session.commit()

        # Act
        bom = ProductComponent(
            parent_id=parent.id,
            component_id=component.id,
            quantity=Decimal("5.000"),
        )
        session.add(bom)
        session.commit()

        # Assert
        session.refresh(parent)
        assert len(parent.components) == 1
        assert parent.components[0].quantity == Decimal("5.000")

    def test_bom_tree_single_level(self, session):
        """Test get_bom_tree() for single-level BOM."""
        # Arrange
        parent = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="PAR-001",
            designation_es="Parent",
        )
        comp = Product(
            product_type=ProductType.ARTICLE,
            reference="COM-001",
            designation_es="Component",
            cost_price=Decimal("10.00"),
            sale_price=Decimal("15.00"),
        )
        session.add_all([parent, comp])
        session.commit()

        bom = ProductComponent(parent_id=parent.id, component_id=comp.id, quantity=Decimal("2.000"))
        session.add(bom)
        session.commit()
        session.refresh(parent)

        # Act
        tree = parent.get_bom_tree()

        # Assert
        assert tree["reference"] == "PAR-001"
        assert tree["level"] == 0
        assert len(tree["components"]) == 1
        assert tree["components"][0]["reference"] == "COM-001"
        assert tree["components"][0]["quantity"] == 2.0

    def test_bom_tree_multi_level(self, session):
        """Test get_bom_tree() for hierarchical multi-level BOM."""
        # Arrange - Create 3-level hierarchy
        level2_comp = Product(product_type=ProductType.ARTICLE, reference="L2-001")
        level1_nom = Product(product_type=ProductType.NOMENCLATURE, reference="L1-001")
        level0_nom = Product(product_type=ProductType.NOMENCLATURE, reference="L0-001")

        session.add_all([level2_comp, level1_nom, level0_nom])
        session.commit()

        # Build hierarchy
        bom_l1 = ProductComponent(parent_id=level1_nom.id, component_id=level2_comp.id, quantity=Decimal("1.000"))
        bom_l0 = ProductComponent(parent_id=level0_nom.id, component_id=level1_nom.id, quantity=Decimal("2.000"))
        session.add_all([bom_l1, bom_l0])
        session.commit()
        session.refresh(level0_nom)

        # Act
        tree = level0_nom.get_bom_tree()

        # Assert
        assert tree["level"] == 0
        assert len(tree["components"]) == 1
        assert tree["components"][0]["level"] == 1
        assert len(tree["components"][0]["components"]) == 1
        assert tree["components"][0]["components"][0]["level"] == 2

    def test_flat_bom_calculation(self, session):
        """Test get_flat_bom() consolidates all components."""
        # Arrange - Create hierarchy (use 2+ character references)
        comp_a = Product(
            product_type=ProductType.ARTICLE,
            reference="CA",  # Changed from "A" to "CA"
            cost_price=Decimal("10.00"),
        )
        comp_b = Product(
            product_type=ProductType.ARTICLE,
            reference="CB",  # Changed from "B" to "CB"
            cost_price=Decimal("5.00"),
        )
        sub_nom = Product(product_type=ProductType.NOMENCLATURE, reference="SUB")
        main_nom = Product(product_type=ProductType.NOMENCLATURE, reference="MAIN")

        session.add_all([comp_a, comp_b, sub_nom, main_nom])
        session.commit()

        # SUB contains: 2x CA, 1x CB
        bom1 = ProductComponent(parent_id=sub_nom.id, component_id=comp_a.id, quantity=Decimal("2.000"))
        bom2 = ProductComponent(parent_id=sub_nom.id, component_id=comp_b.id, quantity=Decimal("1.000"))

        # MAIN contains: 1x SUB, 1x CA
        bom3 = ProductComponent(parent_id=main_nom.id, component_id=sub_nom.id, quantity=Decimal("1.000"))
        bom4 = ProductComponent(parent_id=main_nom.id, component_id=comp_a.id, quantity=Decimal("1.000"))

        session.add_all([bom1, bom2, bom3, bom4])
        session.commit()
        session.refresh(main_nom)

        # Act
        flat = main_nom.get_flat_bom()

        # Assert - Should have CA (2+1=3) and CB (1)
        flat_dict = {item["reference"]: item["quantity"] for item in flat}
        assert flat_dict["CA"] == Decimal("3.000")  # 2 from SUB + 1 direct
        assert flat_dict["CB"] == Decimal("1.000")  # 1 from SUB

    def test_validate_no_cycles_direct(self, session):
        """Test that adding product as its own component is prevented."""
        # Arrange
        product = Product(product_type=ProductType.NOMENCLATURE, reference="SELF")
        session.add(product)
        session.commit()

        # Act & Assert
        with pytest.raises(ValueError, match="cannot be a component of itself"):
            bom = ProductComponent(
                parent_id=product.id,
                component_id=product.id,  # Self-reference
                quantity=Decimal("1.000"),
            )
            session.add(bom)
            session.flush()

    def test_validate_no_cycles_indirect(self, session):
        """Test that circular BOM references are detected."""
        # Arrange - PA -> PB -> PC -> PA (cycle) - use 2+ character references
        prod_a = Product(product_type=ProductType.NOMENCLATURE, reference="PA")
        prod_b = Product(product_type=ProductType.NOMENCLATURE, reference="PB")
        prod_c = Product(product_type=ProductType.NOMENCLATURE, reference="PC")

        session.add_all([prod_a, prod_b, prod_c])
        session.commit()

        # Create: PA -> PB, PB -> PC
        bom1 = ProductComponent(parent_id=prod_a.id, component_id=prod_b.id, quantity=Decimal("1.000"))
        bom2 = ProductComponent(parent_id=prod_b.id, component_id=prod_c.id, quantity=Decimal("1.000"))
        session.add_all([bom1, bom2])
        session.commit()

        # Act & Assert - Try to add PC -> PA (creates cycle)
        session.refresh(prod_c)
        with pytest.raises(ValueError, match="cycle"):
            prod_c.validate_no_cycles(prod_a.id)


class TestProductWeight:
    """Tests for weight calculations."""

    def test_get_total_weight_article(self, session):
        """Test get_total_weight() for ARTICLE returns net_weight."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-001",
            net_weight=Decimal("5.000"),
        )
        session.add(product)
        session.commit()

        assert product.get_total_weight() == Decimal("5.000")

    def test_get_total_weight_service_returns_none(self, session):
        """Test get_total_weight() for SERVICE returns None."""
        product = Product(
            product_type=ProductType.SERVICE,
            reference="SRV-001",
        )
        session.add(product)
        session.commit()

        assert product.get_total_weight() is None

    def test_get_total_weight_nomenclature_sums_components(self, session):
        """Test get_total_weight() for NOMENCLATURE sums component weights."""
        # Arrange
        comp1 = Product(
            product_type=ProductType.ARTICLE,
            reference="C1",
            net_weight=Decimal("2.000"),
        )
        comp2 = Product(
            product_type=ProductType.ARTICLE,
            reference="C2",
            net_weight=Decimal("3.000"),
        )
        parent = Product(product_type=ProductType.NOMENCLATURE, reference="PAR")

        session.add_all([comp1, comp2, parent])
        session.commit()

        bom1 = ProductComponent(parent_id=parent.id, component_id=comp1.id, quantity=Decimal("2.000"))
        bom2 = ProductComponent(parent_id=parent.id, component_id=comp2.id, quantity=Decimal("1.000"))
        session.add_all([bom1, bom2])
        session.commit()
        session.refresh(parent)

        # Act & Assert - (2 * 2) + (3 * 1) = 7
        assert parent.get_total_weight() == Decimal("7.000")


class TestProductRelationships:
    """Tests for Product relationships."""

    def test_family_type_relationship(self, session, sample_family_type):
        """Test relationship with FamilyType."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TEST-001",
            family_type_id=sample_family_type.id,
        )
        session.add(product)
        session.commit()
        session.refresh(product)

        assert product.family_type is not None
        assert product.family_type.id == sample_family_type.id

    def test_matter_relationship(self, session, sample_matter):
        """Test relationship with Matter."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TEST-001",
            matter_id=sample_matter.id,
        )
        session.add(product)
        session.commit()
        session.refresh(product)

        assert product.matter is not None
        assert product.matter.id == sample_matter.id

    def test_sales_type_relationship(self, session, sample_sales_type):
        """Test relationship with SalesType."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TEST-001",
            sales_type_id=sample_sales_type.id,
        )
        session.add(product)
        session.commit()
        session.refresh(product)

        assert product.sales_type is not None
        assert product.sales_type.id == sample_sales_type.id


class TestProductMixins:
    """Tests for Product mixins."""

    def test_timestamp_mixin(self, session):
        """Test TimestampMixin creates timestamps."""
        product = Product(product_type=ProductType.ARTICLE, reference="TEST-001")
        session.add(product)
        session.commit()
        session.refresh(product)

        assert product.created_at is not None
        assert product.updated_at is not None

    def test_audit_mixin_sets_created_by(self, session):
        """Test AuditMixin sets created_by_id from session context."""
        product = Product(product_type=ProductType.ARTICLE, reference="TEST-001")
        session.add(product)
        session.commit()
        session.refresh(product)

        assert product.created_by_id == 1

    def test_active_mixin_default_true(self, session):
        """Test ActiveMixin defaults is_active to True."""
        product = Product(product_type=ProductType.ARTICLE, reference="TEST-001")
        session.add(product)
        session.commit()

        assert product.is_active is True


class TestProductRepr:
    """Tests for Product __repr__ method."""

    def test_repr_method(self, session):
        """Test string representation of Product."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TEST-001",
        )
        session.add(product)
        session.commit()
        session.refresh(product)

        repr_str = repr(product)
        assert "Product" in repr_str
        assert "article" in repr_str
        assert "TEST-001" in repr_str


# ============= PRODUCT COMPONENT TESTS =============


class TestProductComponentCreation:
    """Tests for ProductComponent model creation."""

    def test_create_component_with_valid_data(self, session):
        """Test creating ProductComponent with valid data."""
        # Arrange
        parent = Product(product_type=ProductType.NOMENCLATURE, reference="PAR")
        component = Product(product_type=ProductType.ARTICLE, reference="COM")
        session.add_all([parent, component])
        session.commit()

        # Act
        bom = ProductComponent(
            parent_id=parent.id,
            component_id=component.id,
            quantity=Decimal("3.000"),
            notes="Assembly instructions here",
        )
        session.add(bom)
        session.commit()
        session.refresh(bom)

        # Assert
        assert bom.id is not None
        assert bom.parent_id == parent.id
        assert bom.component_id == component.id
        assert bom.quantity == Decimal("3.000")
        assert bom.notes == "Assembly instructions here"

    def test_create_component_minimal_fields(self, session):
        """Test creating ProductComponent with only required fields."""
        parent = Product(product_type=ProductType.NOMENCLATURE, reference="PAR")
        component = Product(product_type=ProductType.ARTICLE, reference="COM")
        session.add_all([parent, component])
        session.commit()

        bom = ProductComponent(
            parent_id=parent.id,
            component_id=component.id,
            quantity=Decimal("1.000"),
        )
        session.add(bom)
        session.commit()

        assert bom.notes is None
        assert bom.quantity == Decimal("1.000")  # Default


class TestProductComponentValidation:
    """Tests for ProductComponent validators."""

    def test_quantity_must_be_positive(self, session):
        """Test that quantity must be greater than zero."""
        parent = Product(product_type=ProductType.NOMENCLATURE, reference="PAR")
        component = Product(product_type=ProductType.ARTICLE, reference="COM")
        session.add_all([parent, component])
        session.commit()

        # Test zero quantity
        with pytest.raises(ValueError, match="quantity must be positive"):
            bom = ProductComponent(
                parent_id=parent.id,
                component_id=component.id,
                quantity=Decimal("0.000"),
            )
            session.add(bom)
            session.flush()

        session.rollback()

        # Test negative quantity
        with pytest.raises(ValueError, match="quantity must be positive"):
            bom = ProductComponent(
                parent_id=parent.id,
                component_id=component.id,
                quantity=Decimal("-1.000"),
            )
            session.add(bom)
            session.flush()

    def test_no_self_reference_validation(self, session):
        """Test that product cannot be component of itself."""
        product = Product(product_type=ProductType.NOMENCLATURE, reference="SELF")
        session.add(product)
        session.commit()

        with pytest.raises(ValueError, match="cannot be a component of itself"):
            bom = ProductComponent(
                parent_id=product.id,
                component_id=product.id,
                quantity=Decimal("1.000"),
            )
            session.add(bom)
            session.flush()

    def test_unique_constraint_parent_component(self, session):
        """Test that same component cannot be added twice to same parent."""
        parent = Product(product_type=ProductType.NOMENCLATURE, reference="PAR")
        component = Product(product_type=ProductType.ARTICLE, reference="COM")
        session.add_all([parent, component])
        session.commit()

        # Add first time
        bom1 = ProductComponent(
            parent_id=parent.id,
            component_id=component.id,
            quantity=Decimal("1.000"),
        )
        session.add(bom1)
        session.commit()

        # Try to add again
        with pytest.raises(IntegrityError):
            bom2 = ProductComponent(
                parent_id=parent.id,
                component_id=component.id,  # Same component again
                quantity=Decimal("2.000"),
            )
            session.add(bom2)
            session.commit()


class TestProductComponentRelationships:
    """Tests for ProductComponent relationships."""

    def test_parent_relationship(self, session):
        """Test relationship with parent Product."""
        parent = Product(product_type=ProductType.NOMENCLATURE, reference="PAR")
        component = Product(product_type=ProductType.ARTICLE, reference="COM")
        session.add_all([parent, component])
        session.commit()

        bom = ProductComponent(
            parent_id=parent.id,
            component_id=component.id,
            quantity=Decimal("1.000"),
        )
        session.add(bom)
        session.commit()
        session.refresh(bom)

        assert bom.parent is not None
        assert bom.parent.reference == "PAR"

    def test_component_relationship(self, session):
        """Test relationship with component Product."""
        parent = Product(product_type=ProductType.NOMENCLATURE, reference="PAR")
        component = Product(product_type=ProductType.ARTICLE, reference="COM")
        session.add_all([parent, component])
        session.commit()

        bom = ProductComponent(
            parent_id=parent.id,
            component_id=component.id,
            quantity=Decimal("1.000"),
        )
        session.add(bom)
        session.commit()
        session.refresh(bom)

        assert bom.component is not None
        assert bom.component.reference == "COM"

    def test_cascade_delete_with_parent(self, session):
        """Test that deleting parent deletes BOM entries."""
        parent = Product(product_type=ProductType.NOMENCLATURE, reference="PAR")
        component = Product(product_type=ProductType.ARTICLE, reference="COM")
        session.add_all([parent, component])
        session.commit()

        bom = ProductComponent(
            parent_id=parent.id,
            component_id=component.id,
            quantity=Decimal("1.000"),
        )
        session.add(bom)
        session.commit()
        bom_id = bom.id

        # Delete parent
        session.delete(parent)
        session.commit()

        # BOM entry should be deleted
        deleted_bom = session.query(ProductComponent).filter_by(id=bom_id).first()
        assert deleted_bom is None


class TestProductComponentRepr:
    """Tests for ProductComponent __repr__ method."""

    def test_repr_method(self, session):
        """Test string representation of ProductComponent."""
        parent = Product(product_type=ProductType.NOMENCLATURE, reference="PAR")
        component = Product(product_type=ProductType.ARTICLE, reference="COM")
        session.add_all([parent, component])
        session.commit()

        bom = ProductComponent(
            parent_id=parent.id,
            component_id=component.id,
            quantity=Decimal("5.000"),
        )
        session.add(bom)
        session.commit()
        session.refresh(bom)

        repr_str = repr(bom)
        assert "ProductComponent" in repr_str
        assert str(parent.id) in repr_str
        assert str(component.id) in repr_str
