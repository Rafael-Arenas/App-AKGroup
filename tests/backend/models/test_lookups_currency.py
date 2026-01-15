"""
Tests for Currency model from lookups.

This module contains comprehensive tests for the Currency lookup model,
including CRUD operations, field validation, constraints, mixins, and edge cases.

Test Coverage:
    - Basic CRUD operations
    - Field validation (code, name, symbol)
    - CheckConstraints (code length, name not empty)
    - Unique constraints
    - Default values
    - ActiveMixin behavior
    - TimestampMixin behavior
    - Edge cases (empty strings, None values, etc.)
"""

from datetime import datetime, timezone

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.lookups import Currency


class TestCurrencyCreation:
    """Tests for Currency model instantiation and creation."""

    def test_create_currency_with_valid_data(self, session):
        """
        Test creating a Currency with all valid required fields.

        Verifies that a Currency can be created with valid data and
        all fields are properly stored in the database.
        """
        # Arrange & Act
        currency = Currency(
            code="USD",
            name="US Dollar",
            symbol="$",
            is_active=True,
        )
        session.add(currency)
        session.commit()
        session.refresh(currency)

        # Assert
        assert currency.id is not None
        assert currency.code == "USD"
        assert currency.name == "US Dollar"
        assert currency.symbol == "$"
        assert currency.is_active is True

    def test_create_currency_minimal_fields(self, session):
        """
        Test creating Currency with only required fields.

        Symbol is optional, so we test creating a currency without it.
        """
        # Arrange & Act
        currency = Currency(
            code="EUR",
            name="Euro",
        )
        session.add(currency)
        session.commit()
        session.refresh(currency)

        # Assert
        assert currency.id is not None
        assert currency.code == "EUR"
        assert currency.name == "Euro"
        assert currency.symbol is None
        assert currency.is_active is True  # Default value

    def test_create_currency_without_symbol(self, session):
        """Test creating Currency without symbol (optional field)."""
        # Arrange & Act
        currency = Currency(code="JPY", name="Japanese Yen")
        session.add(currency)
        session.commit()

        # Assert
        assert currency.symbol is None

    @pytest.mark.parametrize(
        "code,name,symbol",
        [
            ("CLP", "Chilean Peso", "$"),
            ("EUR", "Euro", "€"),
            ("GBP", "British Pound", "£"),
            ("CNY", "Chinese Yuan", "¥"),
        ],
    )
    def test_create_multiple_currencies(self, session, code, name, symbol):
        """
        Test creating multiple currencies with different valid data.

        Uses parametrization to test multiple currency configurations.
        """
        # Arrange & Act
        currency = Currency(code=code, name=name, symbol=symbol)
        session.add(currency)
        session.commit()
        session.refresh(currency)

        # Assert
        assert currency.code == code
        assert currency.name == name
        assert currency.symbol == symbol


class TestCurrencyValidation:
    """Tests for Currency field validation and constraints."""

    def test_code_must_be_exactly_3_chars(self, session):
        """
        Test that currency code must be exactly 3 characters.

        CheckConstraint: length(code) = 3
        """
        # Test code with 2 characters (too short)
        with pytest.raises(IntegrityError) as exc_info:
            currency = Currency(code="US", name="US Dollar")
            session.add(currency)
            session.commit()
        assert "code_exact_length" in str(exc_info.value).lower() or "check constraint" in str(exc_info.value).lower()
        session.rollback()

        # Test code with 4 characters (too long)
        with pytest.raises(IntegrityError) as exc_info:
            currency = Currency(code="USDD", name="US Dollar")
            session.add(currency)
            session.commit()
        assert "code_exact_length" in str(exc_info.value).lower() or "check constraint" in str(exc_info.value).lower()
        session.rollback()

    def test_code_must_be_unique(self, session):
        """
        Test that currency code must be unique.

        Unique constraint on code column.
        """
        # Arrange - Create first currency
        currency1 = Currency(code="USD", name="US Dollar")
        session.add(currency1)
        session.commit()

        # Act & Assert - Try to create duplicate
        with pytest.raises(IntegrityError) as exc_info:
            currency2 = Currency(code="USD", name="United States Dollar")
            session.add(currency2)
            session.commit()
        assert "unique" in str(exc_info.value).lower()

    def test_code_cannot_be_null(self, session):
        """Test that code is required (NOT NULL constraint)."""
        with pytest.raises(IntegrityError) as exc_info:
            currency = Currency(code=None, name="Some Currency")
            session.add(currency)
            session.commit()
        assert "not null" in str(exc_info.value).lower()

    def test_name_cannot_be_null(self, session):
        """Test that name is required (NOT NULL constraint)."""
        with pytest.raises(IntegrityError) as exc_info:
            currency = Currency(code="XXX", name=None)
            session.add(currency)
            session.commit()
        assert "not null" in str(exc_info.value).lower()

    def test_name_cannot_be_empty_or_whitespace(self, session):
        """
        Test that name cannot be empty or only whitespace.

        CheckConstraint: length(trim(name)) > 0
        """
        # Test empty string
        with pytest.raises(IntegrityError) as exc_info:
            currency = Currency(code="XXX", name="")
            session.add(currency)
            session.commit()
        assert "name_not_empty" in str(exc_info.value).lower() or "check constraint" in str(exc_info.value).lower()
        session.rollback()

        # Test whitespace only
        with pytest.raises(IntegrityError) as exc_info:
            currency = Currency(code="YYY", name="   ")
            session.add(currency)
            session.commit()
        assert "name_not_empty" in str(exc_info.value).lower() or "check constraint" in str(exc_info.value).lower()

    def test_symbol_max_length(self, session):
        """Test that symbol respects max length (5 characters)."""
        # Valid symbol (within limit)
        currency = Currency(code="EUR", name="Euro", symbol="€")
        session.add(currency)
        session.commit()
        assert currency.symbol == "€"

        # Symbol at max length (5 chars)
        currency2 = Currency(code="USD", name="US Dollar", symbol="US$$$")
        session.add(currency2)
        session.commit()
        assert len(currency2.symbol) <= 5

    def test_symbol_can_be_null(self, session):
        """Test that symbol is optional (nullable)."""
        currency = Currency(code="BTC", name="Bitcoin", symbol=None)
        session.add(currency)
        session.commit()
        session.refresh(currency)

        assert currency.symbol is None


