"""
Unit tests for Product and ProductComponent models.

Tests validation, BOM hierarchy, price calculation, and cycle detection.
"""

import pytest
from decimal import Decimal

from models.core.products import (
    Product,
    ProductComponent,
    ProductType,
    PriceCalculationMode,
)


class TestProductType:
    """Test suite for ProductType enum."""

    def test_enum_values(self):
        """Test enum has correct values."""
        assert ProductType.ARTICLE.value == "article"
        assert ProductType.NOMENCLATURE.value == "nomenclature"
        assert ProductType.SERVICE.value == "service"


class TestPriceCalculationMode:
    """Test suite for PriceCalculationMode enum."""

    def test_enum_values(self):
        """Test enum has correct values."""
        assert PriceCalculationMode.MANUAL.value == "manual"
        assert PriceCalculationMode.FROM_COMPONENTS.value == "from_components"
        assert PriceCalculationMode.FROM_COST_MARGIN.value == "from_cost_margin"


class TestProduct:
    """Test suite for Product model."""

    def test_create_article(self, session):
        """Test creating an ARTICLE product."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-001",
            designation_es="Producto terminado",
            designation_en="Finished product",
            cost_price=Decimal("100.00"),
            sale_price=Decimal("150.00"),
            stock_quantity=Decimal("50.000"),
            family_type_id=1,
        )

        session.add(product)
        session.commit()

        assert product.id is not None
        assert product.product_type == ProductType.ARTICLE
        assert product.reference == "ART-001"
        assert product.cost_price == Decimal("100.00")
        assert product.stock_quantity == Decimal("50.000")

    def test_create_nomenclature(self, session):
        """Test creating a NOMENCLATURE product."""
        product = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="NOM-001",
            designation_es="Kit completo",
            price_calculation_mode=PriceCalculationMode.FROM_COMPONENTS,
            family_type_id=1,
        )

        session.add(product)
        session.commit()

        assert product.id is not None
        assert product.product_type == ProductType.NOMENCLATURE
        assert (
            product.price_calculation_mode == PriceCalculationMode.FROM_COMPONENTS
        )

    def test_create_service(self, session):
        """Test creating a SERVICE product."""
        product = Product(
            product_type=ProductType.SERVICE,
            reference="SRV-001",
            designation_es="Servicio de consultoría",
            sale_price=Decimal("500.00"),
            family_type_id=1,
        )

        session.add(product)
        session.commit()

        assert product.id is not None
        assert product.product_type == ProductType.SERVICE
        # Services should not have stock
        assert product.stock_quantity is None or product.stock_quantity == Decimal(
            "0.000"
        )

    def test_reference_validation(self, session):
        """Test reference validation."""
        # Valid reference (uppercase conversion)
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="art-001",
            family_type_id=1,
        )
        assert product.reference == "ART-001"

        # Invalid: too short
        with pytest.raises(ValueError, match="at least 2 characters"):
            product = Product(
                product_type=ProductType.ARTICLE,
                reference="A",
                family_type_id=1,
            )
            session.add(product)
            session.flush()

        # Invalid: empty
        with pytest.raises(ValueError, match="at least 2 characters"):
            product = Product(
                product_type=ProductType.ARTICLE,
                reference="",
                family_type_id=1,
            )
            session.add(product)
            session.flush()

    def test_price_validation(self, session):
        """Test price validation."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TST-001",
            purchase_price=Decimal("80.00"),
            cost_price=Decimal("100.00"),
            sale_price=Decimal("150.00"),
            family_type_id=1,
        )

        assert product.purchase_price == Decimal("80.00")
        assert product.cost_price == Decimal("100.00")
        assert product.sale_price == Decimal("150.00")

        # Invalid: negative prices
        with pytest.raises(ValueError):
            product.purchase_price = Decimal("-10.00")

        with pytest.raises(ValueError):
            product.cost_price = Decimal("-10.00")

        with pytest.raises(ValueError):
            product.sale_price = Decimal("-10.00")

    def test_stock_validation(self, session):
        """Test stock validation."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TST-002",
            stock_quantity=Decimal("100.000"),
            minimum_stock=Decimal("10.000"),
            family_type_id=1,
        )

        assert product.stock_quantity == Decimal("100.000")
        assert product.minimum_stock == Decimal("10.000")

        # Invalid: negative stock
        with pytest.raises(ValueError):
            product.stock_quantity = Decimal("-5.000")

        with pytest.raises(ValueError):
            product.minimum_stock = Decimal("-1.000")

    def test_margin_percentage_validation(self, session):
        """Test margin percentage validation."""
        # Valid margins
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TST-003",
            margin_percentage=Decimal("50.00"),
            family_type_id=1,
        )
        assert product.margin_percentage == Decimal("50.00")

        # Edge cases
        product.margin_percentage = Decimal("-50.00")  # Loss
        assert product.margin_percentage == Decimal("-50.00")

        product.margin_percentage = Decimal("500.00")  # High margin
        assert product.margin_percentage == Decimal("500.00")

        # Invalid: too low
        with pytest.raises(ValueError, match="between -100% and 1000%"):
            product.margin_percentage = Decimal("-150.00")

        # Invalid: too high
        with pytest.raises(ValueError, match="between -100% and 1000%"):
            product.margin_percentage = Decimal("1500.00")

    def test_weight_validation(self, session):
        """Test weight validation."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TST-004",
            net_weight=Decimal("5.500"),
            gross_weight=Decimal("6.000"),
            family_type_id=1,
        )

        assert product.net_weight == Decimal("5.500")
        assert product.gross_weight == Decimal("6.000")

        # Invalid: negative weights
        with pytest.raises(ValueError):
            product.net_weight = Decimal("-1.000")

        with pytest.raises(ValueError):
            product.gross_weight = Decimal("-2.000")

    def test_effective_cost_property(self, session):
        """Test effective_cost property."""
        # Manual mode: returns cost_price
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TST-005",
            cost_price=Decimal("100.00"),
            price_calculation_mode=PriceCalculationMode.MANUAL,
            family_type_id=1,
        )

        assert product.effective_cost == Decimal("100.00")

    def test_effective_price_manual(self, session):
        """Test effective_price with MANUAL mode."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TST-006",
            sale_price=Decimal("150.00"),
            price_calculation_mode=PriceCalculationMode.MANUAL,
            family_type_id=1,
        )

        assert product.effective_price == Decimal("150.00")

    def test_effective_price_from_cost_margin(self, session):
        """Test effective_price with FROM_COST_MARGIN mode."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TST-007",
            cost_price=Decimal("100.00"),
            margin_percentage=Decimal("50.00"),  # 50% margin
            price_calculation_mode=PriceCalculationMode.FROM_COST_MARGIN,
            family_type_id=1,
        )

        # 100 + 50% = 150
        assert product.effective_price == Decimal("150.00")

    def test_margin_property(self, session):
        """Test margin calculation."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TST-008",
            cost_price=Decimal("100.00"),
            sale_price=Decimal("150.00"),
            price_calculation_mode=PriceCalculationMode.MANUAL,
            family_type_id=1,
        )

        # 150 - 100 = 50
        assert product.margin == Decimal("50.00")

    def test_margin_percent_property(self, session):
        """Test margin_percent calculation."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TST-009",
            cost_price=Decimal("100.00"),
            sale_price=Decimal("150.00"),
            price_calculation_mode=PriceCalculationMode.MANUAL,
            family_type_id=1,
        )

        # (150 - 100) / 100 * 100 = 50%
        assert product.margin_percent == Decimal("50.00")

    def test_get_total_weight_article(self, session):
        """Test get_total_weight for ARTICLE."""
        product = Product(
            product_type=ProductType.ARTICLE,
            reference="TST-010",
            net_weight=Decimal("5.500"),
            family_type_id=1,
        )

        assert product.get_total_weight() == Decimal("5.500")

    def test_get_total_weight_service(self, session):
        """Test get_total_weight for SERVICE."""
        product = Product(
            product_type=ProductType.SERVICE,
            reference="SRV-002",
            family_type_id=1,
        )

        # Services have no weight
        assert product.get_total_weight() is None

    def test_repr(self, session):
        """Test string representation."""
        product = Product(
            id=1,
            product_type=ProductType.ARTICLE,
            reference="ART-001",
            family_type_id=1,
        )

        repr_str = repr(product)
        assert "Product" in repr_str
        assert "article" in repr_str
        assert "ART-001" in repr_str


