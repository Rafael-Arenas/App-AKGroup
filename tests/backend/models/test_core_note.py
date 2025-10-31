"""
Tests for Note and NotePriority models from core.notes.

This module contains comprehensive tests for the polymorphic notes system,
including CRUD operations, validators, relationships, and edge cases.

Test Coverage:
    Note:
        - Basic CRUD operations
        - Field validation (entity_type, entity_id, content)
        - Priority levels (NotePriority enum)
        - Polymorphic association pattern
        - Category classification
        - Indexes (entity lookup, priority filtering)
        - Mixins (Timestamp, Audit)
        - Edge cases (unknown entity types, empty content)

    NotePriority:
        - Enum values (LOW, NORMAL, HIGH, URGENT)
        - Default priority behavior
"""

import warnings

import pytest
from sqlalchemy.exc import IntegrityError

from src.backend.models.core.notes import Note, NotePriority


# ============= NOTE PRIORITY ENUM TESTS =============


class TestNotePriorityEnum:
    """Tests for NotePriority enum."""

    def test_priority_enum_values(self):
        """Test that NotePriority has all expected values."""
        assert NotePriority.LOW == "low"
        assert NotePriority.NORMAL == "normal"
        assert NotePriority.HIGH == "high"
        assert NotePriority.URGENT == "urgent"

    def test_priority_enum_members(self):
        """Test enum members list."""
        priorities = list(NotePriority)
        assert len(priorities) == 4
        assert NotePriority.LOW in priorities
        assert NotePriority.NORMAL in priorities
        assert NotePriority.HIGH in priorities
        assert NotePriority.URGENT in priorities


# ============= NOTE MODEL TESTS =============


