"""
Sequence model for document numbering.

This module contains the Sequence model used to track and generate 
sequential numbers for business documents.
"""

from typing import TYPE_CHECKING

from sqlalchemy import Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

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
        trigram: Optional company code for per-company sequences
        last_value: Last used value in the sequence
    """

    __tablename__ = "sequences"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(
        String(50), index=True, comment="Sequence name"
    )
    year: Mapped[int] = mapped_column(index=True, comment="Year for this sequence")
    prefix: Mapped[str | None] = mapped_column(
        String(10),
        index=True,
        comment="Optional prefix for the sequence (e.g., 'C', 'OC', 'DOC')",
    )
    trigram: Mapped[str | None] = mapped_column(
        String(3),
        index=True,
        comment="Three-letter company code (optional, for per-company sequences)",
    )
    last_value: Mapped[int] = mapped_column(
        default=0, comment="Last sequential value generated"
    )

    __table_args__ = (
        UniqueConstraint(
            "name", "year", "prefix", "trigram", name="uq_sequence_name_year_prefix_trigram"
        ),
        Index("ix_sequences_lookup", "name", "year", "prefix", "trigram"),
    )

    def __repr__(self) -> str:
        return f"<Sequence(id={self.id}, name='{self.name}', year={self.year}, last_value={self.last_value})>"