class TestProductComponent:
    """Test suite for ProductComponent model."""

    def test_create_component(self, session):
        """Test creating a product component."""
        component = ProductComponent(
            parent_id=1,
            component_id=2,
            quantity=Decimal("2.000"),
            notes="2 units per kit",
        )

        session.add(component)
        session.commit()

        assert component.id is not None
        assert component.quantity == Decimal("2.000")
        assert component.notes == "2 units per kit"

    def test_quantity_validation(self, session):
        """Test quantity must be positive."""
        # Valid quantity
        component = ProductComponent(
            parent_id=1,
            component_id=2,
            quantity=Decimal("5.000"),
        )
        assert component.quantity == Decimal("5.000")

        # Invalid: zero
        with pytest.raises(ValueError, match="must be positive"):
            component = ProductComponent(
                parent_id=1,
                component_id=2,
                quantity=Decimal("0.000"),
            )
            session.add(component)
            session.flush()

        # Invalid: negative
        with pytest.raises(ValueError, match="must be positive"):
            component = ProductComponent(
                parent_id=1,
                component_id=2,
                quantity=Decimal("-1.000"),
            )
            session.add(component)
            session.flush()

    def test_no_self_reference_validation(self, session):
        """Test product cannot be component of itself."""
        with pytest.raises(ValueError, match="cannot be a component of itself"):
            component = ProductComponent(
                parent_id=1,
                component_id=1,  # Same as parent
                quantity=Decimal("1.000"),
            )
            session.add(component)
            session.flush()

    def test_repr(self, session):
        """Test string representation."""
        component = ProductComponent(
            id=1,
            parent_id=10,
            component_id=20,
            quantity=Decimal("3.000"),
        )

        repr_str = repr(component)
        assert "ProductComponent" in repr_str
        assert "parent_id=10" in repr_str
        assert "component_id=20" in repr_str


