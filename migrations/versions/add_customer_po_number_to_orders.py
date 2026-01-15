"""Add customer_po_number to orders table

Revision ID: add_customer_po_number
Revises: 735494c7fad2
Create Date: 2026-01-08 12:27:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_customer_po_number'
down_revision: Union[str, Sequence[str], None] = '735494c7fad2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add customer_po_number column to orders table."""
    op.add_column('orders', sa.Column('customer_po_number', sa.String(length=100), nullable=True, comment="Customer's purchase order number"))
    op.create_index(op.f('ix_orders_customer_po_number'), 'orders', ['customer_po_number'], unique=False)


def downgrade() -> None:
    """Remove customer_po_number column from orders table."""
    op.drop_index(op.f('ix_orders_customer_po_number'), table_name='orders')
    op.drop_column('orders', 'customer_po_number')
