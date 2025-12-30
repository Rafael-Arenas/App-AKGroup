"""
Sequence service for generating standardized document numbers.
"""

from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from src.backend.models.core.sequences import Sequence
from src.backend.config.settings import settings
from src.backend.utils.logger import logger

class SequenceService:
    """
    Service for managing document sequences and numbering.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_next_number(self, name: str, prefix: str = None, year: int = None, trigram: str = None) -> int:
        """
        Get the next sequential number and increment the counter.
        
        Args:
            name: Sequence name
            prefix: Optional prefix filter
            year: Year for the sequence (defaults to current year)
            
        Returns:
            Next integer in the sequence
            trigram: Optional trigram filter
            
        Returns:
            The next integer value in the sequence
        """
        sequence = self.session.query(Sequence).filter(
            Sequence.name == name,
            Sequence.year == year,
            Sequence.prefix == prefix,
            Sequence.trigram == trigram
        ).with_for_update().first()

        if not sequence:
            logger.info(f"Creating new sequence: {name} for year {year} (prefix={prefix}, trigram={trigram})")
            sequence = Sequence(
                name=name,
                year=year,
                prefix=prefix,
                trigram=trigram,
                last_value=0
            )
            self.session.add(sequence)
            self.session.flush()

        sequence.last_value += 1
        sequence.updated_at = datetime.now()
        # We don't commit here, we let the calling service handle the transaction
        
        return sequence.last_value

    def generate_document_number(self, prefix: str, company_trigram: str = None) -> str:
        """
        Generate a formatted document number (e.g., C-2025-MDO-001).
        
        Args:
            prefix: Document type prefix (C, OC, DOC)
            company_trigram: Optional 3-letter company code. 
                             If not provided, uses the internal company trigram from settings.
        
        Returns:
            Formatted document number string
        """
        year = date.today().year
        trigram = (company_trigram or settings.internal_company_trigram).upper()
        
        # We use a shared sequence across all prefixes but per trigram+year
        # If the user wants separate counters per prefix, we would pass prefix=prefix
        next_val = self.get_next_number(
            name="global_document_sequence", 
            year=year, 
            prefix=None, # Global sequence across C, OC, DOC
            trigram=trigram
        )

        return f"{prefix}-{year}-{trigram}-{next_val:03d}"