class TestProductBOM:
    """Integration tests for Product BOM functionality."""

    def test_simple_bom(self, session):
        """Test simple one-level BOM."""
        # Create parent (nomenclature)
        parent = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="KIT-001",
            designation_es="Kit básico",
            price_calculation_mode=PriceCalculationMode.FROM_COMPONENTS,
            family_type_id=1,
        )
        session.add(parent)
        session.flush()

        # Create components
        comp1 = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-001",
            designation_es="Componente A",
            cost_price=Decimal("50.00"),
            sale_price=Decimal("75.00"),
            family_type_id=1,
        )
        comp2 = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-002",
            designation_es="Componente B",
            cost_price=Decimal("30.00"),
            sale_price=Decimal("45.00"),
            family_type_id=1,
        )
        session.add_all([comp1, comp2])
        session.flush()

        # Add to BOM
        bom1 = ProductComponent(
            parent_id=parent.id,
            component_id=comp1.id,
            quantity=Decimal("2.000"),
        )
        bom2 = ProductComponent(
            parent_id=parent.id,
            component_id=comp2.id,
            quantity=Decimal("3.000"),
        )
        session.add_all([bom1, bom2])
        session.commit()

        # Refresh to load relationships
        session.refresh(parent)

        # Verify BOM
        assert len(parent.components) == 2

    def test_calculated_cost(self, session):
        """Test cost calculation from components."""
        # Create parent
        parent = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="KIT-002",
            price_calculation_mode=PriceCalculationMode.FROM_COMPONENTS,
            family_type_id=1,
        )
        session.add(parent)
        session.flush()

        # Create components
        comp1 = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-010",
            cost_price=Decimal("50.00"),
            sale_price=Decimal("75.00"),
            family_type_id=1,
        )
        comp2 = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-011",
            cost_price=Decimal("30.00"),
            sale_price=Decimal("45.00"),
            family_type_id=1,
        )
        session.add_all([comp1, comp2])
        session.flush()

        # Add to BOM
        bom1 = ProductComponent(
            parent_id=parent.id,
            component_id=comp1.id,
            quantity=Decimal("2.000"),  # 2 * 50 = 100
        )
        bom2 = ProductComponent(
            parent_id=parent.id,
            component_id=comp2.id,
            quantity=Decimal("3.000"),  # 3 * 30 = 90
        )
        parent.components = [bom1, bom2]
        session.commit()

        # Refresh to load relationships
        session.refresh(parent)

        # Total cost: (2 * 50) + (3 * 30) = 100 + 90 = 190
        assert parent.calculated_cost == Decimal("190.00")

    def test_calculated_price(self, session):
        """Test price calculation from components."""
        # Create parent
        parent = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="KIT-003",
            price_calculation_mode=PriceCalculationMode.FROM_COMPONENTS,
            family_type_id=1,
        )
        session.add(parent)
        session.flush()

        # Create components
        comp1 = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-020",
            cost_price=Decimal("50.00"),
            sale_price=Decimal("75.00"),
            family_type_id=1,
        )
        comp2 = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-021",
            cost_price=Decimal("30.00"),
            sale_price=Decimal("45.00"),
            family_type_id=1,
        )
        session.add_all([comp1, comp2])
        session.flush()

        # Add to BOM
        bom1 = ProductComponent(
            parent_id=parent.id,
            component_id=comp1.id,
            quantity=Decimal("2.000"),  # 2 * 75 = 150
        )
        bom2 = ProductComponent(
            parent_id=parent.id,
            component_id=comp2.id,
            quantity=Decimal("3.000"),  # 3 * 45 = 135
        )
        parent.components = [bom1, bom2]
        session.commit()

        # Refresh
        session.refresh(parent)

        # Total price: (2 * 75) + (3 * 45) = 150 + 135 = 285
        assert parent.calculated_price == Decimal("285.00")

    def test_hierarchical_bom(self, session):
        """Test multi-level hierarchical BOM."""
        # Level 2: Base articles
        art1 = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-100",
            cost_price=Decimal("10.00"),
            sale_price=Decimal("15.00"),
            family_type_id=1,
        )
        art2 = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-101",
            cost_price=Decimal("20.00"),
            sale_price=Decimal("30.00"),
            family_type_id=1,
        )
        session.add_all([art1, art2])
        session.flush()

        # Level 1: Sub-assembly
        subasm = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="SUB-001",
            price_calculation_mode=PriceCalculationMode.FROM_COMPONENTS,
            family_type_id=1,
        )
        session.add(subasm)
        session.flush()

        # Add components to sub-assembly
        bom1 = ProductComponent(
            parent_id=subasm.id,
            component_id=art1.id,
            quantity=Decimal("2.000"),
        )
        bom2 = ProductComponent(
            parent_id=subasm.id,
            component_id=art2.id,
            quantity=Decimal("1.000"),
        )
        subasm.components = [bom1, bom2]
        session.flush()

        # Level 0: Main assembly
        main = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="MAIN-001",
            price_calculation_mode=PriceCalculationMode.FROM_COMPONENTS,
            family_type_id=1,
        )
        session.add(main)
        session.flush()

        # Add sub-assembly to main
        bom3 = ProductComponent(
            parent_id=main.id,
            component_id=subasm.id,
            quantity=Decimal("3.000"),
        )
        main.components = [bom3]
        session.commit()

        # Refresh all
        session.refresh(main)
        session.refresh(subasm)

        # Sub-assembly cost: (2 * 10) + (1 * 20) = 40
        assert subasm.calculated_cost == Decimal("40.00")

        # Main assembly cost: 3 * 40 = 120
        assert main.calculated_cost == Decimal("120.00")

    def test_get_bom_tree(self, session):
        """Test BOM tree generation."""
        # Create simple BOM
        parent = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="TREE-001",
            designation_es="Producto con BOM",
            family_type_id=1,
        )
        session.add(parent)
        session.flush()

        comp = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-200",
            designation_es="Componente",
            cost_price=Decimal("50.00"),
            sale_price=Decimal("75.00"),
            family_type_id=1,
        )
        session.add(comp)
        session.flush()

        bom = ProductComponent(
            parent_id=parent.id,
            component_id=comp.id,
            quantity=Decimal("2.000"),
        )
        parent.components = [bom]
        session.commit()

        # Refresh
        session.refresh(parent)

        # Get tree
        tree = parent.get_bom_tree()

        assert tree["reference"] == "TREE-001"
        assert tree["level"] == 0
        assert len(tree["components"]) == 1
        assert tree["components"][0]["reference"] == "ART-200"
        assert tree["components"][0]["quantity"] == 2.0

    def test_get_flat_bom(self, session):
        """Test flat BOM generation."""
        # Create hierarchical BOM
        art1 = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-300",
            cost_price=Decimal("10.00"),
            family_type_id=1,
        )
        session.add(art1)
        session.flush()

        subasm = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="SUB-002",
            family_type_id=1,
        )
        session.add(subasm)
        session.flush()

        bom1 = ProductComponent(
            parent_id=subasm.id,
            component_id=art1.id,
            quantity=Decimal("2.000"),
        )
        subasm.components = [bom1]
        session.flush()

        main = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="MAIN-002",
            family_type_id=1,
        )
        session.add(main)
        session.flush()

        bom2 = ProductComponent(
            parent_id=main.id,
            component_id=subasm.id,
            quantity=Decimal("3.000"),
        )
        main.components = [bom2]
        session.commit()

        # Refresh
        session.refresh(main)

        # Get flat BOM
        flat = main.get_flat_bom()

        # Should consolidate: 3 sub-assemblies * 2 articles = 6 articles total
        assert len(flat) > 0
        # Find ART-300 in flat list
        art_entry = next((item for item in flat if item["reference"] == "ART-300"), None)
        assert art_entry is not None

    def test_get_total_weight_nomenclature(self, session):
        """Test total weight calculation for nomenclature."""
        # Create components with weight
        comp1 = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-400",
            net_weight=Decimal("2.000"),
            family_type_id=1,
        )
        comp2 = Product(
            product_type=ProductType.ARTICLE,
            reference="ART-401",
            net_weight=Decimal("3.000"),
            family_type_id=1,
        )
        session.add_all([comp1, comp2])
        session.flush()

        # Create nomenclature
        parent = Product(
            product_type=ProductType.NOMENCLATURE,
            reference="KIT-WEIGHT",
            family_type_id=1,
        )
        session.add(parent)
        session.flush()

        # Add components
        bom1 = ProductComponent(
            parent_id=parent.id,
            component_id=comp1.id,
            quantity=Decimal("2.000"),  # 2 * 2kg = 4kg
        )
        bom2 = ProductComponent(
            parent_id=parent.id,
            component_id=comp2.id,
            quantity=Decimal("1.000"),  # 1 * 3kg = 3kg
        )
        parent.components = [bom1, bom2]
        session.commit()

        # Refresh
        session.refresh(parent)

        # Total: 4kg + 3kg = 7kg
        assert parent.get_total_weight() == Decimal("7.000")
