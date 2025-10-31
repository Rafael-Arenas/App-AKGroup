"""
Tests for Staff model from core.staff.

This module contains comprehensive tests for the Staff model,
including CRUD operations, validators, properties, unique constraints, and edge cases.

Test Coverage:
    Staff:
        - Basic CRUD operations with all fields
        - Username validator (min 3 chars, lowercase, alphanumeric+hyphens+underscores)
        - Email validator (format validation, lowercase normalization)
        - First name and last name validators (non-empty, strip whitespace)
        - Trigram validator (exactly 3 letters, uppercase, optional/nullable)
        - Phone validator (E.164 format, optional)
        - Position validator (strip whitespace, optional)
        - full_name property
        - __repr__ method
        - Unique constraints (username, email, trigram)
        - is_active and is_admin default values
        - TimestampMixin and AuditMixin behavior
"""

from typing import Optional

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.backend.models.core.staff import Staff


# ============= STAFF MODEL TESTS =============


class TestStaffCreation:
    """Tests for Staff model instantiation and creation."""

    def test_create_staff_with_all_fields(self, session: Session):
        """
        Test creating a Staff member with all valid fields.

        Verifies that a Staff member can be created with complete data and
        all fields are properly stored.
        """
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="john.doe@akgroup.com",
            first_name="John",
            last_name="Doe",
            trigram="JDO",
            phone="+56912345678",
            position="Sales Manager",
            is_active=True,
            is_admin=False,
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.id is not None
        assert staff.username == "jdoe"
        assert staff.email == "john.doe@akgroup.com"
        assert staff.first_name == "John"
        assert staff.last_name == "Doe"
        assert staff.trigram == "JDO"
        assert staff.phone == "+56912345678"
        assert staff.position == "Sales Manager"
        assert staff.is_active is True
        assert staff.is_admin is False

    def test_create_staff_minimal_fields(self, session: Session):
        """Test creating Staff with only required fields."""
        # Arrange & Act
        staff = Staff(
            username="jsmith",
            email="jsmith@example.com",
            first_name="Jane",
            last_name="Smith",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.id is not None
        assert staff.username == "jsmith"
        assert staff.email == "jsmith@example.com"
        assert staff.first_name == "Jane"
        assert staff.last_name == "Smith"
        assert staff.trigram is None
        assert staff.phone is None
        assert staff.position is None
        assert staff.is_active is True  # Default
        assert staff.is_admin is False  # Default

    def test_create_staff_default_values(self, session: Session):
        """Test that default values are properly set."""
        # Arrange & Act
        staff = Staff(
            username="testuser",
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert - Check defaults
        assert staff.is_active is True
        assert staff.is_admin is False
        assert staff.created_at is not None
        assert staff.updated_at is not None

    def test_create_admin_staff(self, session: Session):
        """Test creating Staff with admin privileges."""
        # Arrange & Act
        staff = Staff(
            username="admin",
            email="admin@akgroup.com",
            first_name="Admin",
            last_name="User",
            is_admin=True,
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.is_admin is True
        assert staff.is_active is True

    def test_create_inactive_staff(self, session: Session):
        """Test creating Staff with inactive status."""
        # Arrange & Act
        staff = Staff(
            username="inactive",
            email="inactive@example.com",
            first_name="Inactive",
            last_name="User",
            is_active=False,
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.is_active is False


class TestStaffUsernameValidator:
    """Tests for Staff username validation."""

    def test_username_normalized_to_lowercase(self, session: Session):
        """Test that username is normalized to lowercase."""
        # Arrange & Act
        staff = Staff(
            username="JOHNDOE",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.username == "johndoe"

    def test_username_with_hyphens_allowed(self, session: Session):
        """Test that hyphens are allowed in username."""
        # Arrange & Act
        staff = Staff(
            username="john-doe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.username == "john-doe"

    def test_username_with_underscores_allowed(self, session: Session):
        """Test that underscores are allowed in username."""
        # Arrange & Act
        staff = Staff(
            username="john_doe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.username == "john_doe"

    def test_username_with_numbers_allowed(self, session: Session):
        """Test that numbers are allowed in username."""
        # Arrange & Act
        staff = Staff(
            username="john123",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.username == "john123"

    def test_username_strips_whitespace(self, session: Session):
        """Test that whitespace is stripped from username."""
        # Arrange & Act
        staff = Staff(
            username="  jdoe  ",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.username == "jdoe"

    def test_username_minimum_length_valid(self, session: Session):
        """Test username with minimum valid length (3 characters)."""
        # Arrange & Act
        staff = Staff(
            username="abc",
            email="abc@example.com",
            first_name="Test",
            last_name="User",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.username == "abc"

    def test_username_too_short_raises_error(self, session: Session):
        """Test that username shorter than 3 characters raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Username must be at least 3 characters"):
            staff = Staff(
                username="ab",
                email="ab@example.com",
                first_name="Test",
                last_name="User",
            )

    def test_username_empty_raises_error(self, session: Session):
        """Test that empty username raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Username must be at least 3 characters"):
            staff = Staff(
                username="",
                email="test@example.com",
                first_name="Test",
                last_name="User",
            )

    def test_username_with_spaces_raises_error(self, session: Session):
        """Test that username with spaces raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="can only contain lowercase letters"):
            staff = Staff(
                username="john doe",
                email="jdoe@example.com",
                first_name="John",
                last_name="Doe",
            )

    def test_username_with_special_chars_raises_error(self, session: Session):
        """Test that username with special characters raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="can only contain lowercase letters"):
            staff = Staff(
                username="john@doe",
                email="jdoe@example.com",
                first_name="John",
                last_name="Doe",
            )


class TestStaffEmailValidator:
    """Tests for Staff email validation."""

    def test_email_normalized_to_lowercase(self, session: Session):
        """Test that email is normalized to lowercase."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="JOHN.DOE@EXAMPLE.COM",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.email == "john.doe@example.com"

    def test_email_with_plus_sign_valid(self, session: Session):
        """Test that email with plus sign is valid."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="john.doe+test@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.email == "john.doe+test@example.com"

    def test_email_strips_whitespace(self, session: Session):
        """Test that whitespace is stripped from email."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="  jdoe@example.com  ",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.email == "jdoe@example.com"

    def test_email_invalid_format_raises_error(self, session: Session):
        """Test that invalid email format raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email format"):
            staff = Staff(
                username="jdoe",
                email="invalid-email",
                first_name="John",
                last_name="Doe",
            )

    def test_email_missing_at_sign_raises_error(self, session: Session):
        """Test that email without @ raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email format"):
            staff = Staff(
                username="jdoe",
                email="johndoe.example.com",
                first_name="John",
                last_name="Doe",
            )

    def test_email_missing_domain_raises_error(self, session: Session):
        """Test that email without domain raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid email format"):
            staff = Staff(
                username="jdoe",
                email="johndoe@",
                first_name="John",
                last_name="Doe",
            )


class TestStaffNameValidators:
    """Tests for Staff first_name and last_name validation."""

    def test_first_name_strips_whitespace(self, session: Session):
        """Test that first_name strips whitespace."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="  John  ",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.first_name == "John"

    def test_last_name_strips_whitespace(self, session: Session):
        """Test that last_name strips whitespace."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="  Doe  ",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.last_name == "Doe"

    def test_first_name_empty_raises_error(self, session: Session):
        """Test that empty first_name raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="first_name cannot be empty"):
            staff = Staff(
                username="jdoe",
                email="jdoe@example.com",
                first_name="",
                last_name="Doe",
            )

    def test_last_name_empty_raises_error(self, session: Session):
        """Test that empty last_name raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="last_name cannot be empty"):
            staff = Staff(
                username="jdoe",
                email="jdoe@example.com",
                first_name="John",
                last_name="",
            )

    def test_first_name_only_whitespace_raises_error(self, session: Session):
        """Test that first_name with only whitespace raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="first_name cannot be empty"):
            staff = Staff(
                username="jdoe",
                email="jdoe@example.com",
                first_name="   ",
                last_name="Doe",
            )


class TestStaffTrigramValidator:
    """Tests for Staff trigram validation."""

    def test_trigram_converted_to_uppercase(self, session: Session):
        """Test that trigram is converted to uppercase."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            trigram="jdo",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.trigram == "JDO"

    def test_trigram_exactly_three_letters_valid(self, session: Session):
        """Test that trigram with exactly 3 letters is valid."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            trigram="ABC",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.trigram == "ABC"

    def test_trigram_strips_whitespace(self, session: Session):
        """Test that trigram strips whitespace."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            trigram="  ABC  ",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.trigram == "ABC"

    def test_trigram_none_is_valid(self, session: Session):
        """Test that None is a valid value for trigram."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            trigram=None,
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.trigram is None

    def test_trigram_empty_string_converts_to_none(self, session: Session):
        """Test that empty string is converted to None."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            trigram="",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.trigram is None

    def test_trigram_whitespace_only_converts_to_none(self, session: Session):
        """Test that whitespace-only string is converted to None."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            trigram="   ",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.trigram is None

    def test_trigram_too_short_raises_error(self, session: Session):
        """Test that trigram shorter than 3 characters raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Trigram must be exactly 3 characters"):
            staff = Staff(
                username="jdoe",
                email="jdoe@example.com",
                first_name="John",
                last_name="Doe",
                trigram="AB",
            )

    def test_trigram_too_long_raises_error(self, session: Session):
        """Test that trigram longer than 3 characters raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Trigram must be exactly 3 characters"):
            staff = Staff(
                username="jdoe",
                email="jdoe@example.com",
                first_name="John",
                last_name="Doe",
                trigram="ABCD",
            )

    def test_trigram_with_numbers_raises_error(self, session: Session):
        """Test that trigram with numbers raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Trigram must contain only letters"):
            staff = Staff(
                username="jdoe",
                email="jdoe@example.com",
                first_name="John",
                last_name="Doe",
                trigram="AB1",
            )

    def test_trigram_with_special_chars_raises_error(self, session: Session):
        """Test that trigram with special characters raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Trigram must contain only letters"):
            staff = Staff(
                username="jdoe",
                email="jdoe@example.com",
                first_name="John",
                last_name="Doe",
                trigram="AB-",
            )


class TestStaffPhoneValidator:
    """Tests for Staff phone validation."""

    def test_phone_valid_e164_format(self, session: Session):
        """Test that valid E.164 format phone is accepted."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            phone="+56912345678",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.phone == "+56912345678"

    def test_phone_with_spaces_valid(self, session: Session):
        """Test that phone with spaces is accepted."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            phone="+56 9 1234 5678",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.phone == "+56 9 1234 5678"

    def test_phone_with_hyphens_valid(self, session: Session):
        """Test that phone with hyphens is accepted."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            phone="+56-9-1234-5678",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.phone == "+56-9-1234-5678"

    def test_phone_none_is_valid(self, session: Session):
        """Test that None is a valid value for phone."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            phone=None,
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.phone is None

    def test_phone_too_short_raises_error(self, session: Session):
        """Test that phone shorter than 8 digits raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Phone must be 8-15 digits"):
            staff = Staff(
                username="jdoe",
                email="jdoe@example.com",
                first_name="John",
                last_name="Doe",
                phone="+123456",
            )

    def test_phone_too_long_raises_error(self, session: Session):
        """Test that phone longer than 15 digits raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Phone must be 8-15 digits"):
            staff = Staff(
                username="jdoe",
                email="jdoe@example.com",
                first_name="John",
                last_name="Doe",
                phone="+12345678901234567",
            )

    def test_phone_with_letters_raises_error(self, session: Session):
        """Test that phone with letters raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Phone must be 8-15 digits"):
            staff = Staff(
                username="jdoe",
                email="jdoe@example.com",
                first_name="John",
                last_name="Doe",
                phone="+56ABC1234567",
            )


class TestStaffPositionValidator:
    """Tests for Staff position validation."""

    def test_position_strips_whitespace(self, session: Session):
        """Test that position strips whitespace."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            position="  Sales Manager  ",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.position == "Sales Manager"

    def test_position_none_is_valid(self, session: Session):
        """Test that None is a valid value for position."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            position=None,
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.position is None

    def test_position_empty_string_converts_to_none(self, session: Session):
        """Test that empty string is converted to None."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            position="",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.position is None

    def test_position_whitespace_only_converts_to_none(self, session: Session):
        """Test that whitespace-only string is converted to None."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            position="   ",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.position is None


class TestStaffProperties:
    """Tests for Staff model properties."""

    def test_full_name_property(self, session: Session):
        """Test that full_name property returns first_name + last_name."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.full_name == "John Doe"

    def test_full_name_with_multiple_names(self, session: Session):
        """Test full_name with multiple first/last names."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John Michael",
            last_name="Doe Smith",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.full_name == "John Michael Doe Smith"


class TestStaffRepr:
    """Tests for Staff __repr__ method."""

    def test_repr_with_trigram(self, session: Session):
        """Test __repr__ includes trigram when present."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            trigram="JDO",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        repr_str = repr(staff)
        assert "Staff" in repr_str
        assert f"id={staff.id}" in repr_str
        assert "username=jdoe" in repr_str
        assert "trigram=JDO" in repr_str
        assert "active=True" in repr_str

    def test_repr_without_trigram(self, session: Session):
        """Test __repr__ without trigram."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            trigram=None,
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        repr_str = repr(staff)
        assert "Staff" in repr_str
        assert f"id={staff.id}" in repr_str
        assert "username=jdoe" in repr_str
        assert "trigram" not in repr_str or "trigram=None" not in repr_str
        assert "active=True" in repr_str

    def test_repr_inactive_staff(self, session: Session):
        """Test __repr__ shows inactive status."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            is_active=False,
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        repr_str = repr(staff)
        assert "active=False" in repr_str


class TestStaffUniqueConstraints:
    """Tests for Staff unique constraints."""

    def test_username_must_be_unique(self, session: Session):
        """Test that username must be unique."""
        # Arrange
        staff1 = Staff(
            username="jdoe",
            email="jdoe1@example.com",
            first_name="John",
            last_name="Doe",
        )
        staff2 = Staff(
            username="jdoe",
            email="jdoe2@example.com",
            first_name="Jane",
            last_name="Doe",
        )
        session.add(staff1)
        session.commit()

        # Act & Assert
        with pytest.raises(IntegrityError):
            session.add(staff2)
            session.commit()

    def test_email_must_be_unique(self, session: Session):
        """Test that email must be unique."""
        # Arrange
        staff1 = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        staff2 = Staff(
            username="janedoe",
            email="jdoe@example.com",
            first_name="Jane",
            last_name="Doe",
        )
        session.add(staff1)
        session.commit()

        # Act & Assert
        with pytest.raises(IntegrityError):
            session.add(staff2)
            session.commit()

    def test_trigram_must_be_unique_when_not_null(self, session: Session):
        """Test that trigram must be unique when not null."""
        # Arrange
        staff1 = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            trigram="JDO",
        )
        staff2 = Staff(
            username="janedoe",
            email="jane@example.com",
            first_name="Jane",
            last_name="Doe",
            trigram="JDO",
        )
        session.add(staff1)
        session.commit()

        # Act & Assert
        with pytest.raises(IntegrityError):
            session.add(staff2)
            session.commit()

    def test_multiple_staff_with_null_trigram_allowed(self, session: Session):
        """Test that multiple staff members can have null trigram."""
        # Arrange & Act
        staff1 = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            trigram=None,
        )
        staff2 = Staff(
            username="janedoe",
            email="jane@example.com",
            first_name="Jane",
            last_name="Doe",
            trigram=None,
        )
        session.add(staff1)
        session.add(staff2)
        session.commit()

        # Assert
        assert staff1.id is not None
        assert staff2.id is not None
        assert staff1.trigram is None
        assert staff2.trigram is None


class TestStaffTimestampMixin:
    """Tests for Staff TimestampMixin behavior."""

    def test_created_at_set_on_creation(self, session: Session):
        """Test that created_at is set automatically on creation."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.created_at is not None

    def test_updated_at_set_on_creation(self, session: Session):
        """Test that updated_at is set automatically on creation."""
        # Arrange & Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.updated_at is not None

    def test_updated_at_changes_on_update(self, session: Session):
        """Test that updated_at is updated when record changes."""
        # Arrange
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)
        original_updated_at = staff.updated_at

        # Act - Update the staff
        import time
        time.sleep(0.01)  # Small delay to ensure timestamp difference
        staff.position = "New Position"
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.updated_at > original_updated_at


class TestStaffAuditMixin:
    """Tests for Staff AuditMixin behavior."""

    def test_created_by_id_set_from_session_context(self, session: Session):
        """Test that created_by_id is set from session context."""
        # Arrange
        session.info["user_id"] = 42

        # Act
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.created_by_id == 42

    def test_updated_by_id_set_from_session_context(self, session: Session):
        """Test that updated_by_id is set from session context."""
        # Arrange
        session.info["user_id"] = 42
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        session.refresh(staff)

        # Act - Update with different user
        session.info["user_id"] = 99
        staff.position = "Updated Position"
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.created_by_id == 42
        assert staff.updated_by_id == 99


class TestStaffCRUDOperations:
    """Tests for Staff CRUD operations."""

    def test_read_staff_by_id(self, session: Session):
        """Test reading Staff by ID."""
        # Arrange
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        staff_id = staff.id

        # Act
        retrieved_staff = session.query(Staff).filter_by(id=staff_id).first()

        # Assert
        assert retrieved_staff is not None
        assert retrieved_staff.id == staff_id
        assert retrieved_staff.username == "jdoe"

    def test_update_staff(self, session: Session):
        """Test updating Staff fields."""
        # Arrange
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()

        # Act
        staff.position = "Senior Manager"
        staff.phone = "+56987654321"
        session.commit()
        session.refresh(staff)

        # Assert
        assert staff.position == "Senior Manager"
        assert staff.phone == "+56987654321"

    def test_delete_staff(self, session: Session):
        """Test deleting Staff."""
        # Arrange
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()
        staff_id = staff.id

        # Act
        session.delete(staff)
        session.commit()

        # Assert
        deleted_staff = session.query(Staff).filter_by(id=staff_id).first()
        assert deleted_staff is None

    def test_query_active_staff(self, session: Session):
        """Test querying only active staff."""
        # Arrange
        active_staff = Staff(
            username="active",
            email="active@example.com",
            first_name="Active",
            last_name="User",
            is_active=True,
        )
        inactive_staff = Staff(
            username="inactive",
            email="inactive@example.com",
            first_name="Inactive",
            last_name="User",
            is_active=False,
        )
        session.add_all([active_staff, inactive_staff])
        session.commit()

        # Act
        active_results = session.query(Staff).filter_by(is_active=True).all()

        # Assert
        assert len(active_results) == 1
        assert active_results[0].username == "active"

    def test_query_admin_staff(self, session: Session):
        """Test querying only admin staff."""
        # Arrange
        admin_staff = Staff(
            username="admin",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True,
        )
        regular_staff = Staff(
            username="user",
            email="user@example.com",
            first_name="Regular",
            last_name="User",
            is_admin=False,
        )
        session.add_all([admin_staff, regular_staff])
        session.commit()

        # Act
        admin_results = session.query(Staff).filter_by(is_admin=True).all()

        # Assert
        assert len(admin_results) == 1
        assert admin_results[0].username == "admin"

    def test_query_staff_by_username(self, session: Session):
        """Test querying Staff by username."""
        # Arrange
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()

        # Act
        result = session.query(Staff).filter_by(username="jdoe").first()

        # Assert
        assert result is not None
        assert result.email == "jdoe@example.com"

    def test_query_staff_by_email(self, session: Session):
        """Test querying Staff by email."""
        # Arrange
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
        )
        session.add(staff)
        session.commit()

        # Act
        result = session.query(Staff).filter_by(email="jdoe@example.com").first()

        # Assert
        assert result is not None
        assert result.username == "jdoe"

    def test_query_staff_by_trigram(self, session: Session):
        """Test querying Staff by trigram."""
        # Arrange
        staff = Staff(
            username="jdoe",
            email="jdoe@example.com",
            first_name="John",
            last_name="Doe",
            trigram="JDO",
        )
        session.add(staff)
        session.commit()

        # Act
        result = session.query(Staff).filter_by(trigram="JDO").first()

        # Assert
        assert result is not None
        assert result.username == "jdoe"
