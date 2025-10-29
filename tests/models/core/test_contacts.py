"""
Unit tests for Contact and Service models.

Tests validation, business logic, and relationships for contact models.
"""

import pytest

from models.core.contacts import Contact, Service


class TestContact:
    """Test suite for Contact model."""

    def test_create_contact(self, session):
        """Test creating a basic contact."""
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            email="jperez@example.com",
            phone="+56912345678",
            mobile="+56987654321",
            position="Gerente de Ventas",
            company_id=1,
            service_id=1,
        )

        session.add(contact)
        session.commit()

        assert contact.id is not None
        assert contact.first_name == "Juan"
        assert contact.last_name == "Pérez"
        assert contact.email == "jperez@example.com"
        assert contact.position == "Gerente de Ventas"

    def test_name_validation(self, session):
        """Test first name and last name validation."""
        # Valid names (trimmed)
        contact = Contact(
            first_name="  Carlos  ",
            last_name="  Rodriguez  ",
            company_id=1,
        )
        assert contact.first_name == "Carlos"
        assert contact.last_name == "Rodriguez"

        # Invalid: empty first name
        with pytest.raises(ValueError, match="cannot be empty"):
            contact = Contact(
                first_name="",
                last_name="Pérez",
                company_id=1,
            )
            session.add(contact)
            session.flush()

        # Invalid: empty last name
        with pytest.raises(ValueError, match="cannot be empty"):
            contact = Contact(
                first_name="Juan",
                last_name="",
                company_id=1,
            )
            session.add(contact)
            session.flush()

        # Invalid: whitespace only
        with pytest.raises(ValueError, match="cannot be empty"):
            contact = Contact(
                first_name="   ",
                last_name="Pérez",
                company_id=1,
            )
            session.add(contact)
            session.flush()

    def test_email_validation(self, session):
        """Test email validation."""
        # Valid email
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            email="jperez@example.com",
            company_id=1,
        )
        assert contact.email == "jperez@example.com"

        # Email trimmed and lowercase
        contact.email = "  TEST@EXAMPLE.COM  "
        assert contact.email == "test@example.com"

        # None is valid
        contact.email = None
        assert contact.email is None

    def test_phone_validation(self, session):
        """Test phone and mobile validation."""
        # Valid phones
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            phone="+56912345678",
            mobile="+56987654321",
            company_id=1,
        )
        session.add(contact)
        session.flush()
        assert contact.phone == "+56912345678"
        assert contact.mobile == "+56987654321"

        # Change to another valid phone
        contact.phone = "+56923456789"
        session.flush()
        assert contact.phone == "+56923456789"

        # None is valid
        contact.phone = None
        contact.mobile = None
        session.flush()
        assert contact.phone is None
        assert contact.mobile is None

    def test_full_name_property(self, session):
        """Test full_name property."""
        contact = Contact(
            first_name="María",
            last_name="González",
            company_id=1,
        )

        assert contact.full_name == "María González"

    def test_active_mixin(self, session):
        """Test ActiveMixin functionality."""
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            company_id=1,
        )
        session.add(contact)
        session.flush()

        # Default should be active
        assert contact.is_active is True

        # Can be deactivated
        contact.is_active = False
        session.flush()
        assert contact.is_active is False

    def test_repr(self, session):
        """Test string representation."""
        contact = Contact(
            id=1,
            first_name="Juan",
            last_name="Pérez",
            company_id=5,
        )

        repr_str = repr(contact)
        assert "Contact" in repr_str
        assert "Juan Pérez" in repr_str
        assert "company_id=5" in repr_str


class TestService:
    """Test suite for Service model."""

    def test_create_service(self, session):
        """Test creating a service."""
        service = Service(
            name="Ventas",
            description="Departamento de ventas",
        )

        session.add(service)
        session.commit()

        assert service.id is not None
        assert service.name == "Ventas"
        assert service.description == "Departamento de ventas"

    def test_name_validation(self, session):
        """Test service name validation."""
        # Valid name (trimmed)
        service = Service(
            name="  Soporte Técnico  ",
            description="Ayuda técnica",
        )
        assert service.name == "Soporte Técnico"

        # Invalid: empty
        with pytest.raises(ValueError, match="cannot be empty"):
            service = Service(
                name="",
                description="Test",
            )
            session.add(service)
            session.flush()

        # Invalid: whitespace only
        with pytest.raises(ValueError, match="cannot be empty"):
            service = Service(
                name="   ",
                description="Test",
            )
            session.add(service)
            session.flush()

    def test_active_mixin(self, session):
        """Test ActiveMixin functionality."""
        service = Service(
            name="Compras",
            description="Departamento de compras",
        )
        session.add(service)
        session.flush()

        # Default should be active
        assert service.is_active is True

        # Can be deactivated
        service.is_active = False
        session.flush()
        assert service.is_active is False

    def test_repr(self, session):
        """Test string representation."""
        service = Service(
            id=1,
            name="Ventas",
        )

        repr_str = repr(service)
        assert "Service" in repr_str
        assert "Ventas" in repr_str


