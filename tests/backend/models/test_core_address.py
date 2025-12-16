"""
Tests for Address model from core.addresses.

This module contains comprehensive tests for the Address model,
including CRUD operations, validators, relationships, enums, and edge cases.

Test Coverage:
    Address:
        - Basic CRUD operations with all fields
        - AddressType enum (DELIVERY, BILLING, HEADQUARTERS, PLANT)
        - Address validator (min 5 chars, strip whitespace)
        - CheckConstraint for address length
        - is_default default value (False)
        - address_type default value (DELIVERY)
        - Relationship with Company (cascade delete)
        - Multiple addresses per company
        - Default address logic
        - TimestampMixin and AuditMixin behavior
        - __repr__ method
"""

from typing import Optional

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.backend.models.core.addresses import Address, AddressType
from src.backend.models.core.companies import Company
from src.backend.models.lookups.lookups import City, CompanyType, Country


# ============= ADDRESS TYPE ENUM TESTS =============


class TestAddressTypeEnum:
    """Tests for AddressType enum."""

    def test_address_type_enum_values(self):
        """Test that AddressType enum has correct values."""
        # Assert
        assert AddressType.DELIVERY.value == "delivery"
        assert AddressType.BILLING.value == "billing"
        assert AddressType.HEADQUARTERS.value == "headquarters"
        assert AddressType.PLANT.value == "plant"

    def test_address_type_enum_members(self):
        """Test that AddressType enum has all expected members."""
        # Assert
        enum_members = [e.value for e in AddressType]
        assert "delivery" in enum_members
        assert "billing" in enum_members
        assert "headquarters" in enum_members
        assert "plant" in enum_members
        assert len(enum_members) == 4


# ============= ADDRESS MODEL TESTS =============