class TestNoteCreation:
    """Tests for Note model instantiation and creation."""

    def test_create_note_with_valid_data(self, session):
        """
        Test creating a Note with all valid fields.

        Verifies that a Note can be created with complete data and
        all fields are properly stored.
        """
        # Arrange & Act
        note = Note(
            entity_type="company",
            entity_id=123,
            title="Important Reminder",
            content="Client prefers Tuesday deliveries",
            priority=NotePriority.HIGH,
            category="Commercial",
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        # Assert
        assert note.id is not None
        assert note.entity_type == "company"
        assert note.entity_id == 123
        assert note.title == "Important Reminder"
        assert note.content == "Client prefers Tuesday deliveries"
        assert note.priority == NotePriority.HIGH
        assert note.category == "Commercial"

    def test_create_note_minimal_fields(self, session):
        """Test creating Note with only required fields."""
        # Arrange & Act
        note = Note(
            entity_type="product",
            entity_id=456,
            content="Check minimum stock",
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        # Assert
        assert note.id is not None
        assert note.entity_type == "product"
        assert note.entity_id == 456
        assert note.content == "Check minimum stock"
        assert note.title is None
        assert note.priority == NotePriority.NORMAL  # Default value
        assert note.category is None

    def test_create_note_without_optional_fields(self, session):
        """Test that title and category can be None."""
        # Arrange & Act
        note = Note(
            entity_type="quote",
            entity_id=789,
            content="Follow up required",
            title=None,
            category=None,
        )
        session.add(note)
        session.commit()

        # Assert
        assert note.id is not None
        assert note.title is None
        assert note.category is None

    @pytest.mark.parametrize(
        "entity_type,entity_id,priority",
        [
            ("company", 1, NotePriority.LOW),
            ("product", 2, NotePriority.NORMAL),
            ("quote", 3, NotePriority.HIGH),
            ("order", 4, NotePriority.URGENT),
            ("invoice", 5, NotePriority.NORMAL),
        ],
    )
    def test_create_notes_for_different_entities(
        self, session, entity_type, entity_id, priority
    ):
        """Test creating notes for various entity types."""
        # Arrange & Act
        note = Note(
            entity_type=entity_type,
            entity_id=entity_id,
            content=f"Note for {entity_type} {entity_id}",
            priority=priority,
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        # Assert
        assert note.entity_type == entity_type
        assert note.entity_id == entity_id
        assert note.priority == priority


class TestNoteValidation:
    """Tests for Note field validators."""

    def test_entity_type_validator_normalizes_to_lowercase(self, session):
        """Test that entity_type is normalized to lowercase."""
        # Arrange & Act
        note = Note(
            entity_type="COMPANY",  # Uppercase
            entity_id=1,
            content="Test note",
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        # Assert
        assert note.entity_type == "company"  # Lowercase

    def test_entity_type_validator_strips_whitespace(self, session):
        """Test that entity_type strips leading/trailing whitespace."""
        # Arrange & Act
        note = Note(
            entity_type="  product  ",
            entity_id=1,
            content="Test note",
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        # Assert
        assert note.entity_type == "product"  # Whitespace removed

    def test_entity_type_validator_rejects_empty_string(self, session):
        """Test that entity_type cannot be empty."""
        with pytest.raises(ValueError, match="entity_type cannot be empty"):
            note = Note(
                entity_type="",
                entity_id=1,
                content="Test note",
            )
            session.add(note)
            session.flush()

    def test_entity_type_validator_rejects_whitespace_only(self, session):
        """Test that entity_type cannot be whitespace only."""
        with pytest.raises(ValueError, match="entity_type cannot be empty"):
            note = Note(
                entity_type="   ",
                entity_id=1,
                content="Test note",
            )
            session.add(note)
            session.flush()

    def test_entity_type_warns_on_unknown_type(self, session):
        """Test that unknown entity_type triggers warning but is allowed."""
        # Arrange & Act
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            note = Note(
                entity_type="unknown_entity",
                entity_id=1,
                content="Test note",
            )
            session.add(note)
            session.commit()

            # Assert warning was raised
            assert len(w) == 1
            assert "not in known types" in str(w[0].message)
            assert note.entity_type == "unknown_entity"

    def test_entity_id_must_be_positive(self, session):
        """Test that entity_id must be a positive integer."""
        # Test zero
        with pytest.raises(ValueError, match="must be a positive integer"):
            note = Note(
                entity_type="company",
                entity_id=0,
                content="Test note",
            )
            session.add(note)
            session.flush()

        session.rollback()

        # Test negative
        with pytest.raises(ValueError, match="must be a positive integer"):
            note = Note(
                entity_type="company",
                entity_id=-1,
                content="Test note",
            )
            session.add(note)
            session.flush()

    def test_entity_id_cannot_be_none(self, session):
        """Test that entity_id is required."""
        with pytest.raises((ValueError, IntegrityError)):
            note = Note(
                entity_type="company",
                entity_id=None,
                content="Test note",
            )
            session.add(note)
            session.flush()

    def test_content_validator_strips_whitespace(self, session):
        """Test that content strips leading/trailing whitespace."""
        # Arrange & Act
        note = Note(
            entity_type="company",
            entity_id=1,
            content="  Important note  ",
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        # Assert
        assert note.content == "Important note"

    def test_content_cannot_be_empty(self, session):
        """Test that content cannot be empty."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            note = Note(
                entity_type="company",
                entity_id=1,
                content="",
            )
            session.add(note)
            session.flush()

    def test_content_cannot_be_whitespace_only(self, session):
        """Test that content cannot be whitespace only."""
        with pytest.raises(ValueError, match="content cannot be empty"):
            note = Note(
                entity_type="company",
                entity_id=1,
                content="    ",
            )
            session.add(note)
            session.flush()

    def test_content_cannot_be_none(self, session):
        """Test that content is required."""
        with pytest.raises((ValueError, IntegrityError)):
            note = Note(
                entity_type="company",
                entity_id=1,
                content=None,
            )
            session.add(note)
            session.commit()


class TestNotePriority:
    """Tests for Note priority field."""

    def test_default_priority_is_normal(self, session):
        """Test that priority defaults to NORMAL."""
        # Arrange & Act
        note = Note(
            entity_type="company",
            entity_id=1,
            content="Test note",
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        # Assert
        assert note.priority == NotePriority.NORMAL

    @pytest.mark.parametrize(
        "priority",
        [
            NotePriority.LOW,
            NotePriority.NORMAL,
            NotePriority.HIGH,
            NotePriority.URGENT,
        ],
    )
    def test_all_priority_levels(self, session, priority):
        """Test creating notes with all priority levels."""
        # Arrange & Act
        note = Note(
            entity_type="company",
            entity_id=1,
            content="Test note",
            priority=priority,
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        # Assert
        assert note.priority == priority

    def test_filter_notes_by_priority(self, session):
        """Test filtering notes by priority level."""
        # Arrange - Create notes with different priorities
        notes = [
            Note(
                entity_type="company",
                entity_id=1,
                content="Low priority",
                priority=NotePriority.LOW,
            ),
            Note(
                entity_type="company",
                entity_id=1,
                content="Normal priority",
                priority=NotePriority.NORMAL,
            ),
            Note(
                entity_type="company",
                entity_id=1,
                content="High priority",
                priority=NotePriority.HIGH,
            ),
            Note(
                entity_type="company",
                entity_id=1,
                content="Urgent",
                priority=NotePriority.URGENT,
            ),
        ]
        session.add_all(notes)
        session.commit()

        # Act - Query urgent notes
        urgent_notes = (
            session.query(Note).filter_by(priority=NotePriority.URGENT).all()
        )

        # Assert
        assert len(urgent_notes) == 1
        assert urgent_notes[0].content == "Urgent"


class TestNoteCRUD:
    """Tests for CRUD operations on Note model."""

    def test_read_note_by_id(self, session):
        """Test reading a note by primary key."""
        # Arrange
        note = Note(
            entity_type="company",
            entity_id=1,
            content="Test note",
        )
        session.add(note)
        session.commit()
        note_id = note.id

        # Act
        retrieved = session.query(Note).filter_by(id=note_id).first()

        # Assert
        assert retrieved is not None
        assert retrieved.id == note_id
        assert retrieved.content == "Test note"

    def test_read_notes_by_entity(self, session):
        """Test querying notes for a specific entity."""
        # Arrange - Create notes for different entities
        company_notes = [
            Note(entity_type="company", entity_id=1, content="Note 1"),
            Note(entity_type="company", entity_id=1, content="Note 2"),
        ]
        product_note = Note(entity_type="product", entity_id=2, content="Product note")

        session.add_all(company_notes + [product_note])
        session.commit()

        # Act
        retrieved = (
            session.query(Note)
            .filter_by(entity_type="company", entity_id=1)
            .all()
        )

        # Assert
        assert len(retrieved) == 2
        assert all(n.entity_type == "company" for n in retrieved)
        assert all(n.entity_id == 1 for n in retrieved)

    def test_update_note(self, session):
        """Test updating note fields."""
        # Arrange
        note = Note(
            entity_type="company",
            entity_id=1,
            content="Original content",
            priority=NotePriority.NORMAL,
        )
        session.add(note)
        session.commit()
        original_created_at = note.created_at

        # Act
        note.content = "Updated content"
        note.priority = NotePriority.HIGH
        note.category = "Updated Category"
        session.commit()
        session.refresh(note)

        # Assert
        assert note.content == "Updated content"
        assert note.priority == NotePriority.HIGH
        assert note.category == "Updated Category"
        assert note.created_at == original_created_at
        assert note.updated_at > original_created_at

    def test_delete_note(self, session):
        """Test deleting a note."""
        # Arrange
        note = Note(
            entity_type="company",
            entity_id=1,
            content="To be deleted",
        )
        session.add(note)
        session.commit()
        note_id = note.id

        # Act
        session.delete(note)
        session.commit()

        # Assert
        deleted = session.query(Note).filter_by(id=note_id).first()
        assert deleted is None


class TestNotePolymorphicPattern:
    """Tests for polymorphic association pattern."""

    def test_multiple_notes_for_same_entity(self, session):
        """Test that an entity can have multiple notes."""
        # Arrange & Act
        notes = [
            Note(entity_type="company", entity_id=1, content="First note"),
            Note(entity_type="company", entity_id=1, content="Second note"),
            Note(entity_type="company", entity_id=1, content="Third note"),
        ]
        session.add_all(notes)
        session.commit()

        # Assert
        company_notes = (
            session.query(Note)
            .filter_by(entity_type="company", entity_id=1)
            .all()
        )
        assert len(company_notes) == 3

    def test_notes_for_different_entities(self, session):
        """Test notes associated with different entity types."""
        # Arrange & Act
        notes = [
            Note(entity_type="company", entity_id=1, content="Company note"),
            Note(entity_type="product", entity_id=2, content="Product note"),
            Note(entity_type="quote", entity_id=3, content="Quote note"),
            Note(entity_type="order", entity_id=4, content="Order note"),
        ]
        session.add_all(notes)
        session.commit()

        # Assert - Each entity type has its notes
        for entity_type in ["company", "product", "quote", "order"]:
            notes = session.query(Note).filter_by(entity_type=entity_type).all()
            assert len(notes) == 1

    def test_filter_notes_by_entity_and_priority(self, session):
        """Test filtering by both entity and priority."""
        # Arrange
        notes = [
            Note(
                entity_type="company",
                entity_id=1,
                content="Low",
                priority=NotePriority.LOW,
            ),
            Note(
                entity_type="company",
                entity_id=1,
                content="High",
                priority=NotePriority.HIGH,
            ),
            Note(
                entity_type="product",
                entity_id=2,
                content="High product",
                priority=NotePriority.HIGH,
            ),
        ]
        session.add_all(notes)
        session.commit()

        # Act - Query high priority company notes
        high_company_notes = (
            session.query(Note)
            .filter_by(
                entity_type="company",
                entity_id=1,
                priority=NotePriority.HIGH,
            )
            .all()
        )

        # Assert
        assert len(high_company_notes) == 1
        assert high_company_notes[0].content == "High"


class TestNoteCategory:
    """Tests for Note category field."""

    def test_category_can_be_set(self, session):
        """Test that category can be set."""
        # Arrange & Act
        note = Note(
            entity_type="company",
            entity_id=1,
            content="Test note",
            category="Technical",
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        # Assert
        assert note.category == "Technical"

    def test_category_can_be_none(self, session):
        """Test that category is optional."""
        # Arrange & Act
        note = Note(
            entity_type="company",
            entity_id=1,
            content="Test note",
            category=None,
        )
        session.add(note)
        session.commit()

        # Assert
        assert note.category is None

    def test_filter_notes_by_category(self, session):
        """Test filtering notes by category."""
        # Arrange
        notes = [
            Note(
                entity_type="company",
                entity_id=1,
                content="Tech note",
                category="Technical",
            ),
            Note(
                entity_type="company",
                entity_id=1,
                content="Com note",
                category="Commercial",
            ),
            Note(
                entity_type="company",
                entity_id=1,
                content="No category",
                category=None,
            ),
        ]
        session.add_all(notes)
        session.commit()

        # Act
        technical_notes = session.query(Note).filter_by(category="Technical").all()

        # Assert
        assert len(technical_notes) == 1
        assert technical_notes[0].content == "Tech note"


class TestNoteMixins:
    """Tests for Note mixins (Timestamp, Audit)."""

    def test_timestamp_mixin_creates_timestamps(self, session):
        """Test that TimestampMixin sets created_at and updated_at."""
        # Arrange & Act
        note = Note(
            entity_type="company",
            entity_id=1,
            content="Test note",
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        # Assert
        assert note.created_at is not None
        assert note.updated_at is not None

    def test_audit_mixin_sets_created_by(self, session):
        """Test AuditMixin sets created_by_id from session context."""
        # Session has user_id = 1 set in conftest
        note = Note(
            entity_type="company",
            entity_id=1,
            content="Test note",
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        assert note.created_by_id == 1


class TestNoteRepr:
    """Tests for Note __repr__ method."""

    def test_repr_method(self, session):
        """Test string representation of Note."""
        note = Note(
            entity_type="company",
            entity_id=123,
            content="Test note",
            priority=NotePriority.HIGH,
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        repr_str = repr(note)
        assert "Note" in repr_str
        assert "company" in repr_str
        assert "123" in repr_str
        assert "high" in repr_str


class TestNoteEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_very_long_content(self, session):
        """Test note with very long content (Text field)."""
        # Arrange - Create note with long content
        long_content = "A" * 10000  # 10,000 characters
        note = Note(
            entity_type="company",
            entity_id=1,
            content=long_content,
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        # Assert
        assert len(note.content) == 10000

    def test_special_characters_in_content(self, session):
        """Test that content accepts special characters and unicode."""
        # Arrange & Act
        note = Note(
            entity_type="company",
            entity_id=1,
            content="Special chars: €, £, ñ, á, 中文",
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        # Assert
        assert "€" in note.content
        assert "中文" in note.content

    def test_title_with_max_length(self, session):
        """Test title with maximum length (200 chars)."""
        # Arrange
        long_title = "T" * 200
        note = Note(
            entity_type="company",
            entity_id=1,
            title=long_title,
            content="Test",
        )
        session.add(note)
        session.commit()
        session.refresh(note)

        # Assert
        assert len(note.title) == 200

    def test_concurrent_note_creation(self, session):
        """Test creating multiple notes in same transaction."""
        # Arrange
        notes = [
            Note(entity_type="company", entity_id=i, content=f"Note {i}")
            for i in range(1, 11)
        ]

        # Act
        session.add_all(notes)
        session.commit()

        # Assert
        count = session.query(Note).count()
        assert count == 10


class TestNoteIndexes:
    """Tests for database indexes."""

    def test_entity_composite_index(self, session):
        """Test that composite index on entity_type + entity_id works efficiently."""
        # Arrange - Create many notes
        for i in range(1, 101):  # Start from 1 to avoid entity_id=0
            note = Note(
                entity_type="company",
                entity_id=(i % 10) + 1,  # Range 1-10 instead of 0-9
                content=f"Note {i}",
            )
            session.add(note)
        session.commit()

        # Act - Query using indexed columns
        result = (
            session.query(Note)
            .filter_by(entity_type="company", entity_id=5)
            .all()
        )

        # Assert
        assert len(result) == 10

    def test_priority_type_index(self, session):
        """Test that priority + entity_type index works efficiently."""
        # Arrange - Create notes with various priorities
        for priority in NotePriority:
            for i in range(1, 6):  # Start from 1 to avoid entity_id=0
                note = Note(
                    entity_type="company",
                    entity_id=i,
                    content=f"Note {priority.value}",
                    priority=priority,
                )
                session.add(note)
        session.commit()

        # Act - Query using indexed columns
        result = (
            session.query(Note)
            .filter_by(priority=NotePriority.URGENT, entity_type="company")
            .all()
        )

        # Assert
        assert len(result) == 5
