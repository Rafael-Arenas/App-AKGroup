"""
Sequence model for document numbering.

This module contains the Sequence model used to track and generate 
sequential numbers for business documents.
"""

from sqlalchemy import Column, Integer, String, Index, UniqueConstraint
from ..base import Base, TimestampMixin


class Sequence(Base, TimestampMixin):
    """
    Sequence tracking model.
    
    Used to maintain sequential numbers for documents like quotes, 
    orders, and deliveries.
    
    Attributes:
        id: Primary key
        name: Name of the sequence (e.g., "document_sequence")
        year: Year for the sequence (numbers reset or track per year)
        prefix: Optional prefix for the sequence
        last_value: Last used value in the sequence
    """
    __tablename__ = "sequences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, index=True, comment="Sequence name")
    year = Column(Integer, nullable=False, index=True, comment="Year for this sequence")
    prefix = Column(
        String(10),
        nullable=True,
        index=True,
        comment="Optional prefix for the sequence (e.g., 'C', 'OC', 'DOC')"
    )

    trigram = Column(
        String(3),
        nullable=True,
        index=True,
        comment="Three-letter company code (optional, for per-company sequences)"
    )

    last_value = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Last sequential value generated"
    )
    __table_args__ = (
        UniqueConstraint("name", "year", "prefix", name="uq_sequence_name_year_prefix"),
        Index("ix_sequences_lookup", "name", "year", "prefix"),
    )

    def __repr__(self) -> str:
        return f"<Sequence(id={self.id}, name='{self.name}', year={self.year}, last_value={self.last_value})>"