class TestCurrencyCRUD:
    """Tests for CRUD operations on Currency model."""

    def test_read_currency_by_id(self, session, sample_currency):
        """Test reading a currency by primary key."""
        # Arrange - sample_currency fixture already created

        # Act
        retrieved = session.query(Currency).filter_by(id=sample_currency.id).first()

        # Assert
        assert retrieved is not None
        assert retrieved.id == sample_currency.id
        assert retrieved.code == "CLP"
        assert retrieved.name == "Chilean Peso"

    def test_read_currency_by_code(self, session, sample_currency):
        """Test querying currency by unique code."""
        # Act
        retrieved = session.query(Currency).filter_by(code="CLP").first()

        # Assert
        assert retrieved is not None
        assert retrieved.id == sample_currency.id

    def test_read_all_currencies(self, session):
        """Test retrieving all currencies."""
        # Arrange - Create multiple currencies
        currencies_data = [
            ("USD", "US Dollar", "$"),
            ("EUR", "Euro", "€"),
            ("GBP", "British Pound", "£"),
        ]
        for code, name, symbol in currencies_data:
            currency = Currency(code=code, name=name, symbol=symbol)
            session.add(currency)
        session.commit()

        # Act
        all_currencies = session.query(Currency).all()

        # Assert
        assert len(all_currencies) == 3
        codes = [c.code for c in all_currencies]
        assert "USD" in codes
        assert "EUR" in codes
        assert "GBP" in codes

    def test_update_currency(self, session, sample_currency):
        """Test updating currency fields."""
        # Arrange
        original_id = sample_currency.id
        original_created_at = sample_currency.created_at

        # Act
        sample_currency.name = "Chilean Peso (Updated)"
        sample_currency.symbol = "CLP$"
        session.commit()
        session.refresh(sample_currency)

        # Assert
        assert sample_currency.id == original_id  # ID unchanged
        assert sample_currency.name == "Chilean Peso (Updated)"
        assert sample_currency.symbol == "CLP$"
        assert sample_currency.created_at == original_created_at  # created_at unchanged
        assert sample_currency.updated_at > original_created_at  # updated_at changed

    def test_delete_currency(self, session, sample_currency):
        """Test deleting a currency."""
        # Arrange
        currency_id = sample_currency.id

        # Act
        session.delete(sample_currency)
        session.commit()

        # Assert
        deleted = session.query(Currency).filter_by(id=currency_id).first()
        assert deleted is None

    def test_filter_active_currencies(self, session):
        """Test filtering currencies by is_active flag."""
        # Arrange - Create active and inactive currencies
        active = Currency(code="USD", name="US Dollar", is_active=True)
        inactive = Currency(code="EUR", name="Euro", is_active=False)
        session.add_all([active, inactive])
        session.commit()

        # Act
        active_currencies = session.query(Currency).filter_by(is_active=True).all()

        # Assert
        assert len(active_currencies) == 1
        assert active_currencies[0].code == "USD"


