"""
Tests for Contact and Service models from core.contacts.

This module contains comprehensive tests for the Contact and Service models,
including CRUD operations, validators, relationships, cascade delete, and edge cases.

Test Coverage:
    Contact:
        - Basic CRUD operations with all fields
        - First name and last name validators (non-empty, strip whitespace)
        - Email validator (optional, format validation, lowercase normalization)
        - Phone and mobile validators (optional, E.164 format)
        - full_name property
        - Relationship with Company (cascade delete)
        - Relationship with Service (SET NULL on delete)
        - ActiveMixin behavior
        - __repr__ method
        - TimestampMixin and AuditMixin behavior

    Service:
        - Basic CRUD operations
        - Name validator (non-empty, strip whitespace, unique)
        - Description field
        - Relationship with Contact (one-to-many)
        - ActiveMixin behavior
        - __repr__ method
        - TimestampMixin behavior
"""

from typing import Optional

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.backend.models.core.companies import Company
from src.backend.models.core.contacts import Contact, Service
from src.backend.models.lookups.lookups import City, CompanyType, Country


# ============= SERVICE MODEL TESTS =============


class TestServiceCreation:
    """Tests for Service model instantiation and creation."""

    def test_create_service_with_all_fields(self, session: Session):
        """
        Test creating a Service with all valid fields.

        Verifies that a Service can be created with complete data and
        all fields are properly stored.
        """
        # Arrange & Act
        service = Service(
            name="Sales",
            description="Sales department",
        )
        session.add(service)
        session.commit()
        session.refresh(service)

        # Assert
        assert service.id is not None
        assert service.name == "Sales"
        assert service.description == "Sales department"
        assert service.is_active is True  # Default from ActiveMixin

    def test_create_service_minimal_fields(self, session: Session):
        """Test creating Service with only required fields."""
        # Arrange & Act
        service = Service(name="Purchasing")
        session.add(service)
        session.commit()
        session.refresh(service)

        # Assert
        assert service.id is not None
        assert service.name == "Purchasing"
        assert service.description is None

    def test_create_service_with_empty_description(self, session: Session):
        """Test creating Service with None description."""
        # Arrange & Act
        service = Service(
            name="Support",
            description=None,
        )
        session.add(service)
        session.commit()
        session.refresh(service)

        # Assert
        assert service.description is None


class TestServiceNameValidator:
    """Tests for Service name validation."""

    def test_name_strips_whitespace(self, session: Session):
        """Test that name strips whitespace."""
        # Arrange & Act
        service = Service(name="  Sales Department  ")
        session.add(service)
        session.commit()
        session.refresh(service)

        # Assert
        assert service.name == "Sales Department"

    def test_name_empty_raises_error(self, session: Session):
        """Test that empty name raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Service name cannot be empty"):
            service = Service(name="")

    def test_name_whitespace_only_raises_error(self, session: Session):
        """Test that whitespace-only name raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Service name cannot be empty"):
            service = Service(name="   ")

    def test_name_must_be_unique(self, session: Session):
        """Test that service name must be unique."""
        # Arrange
        service1 = Service(name="Sales")
        service2 = Service(name="Sales")
        session.add(service1)
        session.commit()

        # Act & Assert
        with pytest.raises(IntegrityError):
            session.add(service2)
            session.commit()


class TestServiceRepr:
    """Tests for Service __repr__ method."""

    def test_repr_format(self, session: Session):
        """Test __repr__ format."""
        # Arrange & Act
        service = Service(name="Sales")
        session.add(service)
        session.commit()
        session.refresh(service)

        # Assert
        repr_str = repr(service)
        assert "Service" in repr_str
        assert f"id={service.id}" in repr_str
        assert "name=Sales" in repr_str


class TestServiceActiveMixin:
    """Tests for Service ActiveMixin behavior."""

    def test_is_active_default_true(self, session: Session):
        """Test that is_active defaults to True."""
        # Arrange & Act
        service = Service(name="Sales")
        session.add(service)
        session.commit()
        session.refresh(service)

        # Assert
        assert service.is_active is True

    def test_create_inactive_service(self, session: Session):
        """Test creating inactive service."""
        # Arrange & Act
        service = Service(
            name="Inactive Service",
            is_active=False,
        )
        session.add(service)
        session.commit()
        session.refresh(service)

        # Assert
        assert service.is_active is False

    def test_query_active_services(self, session: Session):
        """Test querying only active services."""
        # Arrange
        active_service = Service(name="Active Service", is_active=True)
        inactive_service = Service(name="Inactive Service", is_active=False)
        session.add_all([active_service, inactive_service])
        session.commit()

        # Act
        active_results = session.query(Service).filter_by(is_active=True).all()

        # Assert
        assert len(active_results) == 1
        assert active_results[0].name == "Active Service"


