"""Add sequences table

Revision ID: a2ea0f1e2dc9
Revises: 0dd3f1c106bf
Create Date: 2025-12-29 18:04:37.450243

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2ea0f1e2dc9'
down_revision: Union[str, Sequence[str], None] = '0dd3f1c106bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'sequences',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('prefix', sa.String(length=20), nullable=True),
        sa.Column('last_value', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_sequences')),
        sa.UniqueConstraint('name', 'year', 'prefix', name='uq_sequence_name_year_prefix')
    )
    op.create_index(op.f('ix_sequences_name'), 'sequences', ['name'], unique=False)
    op.create_index(op.f('ix_sequences_year'), 'sequences', ['year'], unique=False)
    op.create_index('ix_sequences_lookup', 'sequences', ['name', 'year', 'prefix'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_sequences_lookup', table_name='sequences')
    op.drop_index(op.f('ix_sequences_year'), table_name='sequences')
    op.drop_index(op.f('ix_sequences_name'), table_name='sequences')
    op.drop_table('sequences')