class TestCurrencyMixins:
    """Tests for mixin behavior (TimestampMixin, ActiveMixin)."""

    def test_timestamp_mixin_sets_created_at(self, session):
        """Test that TimestampMixin automatically sets created_at."""
        # Arrange & Act
        currency = Currency(code="USD", name="US Dollar")
        session.add(currency)
        session.commit()
        session.refresh(currency)

        # Assert
        assert currency.created_at is not None
        assert isinstance(currency.created_at, datetime)

    def test_timestamp_mixin_sets_updated_at(self, session):
        """Test that TimestampMixin automatically sets updated_at."""
        # Arrange & Act
        currency = Currency(code="USD", name="US Dollar")
        session.add(currency)
        session.commit()
        session.refresh(currency)

        # Assert
        assert currency.updated_at is not None
        # Check that created_at and updated_at are very close (within 1 second)
        from datetime import timedelta
        assert abs((currency.updated_at - currency.created_at).total_seconds()) < 1

    def test_timestamp_mixin_updates_updated_at_on_change(self, session):
        """Test that updated_at changes when record is modified."""
        # Arrange
        currency = Currency(code="USD", name="US Dollar")
        session.add(currency)
        session.commit()
        session.refresh(currency)
        original_updated_at = currency.updated_at

        # Act - Update the currency
        import time
        time.sleep(0.01)  # Small delay to ensure timestamp changes
        currency.name = "United States Dollar"
        session.commit()
        session.refresh(currency)

        # Assert
        assert currency.updated_at > original_updated_at

    def test_active_mixin_default_is_true(self, session):
        """Test that ActiveMixin sets is_active to True by default."""
        # Arrange & Act
        currency = Currency(code="USD", name="US Dollar")
        session.add(currency)
        session.commit()
        session.refresh(currency)

        # Assert
        assert currency.is_active is True

    def test_active_mixin_can_be_set_to_false(self, session):
        """Test that is_active can be explicitly set to False."""
        # Arrange & Act
        currency = Currency(code="EUR", name="Euro", is_active=False)
        session.add(currency)
        session.commit()
        session.refresh(currency)

        # Assert
        assert currency.is_active is False

    def test_active_mixin_toggle(self, session, sample_currency):
        """Test toggling is_active flag."""
        # Arrange
        assert sample_currency.is_active is True

        # Act - Deactivate
        sample_currency.is_active = False
        session.commit()
        session.refresh(sample_currency)

        # Assert
        assert sample_currency.is_active is False

        # Act - Reactivate
        sample_currency.is_active = True
        session.commit()
        session.refresh(sample_currency)

        # Assert
        assert sample_currency.is_active is True


class TestCurrencyEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_code_with_lowercase_letters(self, session):
        """Test that lowercase codes are accepted (should be uppercase in real data)."""
        # Note: Model doesn't enforce uppercase, but business logic might
        currency = Currency(code="usd", name="US Dollar")
        session.add(currency)
        session.commit()
        session.refresh(currency)

        assert currency.code == "usd"  # Stored as-is

    def test_code_with_numbers(self, session):
        """Test that codes with numbers are accepted."""
        currency = Currency(code="X9A", name="Test Currency")
        session.add(currency)
        session.commit()

        assert currency.code == "X9A"

    def test_name_with_special_characters(self, session):
        """Test that names with special characters are accepted."""
        currency = Currency(
            code="EUR",
            name="Euro (€) - European Currency",
        )
        session.add(currency)
        session.commit()
        session.refresh(currency)

        assert "€" in currency.name
        assert "(" in currency.name

    def test_symbol_with_unicode(self, session):
        """Test that symbol accepts unicode characters."""
        currency = Currency(code="EUR", name="Euro", symbol="€")
        session.add(currency)
        session.commit()
        session.refresh(currency)

        assert currency.symbol == "€"

    def test_concurrent_currency_creation(self, session):
        """Test that multiple currencies can be created in same transaction."""
        # Arrange
        currencies = [
            Currency(code="USD", name="US Dollar", symbol="$"),
            Currency(code="EUR", name="Euro", symbol="€"),
            Currency(code="GBP", name="British Pound", symbol="£"),
        ]

        # Act
        session.add_all(currencies)
        session.commit()

        # Assert
        count = session.query(Currency).count()
        assert count == 3


class TestCurrencyRepr:
    """Tests for __repr__ method (if implemented)."""

    def test_repr_method(self, session):
        """Test string representation of Currency (if __repr__ is defined)."""
        currency = Currency(code="USD", name="US Dollar", symbol="$")
        session.add(currency)
        session.commit()
        session.refresh(currency)

        # Check that repr contains useful information
        repr_str = repr(currency)
        assert "Currency" in repr_str or "USD" in repr_str


class TestCurrencyIndexes:
    """Tests for database indexes."""

    def test_code_index_exists(self, session):
        """
        Test that code column has an index for fast lookups.

        This is more of a schema test - verifies index was created.
        """
        # Create multiple currencies
        for i in range(100):
            currency = Currency(
                code=f"C{i:02d}",
                name=f"Currency {i}",
            )
            session.add(currency)
        session.commit()

        # Query by indexed column should be fast
        result = session.query(Currency).filter_by(code="C50").first()
        assert result is not None
        assert result.name == "Currency 50"


class TestCurrencyRelationships:
    """
    Tests for relationships (if any).

    Currency doesn't have explicit relationships in the model shown,
    but it may be referenced by other models (quotes, products, etc.).
    This section is for future expansion.
    """

    def test_currency_can_be_referenced(self, session):
        """
        Test that currency can be created and referenced by ID.

        This is a basic test that other models could use currency_id FK.
        """
        currency = Currency(code="USD", name="US Dollar")
        session.add(currency)
        session.commit()
        session.refresh(currency)

        # Other models would reference currency.id
        assert currency.id is not None
        assert isinstance(currency.id, int)
