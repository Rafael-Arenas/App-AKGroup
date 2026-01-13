"""add order_products table

Revision ID: 1782d0df07a8
Revises: add_customer_po_number
Create Date: 2026-01-13 17:21:53.795311

"""
from typing import Sequence, Union
from decimal import Decimal

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1782d0df07a8'
down_revision: Union[str, Sequence[str], None] = 'add_customer_po_number'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create order_products table
    op.create_table(
        'order_products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id', ondelete='RESTRICT'), nullable=False, index=True),
        sa.Column('sequence', sa.Integer(), nullable=False, default=1),
        sa.Column('quantity', sa.DECIMAL(10, 3), nullable=False),
        sa.Column('unit_price', sa.DECIMAL(15, 2), nullable=False),
        sa.Column('discount_percentage', sa.DECIMAL(5, 2), nullable=False, default=Decimal("0.00")),
        sa.Column('discount_amount', sa.DECIMAL(15, 2), nullable=False, default=Decimal("0.00")),
        sa.Column('subtotal', sa.DECIMAL(15, 2), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.CheckConstraint('quantity > 0', name='ck_order_product_quantity_positive'),
        sa.CheckConstraint('unit_price >= 0', name='ck_order_product_price_positive'),
        sa.CheckConstraint('discount_percentage >= 0 AND discount_percentage <= 100', name='ck_order_product_discount_percentage_valid'),
        sa.CheckConstraint('discount_amount >= 0', name='ck_order_product_discount_positive'),
        sa.CheckConstraint('subtotal >= 0', name='ck_order_product_subtotal_positive'),
    )
    
    # Create index
    op.create_index('ix_order_product_order', 'order_products', ['order_id', 'sequence'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_order_product_order', table_name='order_products')
    op.drop_table('order_products')