class TestAddressCreation:
    """Tests for Address model instantiation and creation."""

    def test_create_address_with_all_fields(
        self,
        session: Session,
        sample_company: Company,
    ):
        """
        Test creating an Address with all valid fields.

        Verifies that an Address can be created with complete data and
        all fields are properly stored.
        """
        # Arrange & Act
        address = Address(
            address="Av. Providencia 1234, Oficina 501",
            city="Santiago",
            postal_code="7500000",
            country="Chile",
            is_default=True,
            address_type=AddressType.DELIVERY,
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.id is not None
        assert address.address == "Av. Providencia 1234, Oficina 501"
        assert address.city == "Santiago"
        assert address.postal_code == "7500000"
        assert address.country == "Chile"
        assert address.is_default is True
        assert address.address_type == AddressType.DELIVERY
        assert address.company_id == sample_company.id

    def test_create_address_minimal_fields(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test creating Address with only required fields."""
        # Arrange & Act
        address = Address(
            address="Av. Providencia 1234",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.id is not None
        assert address.address == "Av. Providencia 1234"
        assert address.city is None
        assert address.postal_code is None
        assert address.country is None
        assert address.is_default is False  # Default
        assert address.address_type == AddressType.DELIVERY  # Default

    def test_create_address_default_values(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that default values are properly set."""
        # Arrange & Act
        address = Address(
            address="Av. Providencia 1234",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert - Check defaults
        assert address.is_default is False
        assert address.address_type == AddressType.DELIVERY
        assert address.created_at is not None
        assert address.updated_at is not None

    def test_create_address_each_type(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test creating Address with each AddressType."""
        # Arrange & Act
        delivery_address = Address(
            address="Delivery Address 123",
            address_type=AddressType.DELIVERY,
            company_id=sample_company.id,
        )
        billing_address = Address(
            address="Billing Address 456",
            address_type=AddressType.BILLING,
            company_id=sample_company.id,
        )
        headquarters_address = Address(
            address="Headquarters Address 789",
            address_type=AddressType.HEADQUARTERS,
            company_id=sample_company.id,
        )
        plant_address = Address(
            address="Plant Address 101",
            address_type=AddressType.PLANT,
            company_id=sample_company.id,
        )
        session.add_all([delivery_address, billing_address, headquarters_address, plant_address])
        session.commit()

        # Assert
        assert delivery_address.address_type == AddressType.DELIVERY
        assert billing_address.address_type == AddressType.BILLING
        assert headquarters_address.address_type == AddressType.HEADQUARTERS
        assert plant_address.address_type == AddressType.PLANT


class TestAddressValidator:
    """Tests for Address address field validation."""

    def test_address_strips_whitespace(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that address strips whitespace."""
        # Arrange & Act
        address = Address(
            address="  Av. Providencia 1234  ",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.address == "Av. Providencia 1234"

    def test_address_minimum_length_valid(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test address with minimum valid length (5 characters)."""
        # Arrange & Act
        address = Address(
            address="12345",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.address == "12345"

    def test_address_too_short_raises_error(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that address shorter than 5 characters raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Address must be at least 5 characters long"):
            address = Address(
                address="1234",
                company_id=sample_company.id,
            )

    def test_address_empty_raises_error(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that empty address raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Address must be at least 5 characters long"):
            address = Address(
                address="",
                company_id=sample_company.id,
            )

    def test_address_whitespace_only_raises_error(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that whitespace-only address raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Address must be at least 5 characters long"):
            address = Address(
                address="     ",
                company_id=sample_company.id,
            )

    def test_address_with_newlines_valid(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that address with newlines is valid (using Text field)."""
        # Arrange & Act
        address = Address(
            address="Av. Providencia 1234\nOficina 501\nSantiago",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert "\n" in address.address
        assert "Oficina 501" in address.address


class TestAddressIsDefault:
    """Tests for Address is_default field."""

    def test_is_default_false_by_default(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that is_default defaults to False."""
        # Arrange & Act
        address = Address(
            address="Av. Providencia 1234",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.is_default is False

    def test_create_default_address(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test creating Address with is_default=True."""
        # Arrange & Act
        address = Address(
            address="Av. Providencia 1234",
            is_default=True,
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.is_default is True

    def test_multiple_default_addresses_allowed(
        self,
        session: Session,
        sample_company: Company,
    ):
        """
        Test that multiple default addresses are allowed per company.

        Note: This test documents current behavior. In production, you might
        want to enforce only one default address per company through
        application logic or database constraints.
        """
        # Arrange & Act
        address1 = Address(
            address="Address 1 12345",
            is_default=True,
            company_id=sample_company.id,
        )
        address2 = Address(
            address="Address 2 67890",
            is_default=True,
            company_id=sample_company.id,
        )
        session.add_all([address1, address2])
        session.commit()

        # Assert - Both can have is_default=True
        assert address1.is_default is True
        assert address2.is_default is True

    def test_query_default_address(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test querying for default address."""
        # Arrange
        default_address = Address(
            address="Default Address 123",
            is_default=True,
            company_id=sample_company.id,
        )
        non_default_address = Address(
            address="Non-Default Address 456",
            is_default=False,
            company_id=sample_company.id,
        )
        session.add_all([default_address, non_default_address])
        session.commit()

        # Act
        default_result = (
            session.query(Address)
            .filter_by(company_id=sample_company.id, is_default=True)
            .first()
        )

        # Assert
        assert default_result is not None
        assert default_result.id == default_address.id


class TestAddressType:
    """Tests for Address address_type field."""

    def test_address_type_defaults_to_delivery(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that address_type defaults to DELIVERY."""
        # Arrange & Act
        address = Address(
            address="Av. Providencia 1234",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.address_type == AddressType.DELIVERY

    def test_create_billing_address(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test creating Address with BILLING type."""
        # Arrange & Act
        address = Address(
            address="Billing Address 1234",
            address_type=AddressType.BILLING,
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.address_type == AddressType.BILLING

    def test_create_headquarters_address(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test creating Address with HEADQUARTERS type."""
        # Arrange & Act
        address = Address(
            address="Headquarters Address 1234",
            address_type=AddressType.HEADQUARTERS,
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.address_type == AddressType.HEADQUARTERS

    def test_create_plant_address(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test creating Address with PLANT type."""
        # Arrange & Act
        address = Address(
            address="Plant Address 1234",
            address_type=AddressType.PLANT,
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.address_type == AddressType.PLANT

    def test_query_addresses_by_type(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test querying addresses by type."""
        # Arrange
        delivery_address = Address(
            address="Delivery Address 123",
            address_type=AddressType.DELIVERY,
            company_id=sample_company.id,
        )
        billing_address = Address(
            address="Billing Address 456",
            address_type=AddressType.BILLING,
            company_id=sample_company.id,
        )
        session.add_all([delivery_address, billing_address])
        session.commit()

        # Act
        delivery_results = (
            session.query(Address)
            .filter_by(address_type=AddressType.DELIVERY)
            .all()
        )

        # Assert
        assert len(delivery_results) == 1
        assert delivery_results[0].id == delivery_address.id


class TestAddressRepr:
    """Tests for Address __repr__ method."""

    def test_repr_format(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test __repr__ format."""
        # Arrange & Act
        address = Address(
            address="Av. Providencia 1234",
            address_type=AddressType.DELIVERY,
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        repr_str = repr(address)
        assert "Address" in repr_str
        assert f"id={address.id}" in repr_str
        assert f"company_id={sample_company.id}" in repr_str
        assert "type=delivery" in repr_str

    def test_repr_with_different_types(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test __repr__ shows correct address type."""
        # Arrange & Act
        billing_address = Address(
            address="Billing Address 123",
            address_type=AddressType.BILLING,
            company_id=sample_company.id,
        )
        session.add(billing_address)
        session.commit()
        session.refresh(billing_address)

        # Assert
        repr_str = repr(billing_address)
        assert "type=billing" in repr_str


class TestAddressRelationships:
    """Tests for Address relationships."""

    def test_relationship_with_company(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that Address has relationship with Company."""
        # Arrange & Act
        address = Address(
            address="Av. Providencia 1234",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.company is not None
        assert address.company.id == sample_company.id
        assert address.company.name == sample_company.name

    def test_company_has_addresses_backref(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that Company has addresses backref."""
        # Arrange & Act
        address1 = Address(
            address="Address 1 12345",
            company_id=sample_company.id,
        )
        address2 = Address(
            address="Address 2 67890",
            company_id=sample_company.id,
        )
        session.add_all([address1, address2])
        session.commit()
        session.refresh(sample_company)

        # Assert
        assert len(sample_company.addresses) == 2
        assert address1 in sample_company.addresses
        assert address2 in sample_company.addresses

    def test_multiple_addresses_per_company(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that a company can have multiple addresses."""
        # Arrange & Act
        delivery_address = Address(
            address="Delivery Address 123",
            address_type=AddressType.DELIVERY,
            company_id=sample_company.id,
        )
        billing_address = Address(
            address="Billing Address 456",
            address_type=AddressType.BILLING,
            company_id=sample_company.id,
        )
        headquarters_address = Address(
            address="Headquarters Address 789",
            address_type=AddressType.HEADQUARTERS,
            company_id=sample_company.id,
        )
        session.add_all([delivery_address, billing_address, headquarters_address])
        session.commit()

        # Act
        company_addresses = (
            session.query(Address)
            .filter_by(company_id=sample_company.id)
            .all()
        )

        # Assert
        assert len(company_addresses) == 3
        assert delivery_address in company_addresses
        assert billing_address in company_addresses
        assert headquarters_address in company_addresses


class TestAddressCascadeDelete:
    """Tests for Address cascade delete behavior."""

    def test_delete_company_cascades_to_addresses(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that deleting Company cascades to its Addresses."""
        # Arrange
        address1 = Address(
            address="Address 1 12345",
            company_id=sample_company.id,
        )
        address2 = Address(
            address="Address 2 67890",
            company_id=sample_company.id,
        )
        session.add_all([address1, address2])
        session.commit()
        address1_id = address1.id
        address2_id = address2.id

        # Act
        session.delete(sample_company)
        session.commit()

        # Assert
        deleted_address1 = session.query(Address).filter_by(id=address1_id).first()
        deleted_address2 = session.query(Address).filter_by(id=address2_id).first()
        assert deleted_address1 is None
        assert deleted_address2 is None


class TestAddressTimestampMixin:
    """Tests for Address TimestampMixin behavior."""

    def test_created_at_set_on_creation(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that created_at is set automatically on creation."""
        # Arrange & Act
        address = Address(
            address="Av. Providencia 1234",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.created_at is not None

    def test_updated_at_set_on_creation(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that updated_at is set automatically on creation."""
        # Arrange & Act
        address = Address(
            address="Av. Providencia 1234",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.updated_at is not None

    def test_updated_at_changes_on_update(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that updated_at is updated when record changes."""
        # Arrange
        address = Address(
            address="Av. Providencia 1234",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)
        original_updated_at = address.updated_at

        # Act - Update the address
        import time
        time.sleep(0.01)  # Small delay to ensure timestamp difference
        address.city = "Santiago"
        session.commit()
        session.refresh(address)

        # Assert
        assert address.updated_at > original_updated_at


class TestAddressAuditMixin:
    """Tests for Address AuditMixin behavior."""

    def test_created_by_id_set_from_session_context(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that created_by_id is set from session context."""
        # Arrange
        session.info["user_id"] = 42

        # Act
        address = Address(
            address="Av. Providencia 1234",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.created_by_id == 42

    def test_updated_by_id_set_from_session_context(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that updated_by_id is set from session context."""
        # Arrange
        session.info["user_id"] = 42
        address = Address(
            address="Av. Providencia 1234",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Act - Update with different user
        session.info["user_id"] = 99
        address.city = "Santiago"
        session.commit()
        session.refresh(address)

        # Assert
        assert address.created_by_id == 42
        assert address.updated_by_id == 99


class TestAddressCRUDOperations:
    """Tests for Address CRUD operations."""

    def test_read_address_by_id(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test reading Address by ID."""
        # Arrange
        address = Address(
            address="Av. Providencia 1234",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        address_id = address.id

        # Act
        retrieved_address = session.query(Address).filter_by(id=address_id).first()

        # Assert
        assert retrieved_address is not None
        assert retrieved_address.id == address_id
        assert retrieved_address.address == "Av. Providencia 1234"

    def test_update_address(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test updating Address fields."""
        # Arrange
        address = Address(
            address="Av. Providencia 1234",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        # Act
        address.city = "Santiago"
        address.postal_code = "7500000"
        address.country = "Chile"
        address.is_default = True
        session.commit()
        session.refresh(address)

        # Assert
        assert address.city == "Santiago"
        assert address.postal_code == "7500000"
        assert address.country == "Chile"
        assert address.is_default is True

    def test_update_address_type(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test updating address_type."""
        # Arrange
        address = Address(
            address="Av. Providencia 1234",
            address_type=AddressType.DELIVERY,
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        # Act
        address.address_type = AddressType.BILLING
        session.commit()
        session.refresh(address)

        # Assert
        assert address.address_type == AddressType.BILLING

    def test_delete_address(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test deleting Address."""
        # Arrange
        address = Address(
            address="Av. Providencia 1234",
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        address_id = address.id

        # Act
        session.delete(address)
        session.commit()

        # Assert
        deleted_address = session.query(Address).filter_by(id=address_id).first()
        assert deleted_address is None

    def test_query_addresses_by_company(
        self,
        session: Session,
        sample_company: Company,
        sample_company_type: CompanyType,
        sample_country: Country,
        sample_city: City,
    ):
        """Test querying Addresses by company."""
        # Arrange
        company2 = Company(
            name="Other Company",
            trigram="OTH",
            company_type_id=sample_company_type.id,
            country_id=sample_country.id,
            city_id=sample_city.id,
        )
        session.add(company2)
        session.commit()

        address1 = Address(
            address="Address 1 12345",
            company_id=sample_company.id,
        )
        address2 = Address(
            address="Address 2 67890",
            company_id=sample_company.id,
        )
        address3 = Address(
            address="Address 3 11111",
            company_id=company2.id,
        )
        session.add_all([address1, address2, address3])
        session.commit()

        # Act
        company_addresses = (
            session.query(Address)
            .filter_by(company_id=sample_company.id)
            .all()
        )

        # Assert
        assert len(company_addresses) == 2
        assert address1 in company_addresses
        assert address2 in company_addresses
        assert address3 not in company_addresses

    def test_query_addresses_by_company_and_type(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test querying Addresses by company and type."""
        # Arrange
        delivery_address = Address(
            address="Delivery Address 123",
            address_type=AddressType.DELIVERY,
            company_id=sample_company.id,
        )
        billing_address = Address(
            address="Billing Address 456",
            address_type=AddressType.BILLING,
            company_id=sample_company.id,
        )
        session.add_all([delivery_address, billing_address])
        session.commit()

        # Act
        delivery_results = (
            session.query(Address)
            .filter_by(company_id=sample_company.id, address_type=AddressType.DELIVERY)
            .all()
        )

        # Assert
        assert len(delivery_results) == 1
        assert delivery_results[0].id == delivery_address.id

    def test_query_default_address_for_company(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test querying default address for a specific company."""
        # Arrange
        default_address = Address(
            address="Default Address 123",
            is_default=True,
            company_id=sample_company.id,
        )
        non_default_address = Address(
            address="Non-Default Address 456",
            is_default=False,
            company_id=sample_company.id,
        )
        session.add_all([default_address, non_default_address])
        session.commit()

        # Act
        result = (
            session.query(Address)
            .filter_by(company_id=sample_company.id, is_default=True)
            .first()
        )

        # Assert
        assert result is not None
        assert result.id == default_address.id


class TestAddressOptionalFields:
    """Tests for Address optional fields."""

    def test_address_without_city(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test creating Address without city."""
        # Arrange & Act
        address = Address(
            address="Av. Providencia 1234",
            city=None,
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.city is None

    def test_address_without_postal_code(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test creating Address without postal_code."""
        # Arrange & Act
        address = Address(
            address="Av. Providencia 1234",
            postal_code=None,
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.postal_code is None

    def test_address_without_country(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test creating Address without country."""
        # Arrange & Act
        address = Address(
            address="Av. Providencia 1234",
            country=None,
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()
        session.refresh(address)

        # Assert
        assert address.country is None

    def test_update_optional_fields(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test updating optional fields from None to values."""
        # Arrange
        address = Address(
            address="Av. Providencia 1234",
            city=None,
            postal_code=None,
            country=None,
            company_id=sample_company.id,
        )
        session.add(address)
        session.commit()

        # Act
        address.city = "Santiago"
        address.postal_code = "7500000"
        address.country = "Chile"
        session.commit()
        session.refresh(address)

        # Assert
        assert address.city == "Santiago"
        assert address.postal_code == "7500000"
        assert address.country == "Chile"


class TestAddressBusinessScenarios:
    """Tests for common business scenarios with addresses."""

    def test_company_with_multiple_address_types(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test company with different types of addresses."""
        # Arrange & Act
        delivery = Address(
            address="Warehouse St 123, Santiago",
            address_type=AddressType.DELIVERY,
            company_id=sample_company.id,
        )
        billing = Address(
            address="Finance Dept, Building A",
            address_type=AddressType.BILLING,
            company_id=sample_company.id,
        )
        headquarters = Address(
            address="Main Office, Tower B, Floor 10",
            address_type=AddressType.HEADQUARTERS,
            is_default=True,
            company_id=sample_company.id,
        )
        session.add_all([delivery, billing, headquarters])
        session.commit()

        # Act - Query by type
        hq_address = (
            session.query(Address)
            .filter_by(
                company_id=sample_company.id,
                address_type=AddressType.HEADQUARTERS
            )
            .first()
        )

        # Assert
        assert hq_address is not None
        assert hq_address.is_default is True
        assert "Main Office" in hq_address.address

    def test_find_default_delivery_address(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test finding default delivery address for a company."""
        # Arrange
        delivery1 = Address(
            address="Delivery Address 1",
            address_type=AddressType.DELIVERY,
            is_default=False,
            company_id=sample_company.id,
        )
        delivery2 = Address(
            address="Delivery Address 2 - Default",
            address_type=AddressType.DELIVERY,
            is_default=True,
            company_id=sample_company.id,
        )
        session.add_all([delivery1, delivery2])
        session.commit()

        # Act
        default_delivery = (
            session.query(Address)
            .filter_by(
                company_id=sample_company.id,
                address_type=AddressType.DELIVERY,
                is_default=True
            )
            .first()
        )

        # Assert
        assert default_delivery is not None
        assert default_delivery.id == delivery2.id
        assert "Default" in default_delivery.address

    def test_company_with_multiple_plants(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test company with multiple plant addresses."""
        # Arrange & Act
        plant1 = Address(
            address="Plant 1 - North District",
            city="Santiago",
            address_type=AddressType.PLANT,
            company_id=sample_company.id,
        )
        plant2 = Address(
            address="Plant 2 - South District",
            city="Concepción",
            address_type=AddressType.PLANT,
            company_id=sample_company.id,
        )
        plant3 = Address(
            address="Plant 3 - Central District",
            city="Valparaíso",
            address_type=AddressType.PLANT,
            company_id=sample_company.id,
        )
        session.add_all([plant1, plant2, plant3])
        session.commit()

        # Act
        plants = (
            session.query(Address)
            .filter_by(
                company_id=sample_company.id,
                address_type=AddressType.PLANT
            )
            .all()
        )

        # Assert
        assert len(plants) == 3
        cities = [plant.city for plant in plants]
        assert "Santiago" in cities
        assert "Concepción" in cities
        assert "Valparaíso" in cities