class TestServiceTimestampMixin:
    """Tests for Service TimestampMixin behavior."""

    def test_created_at_set_on_creation(self, session: Session):
        """Test that created_at is set automatically on creation."""
        # Arrange & Act
        service = Service(name="Sales")
        session.add(service)
        session.commit()
        session.refresh(service)

        # Assert
        assert service.created_at is not None

    def test_updated_at_set_on_creation(self, session: Session):
        """Test that updated_at is set automatically on creation."""
        # Arrange & Act
        service = Service(name="Sales")
        session.add(service)
        session.commit()
        session.refresh(service)

        # Assert
        assert service.updated_at is not None


class TestServiceCRUDOperations:
    """Tests for Service CRUD operations."""

    def test_read_service_by_id(self, session: Session):
        """Test reading Service by ID."""
        # Arrange
        service = Service(name="Sales")
        session.add(service)
        session.commit()
        service_id = service.id

        # Act
        retrieved_service = session.query(Service).filter_by(id=service_id).first()

        # Assert
        assert retrieved_service is not None
        assert retrieved_service.id == service_id
        assert retrieved_service.name == "Sales"

    def test_update_service(self, session: Session):
        """Test updating Service fields."""
        # Arrange
        service = Service(name="Sales")
        session.add(service)
        session.commit()

        # Act
        service.description = "Updated description"
        service.is_active = False
        session.commit()
        session.refresh(service)

        # Assert
        assert service.description == "Updated description"
        assert service.is_active is False

    def test_delete_service(self, session: Session):
        """Test deleting Service."""
        # Arrange
        service = Service(name="Sales")
        session.add(service)
        session.commit()
        service_id = service.id

        # Act
        session.delete(service)
        session.commit()

        # Assert
        deleted_service = session.query(Service).filter_by(id=service_id).first()
        assert deleted_service is None


# ============= CONTACT MODEL TESTS =============


@pytest.fixture
def sample_service(session: Session) -> Service:
    """Create a sample Service for testing."""
    service = Service(
        name="Sales",
        description="Sales department",
    )
    session.add(service)
    session.commit()
    session.refresh(service)
    return service