class TestContactServiceRelationship:
    """Integration tests for Contact-Service relationship."""

    def test_contact_with_service(self, session):
        """Test creating contact with service."""
        # Create service first
        service = Service(
            name="Ventas",
            description="Departamento de ventas",
        )
        session.add(service)
        session.flush()

        # Create contact with service
        contact = Contact(
            first_name="Juan",
            last_name="Pérez",
            email="jperez@example.com",
            position="Vendedor",
            company_id=1,
            service_id=service.id,
        )
        session.add(contact)
        session.commit()

        # Verify relationship
        assert contact.service_id == service.id

    def test_service_with_multiple_contacts(self, session):
        """Test service with multiple contacts."""
        # Create service
        service = Service(
            name="Soporte",
            description="Soporte técnico",
        )
        session.add(service)
        session.flush()

        # Create multiple contacts
        contact1 = Contact(
            first_name="Ana",
            last_name="García",
            company_id=1,
            service_id=service.id,
        )
        contact2 = Contact(
            first_name="Pedro",
            last_name="López",
            company_id=1,
            service_id=service.id,
        )

        service.contacts = [contact1, contact2]
        session.commit()

        # Verify relationships
        assert len(service.contacts) == 2
        assert all(c.service_id == service.id for c in service.contacts)

    def test_contact_without_service(self, session):
        """Test creating contact without service."""
        contact = Contact(
            first_name="María",
            last_name="Rodríguez",
            company_id=1,
            service_id=None,
        )

        session.add(contact)
        session.commit()

        assert contact.service_id is None

    def test_multiple_contacts_same_company(self, session):
        """Test multiple contacts for same company."""
        # Create contacts for same company
        contact1 = Contact(
            first_name="Juan",
            last_name="Pérez",
            email="jperez@company.com",
            position="Gerente",
            company_id=1,
        )
        contact2 = Contact(
            first_name="Ana",
            last_name="García",
            email="agarcia@company.com",
            position="Asistente",
            company_id=1,
        )

        session.add_all([contact1, contact2])
        session.commit()

        # Both contacts should belong to same company
        assert contact1.company_id == contact2.company_id == 1

    def test_contact_email_uniqueness(self, session):
        """Test that contacts can have unique or shared emails."""
        # Different contacts with different emails
        contact1 = Contact(
            first_name="Juan",
            last_name="Pérez",
            email="jperez@example.com",
            company_id=1,
        )
        contact2 = Contact(
            first_name="Ana",
            last_name="García",
            email="agarcia@example.com",
            company_id=2,
        )

        session.add_all([contact1, contact2])
        session.commit()

        assert contact1.email != contact2.email
        assert contact1.id != contact2.id

    def test_deactivate_contact(self, session):
        """Test deactivating a contact."""
        contact = Contact(
            first_name="Carlos",
            last_name="Martínez",
            email="cmartinez@example.com",
            company_id=1,
            is_active=True,
        )

        session.add(contact)
        session.commit()

        # Verify initially active
        assert contact.is_active is True

        # Deactivate
        contact.is_active = False
        session.commit()

        # Verify deactivated
        assert contact.is_active is False

    def test_contact_with_position_info(self, session):
        """Test contact with professional information."""
        contact = Contact(
            first_name="Laura",
            last_name="Fernández",
            email="lfernandez@example.com",
            phone="+56912345678",
            mobile="+56987654321",
            position="Directora de Operaciones",
            company_id=1,
        )

        session.add(contact)
        session.commit()

        assert contact.position == "Directora de Operaciones"
        assert contact.phone == "+56912345678"
        assert contact.mobile == "+56987654321"
        assert contact.full_name == "Laura Fernández"