class TestContactCreation:
    """Tests for Contact model instantiation and creation."""

    def test_create_contact_with_all_fields(
        self,
        session: Session,
        sample_company: Company,
        sample_service: Service,
    ):
        """
        Test creating a Contact with all valid fields.

        Verifies that a Contact can be created with complete data and
        all fields are properly stored.
        """
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            email="jperez@example.com",
            phone="+56912345678",
            mobile="+56987654321",
            position="Sales Manager",
            company_id=sample_company.id,
            service_id=sample_service.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.id is not None
        assert contact.first_name == "Juan"
        assert contact.last_name == "Pérez"
        assert contact.email == "jperez@example.com"
        assert contact.phone == "+56912345678"
        assert contact.mobile == "+56987654321"
        assert contact.position == "Sales Manager"
        assert contact.company_id == sample_company.id
        assert contact.service_id == sample_service.id
        assert contact.is_active is True  # Default

    def test_create_contact_minimal_fields(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test creating Contact with only required fields."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.id is not None
        assert contact.first_name == "Juan"
        assert contact.last_name == "Pérez"
        assert contact.email is None
        assert contact.phone is None
        assert contact.mobile is None
        assert contact.position is None
        assert contact.service_id is None

    def test_create_contact_without_service(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test creating Contact without service (service_id is optional)."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            email="jperez@example.com",
            company_id=sample_company.id,
            service_id=None,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.service_id is None
        assert contact.service is None


class TestContactNameValidators:
    """Tests for Contact first_name and last_name validation."""

    def test_first_name_strips_whitespace(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that first_name strips whitespace."""
        # Arrange & Act
        contact = Contact(
            first_name="  Juan  ",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.first_name == "Juan"

    def test_last_name_strips_whitespace(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that last_name strips whitespace."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="  Pérez  ",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.last_name == "Pérez"

    def test_first_name_empty_raises_error(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that empty first_name raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="first_name cannot be empty"):
            contact = Contact(
                first_name="",
                last_name="Pérez",
                company_id=sample_company.id,
            )

    def test_last_name_empty_raises_error(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that empty last_name raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="last_name cannot be empty"):
            contact = Contact(
                first_name="Juan",
                last_name="",
                company_id=sample_company.id,
            )

    def test_first_name_whitespace_only_raises_error(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that first_name with only whitespace raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="first_name cannot be empty"):
            contact = Contact(
                first_name="   ",
                last_name="Pérez",
                company_id=sample_company.id,
            )


class TestContactEmailValidator:
    """Tests for Contact email validation."""

    def test_email_normalized_to_lowercase(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that email is normalized to lowercase."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            email="JUAN.PEREZ@EXAMPLE.COM",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.email == "juan.perez@example.com"

    def test_email_none_is_valid(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that None is a valid value for email."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            email=None,
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.email is None

    def test_email_strips_whitespace(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that whitespace is stripped from email."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            email="  jperez@example.com  ",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.email == "jperez@example.com"

    def test_email_invalid_format_raises_error(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that invalid email format raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email format"):
            contact = Contact(
                first_name="Juan",
                last_name="Pérez",
                email="invalid-email",
                company_id=sample_company.id,
            )


class TestContactPhoneValidators:
    """Tests for Contact phone and mobile validation."""

    def test_phone_valid_e164_format(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that valid E.164 format phone is accepted."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            phone="+56912345678",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.phone == "+56912345678"

    def test_mobile_valid_e164_format(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that valid E.164 format mobile is accepted."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            mobile="+56987654321",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.mobile == "+56987654321"

    def test_phone_with_spaces_valid(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that phone with spaces is accepted."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            phone="+56 9 1234 5678",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.phone == "+56 9 1234 5678"

    def test_phone_none_is_valid(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that None is a valid value for phone."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            phone=None,
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.phone is None

    def test_mobile_none_is_valid(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that None is a valid value for mobile."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            mobile=None,
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.mobile is None

    def test_phone_too_short_raises_error(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that phone shorter than 8 digits raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Phone must be 8-15 digits"):
            contact = Contact(
                first_name="Juan",
                last_name="Pérez",
                phone="+123456",
                company_id=sample_company.id,
            )

    def test_mobile_invalid_format_raises_error(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that invalid mobile format raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Phone must be 8-15 digits"):
            contact = Contact(
                first_name="Juan",
                last_name="Pérez",
                mobile="ABC123",
                company_id=sample_company.id,
            )


class TestContactProperties:
    """Tests for Contact model properties."""

    def test_full_name_property(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that full_name property returns first_name + last_name."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.full_name == "Juan Pérez"

    def test_full_name_with_multiple_names(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test full_name with multiple first/last names."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan Carlos",
            last_name="Pérez González",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.full_name == "Juan Carlos Pérez González"


class TestContactRepr:
    """Tests for Contact __repr__ method."""

    def test_repr_format(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test __repr__ format."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        repr_str = repr(contact)
        assert "Contact" in repr_str
        assert f"id={contact.id}" in repr_str
        assert "name=Juan Pérez" in repr_str
        assert f"company_id={sample_company.id}" in repr_str


class TestContactRelationships:
    """Tests for Contact relationships."""

    def test_relationship_with_company(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that Contact has relationship with Company."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.company is not None
        assert contact.company.id == sample_company.id
        assert contact.company.name == sample_company.name

    def test_relationship_with_service(
        self,
        session: Session,
        sample_company: Company,
        sample_service: Service,
    ):
        """Test that Contact has relationship with Service."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
            service_id=sample_service.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.service is not None
        assert contact.service.id == sample_service.id
        assert contact.service.name == sample_service.name

    def test_company_has_contacts_backref(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that Company has contacts backref."""
        # Arrange & Act
        contact1 = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        contact2 = Contact(
            first_name="María",
            last_name="González",
            company_id=sample_company.id,
        )
        session.add_all([contact1, contact2])
        session.commit()
        session.refresh(sample_company)

        # Assert
        assert len(sample_company.contacts) == 2
        assert contact1 in sample_company.contacts
        assert contact2 in sample_company.contacts

    def test_service_has_contacts_backref(
        self,
        session: Session,
        sample_company: Company,
        sample_service: Service,
    ):
        """Test that Service has contacts backref."""
        # Arrange & Act
        contact1 = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
            service_id=sample_service.id,
        )
        contact2 = Contact(
            first_name="María",
            last_name="González",
            company_id=sample_company.id,
            service_id=sample_service.id,
        )
        session.add_all([contact1, contact2])
        session.commit()
        session.refresh(sample_service)

        # Assert
        assert len(sample_service.contacts) == 2
        assert contact1 in sample_service.contacts
        assert contact2 in sample_service.contacts


class TestContactCascadeDelete:
    """Tests for Contact cascade delete behavior."""

    def test_delete_company_cascades_to_contacts(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that deleting Company cascades to its Contacts."""
        # Arrange
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        contact_id = contact.id

        # Act
        session.delete(sample_company)
        session.commit()

        # Assert
        deleted_contact = session.query(Contact).filter_by(id=contact_id).first()
        assert deleted_contact is None

    def test_delete_service_sets_null_in_contacts(
        self,
        session: Session,
        sample_company: Company,
        sample_service: Service,
    ):
        """Test that deleting Service sets service_id to NULL in Contacts."""
        # Arrange
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
            service_id=sample_service.id,
        )
        session.add(contact)
        session.commit()
        contact_id = contact.id

        # Act
        session.delete(sample_service)
        session.commit()

        # Assert
        updated_contact = session.query(Contact).filter_by(id=contact_id).first()
        assert updated_contact is not None
        assert updated_contact.service_id is None
        assert updated_contact.service is None


class TestContactActiveMixin:
    """Tests for Contact ActiveMixin behavior."""

    def test_is_active_default_true(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that is_active defaults to True."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.is_active is True

    def test_create_inactive_contact(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test creating inactive contact."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
            is_active=False,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.is_active is False

    def test_query_active_contacts(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test querying only active contacts."""
        # Arrange
        active_contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
            is_active=True,
        )
        inactive_contact = Contact(
            first_name="María",
            last_name="González",
            company_id=sample_company.id,
            is_active=False,
        )
        session.add_all([active_contact, inactive_contact])
        session.commit()

        # Act
        active_results = session.query(Contact).filter_by(is_active=True).all()

        # Assert
        assert len(active_results) == 1
        assert active_results[0].first_name == "Juan"


class TestContactTimestampMixin:
    """Tests for Contact TimestampMixin behavior."""

    def test_created_at_set_on_creation(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that created_at is set automatically on creation."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.created_at is not None

    def test_updated_at_set_on_creation(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that updated_at is set automatically on creation."""
        # Arrange & Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.updated_at is not None


class TestContactAuditMixin:
    """Tests for Contact AuditMixin behavior."""

    def test_created_by_id_set_from_session_context(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that created_by_id is set from session context."""
        # Arrange
        session.info["user_id"] = 42

        # Act
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.created_by_id == 42

    def test_updated_by_id_set_from_session_context(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test that updated_by_id is set from session context."""
        # Arrange
        session.info["user_id"] = 42
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        session.refresh(contact)

        # Act - Update with different user
        session.info["user_id"] = 99
        contact.position = "Updated Position"
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.created_by_id == 42
        assert contact.updated_by_id == 99


class TestContactCRUDOperations:
    """Tests for Contact CRUD operations."""

    def test_read_contact_by_id(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test reading Contact by ID."""
        # Arrange
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        contact_id = contact.id

        # Act
        retrieved_contact = session.query(Contact).filter_by(id=contact_id).first()

        # Assert
        assert retrieved_contact is not None
        assert retrieved_contact.id == contact_id
        assert retrieved_contact.first_name == "Juan"

    def test_update_contact(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test updating Contact fields."""
        # Arrange
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()

        # Act
        contact.email = "newemail@example.com"
        contact.position = "Senior Manager"
        session.commit()
        session.refresh(contact)

        # Assert
        assert contact.email == "newemail@example.com"
        assert contact.position == "Senior Manager"

    def test_delete_contact(
        self,
        session: Session,
        sample_company: Company,
    ):
        """Test deleting Contact."""
        # Arrange
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        session.add(contact)
        session.commit()
        contact_id = contact.id

        # Act
        session.delete(contact)
        session.commit()

        # Assert
        deleted_contact = session.query(Contact).filter_by(id=contact_id).first()
        assert deleted_contact is None

    def test_query_contacts_by_company(
        self,
        session: Session,
        sample_company: Company,
        sample_company_type: CompanyType,
        sample_country: Country,
        sample_city: City,
    ):
        """Test querying Contacts by company."""
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

        contact1 = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
        )
        contact2 = Contact(
            first_name="María",
            last_name="González",
            company_id=sample_company.id,
        )
        contact3 = Contact(
            first_name="Pedro",
            last_name="Martínez",
            company_id=company2.id,
        )
        session.add_all([contact1, contact2, contact3])
        session.commit()

        # Act
        company_contacts = session.query(Contact).filter_by(company_id=sample_company.id).all()

        # Assert
        assert len(company_contacts) == 2
        assert contact1 in company_contacts
        assert contact2 in company_contacts
        assert contact3 not in company_contacts

    def test_query_contacts_by_service(
        self,
        session: Session,
        sample_company: Company,
        sample_service: Service,
    ):
        """Test querying Contacts by service."""
        # Arrange
        service2 = Service(name="Purchasing")
        session.add(service2)
        session.commit()

        contact1 = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=sample_company.id,
            service_id=sample_service.id,
        )
        contact2 = Contact(
            first_name="María",
            last_name="González",
            company_id=sample_company.id,
            service_id=sample_service.id,
        )
        contact3 = Contact(
            first_name="Pedro",
            last_name="Martínez",
            company_id=sample_company.id,
            service_id=service2.id,
        )
        session.add_all([contact1, contact2, contact3])
        session.commit()

        # Act
        service_contacts = session.query(Contact).filter_by(service_id=sample_service.id).all()

        # Assert
        assert len(service_contacts) == 2
        assert contact1 in service_contacts
        assert contact2 in service_contacts
        assert contact3 not in service_contacts
