"""create shop tables (shop_products, shop_discounts, shop_transactions)

Revision ID: 20250813_create_shop_tables
Revises: 20250813_user_actions_ix_type_created
Create Date: 2025-08-13

This migration is idempotent and will safely create the shop tables if they do not exist.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250813_create_shop_tables'
# Chain after the user_actions index migration to keep a single head

down_revision: Union[str, None] = '20250813_user_actions_ix_type_created'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(insp, table: str) -> bool:
    try:
        return table in insp.get_table_names()
    except Exception:
        return False


def _has_column(insp, table: str, col: str) -> bool:
    try:
        return any(c['name'] == col for c in insp.get_columns(table))
    except Exception:
        return False


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # shop_products
    if not _has_table(insp, 'shop_products'):
        op.create_table(
            'shop_products',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('product_id', sa.String(length=100), nullable=False),
            sa.Column('name', sa.String(length=200), nullable=False),
            sa.Column('description', sa.String(length=1000), nullable=True),
            sa.Column('price', sa.Integer(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('extra', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
        )
        op.create_index('ix_shop_products_product_id', 'shop_products', ['product_id'], unique=True)

    # shop_discounts
    if not _has_table(insp, 'shop_discounts'):
        op.create_table(
            'shop_discounts',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('product_id', sa.String(length=100), nullable=False),
            sa.Column('discount_type', sa.String(length=20), nullable=False),
            sa.Column('value', sa.Integer(), nullable=False),
            sa.Column('starts_at', sa.DateTime(), nullable=True),
            sa.Column('ends_at', sa.DateTime(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
        )
        op.create_index('ix_shop_discounts_product_id', 'shop_discounts', ['product_id'], unique=False)

    # shop_transactions
    if not _has_table(insp, 'shop_transactions'):
        op.create_table(
            'shop_transactions',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('product_id', sa.String(length=100), nullable=False),
            sa.Column('kind', sa.String(length=20), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('unit_price', sa.Integer(), nullable=False),
            sa.Column('amount', sa.Integer(), nullable=False),
            sa.Column('payment_method', sa.String(length=50), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='success'),
            sa.Column('receipt_code', sa.String(length=64), nullable=True),
            sa.Column('failure_reason', sa.String(length=500), nullable=True),
            sa.Column('extra', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        )
        op.create_index('ix_shop_transactions_product_id', 'shop_transactions', ['product_id'], unique=False)
        op.create_index('ix_shop_transactions_receipt_code', 'shop_transactions', ['receipt_code'], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Drop in reverse dependency order
    if _has_table(insp, 'shop_transactions'):
        try:
            op.drop_index('ix_shop_transactions_receipt_code', table_name='shop_transactions')
        except Exception:
            pass
        try:
            op.drop_index('ix_shop_transactions_product_id', table_name='shop_transactions')
        except Exception:
            pass
        op.drop_table('shop_transactions')

    if _has_table(insp, 'shop_discounts'):
        try:
            op.drop_index('ix_shop_discounts_product_id', table_name='shop_discounts')
        except Exception:
            pass
        op.drop_table('shop_discounts')

    if _has_table(insp, 'shop_products'):
        try:
            op.drop_index('ix_shop_products_product_id', table_name='shop_products')
        except Exception:
            pass
        op.drop_table('shop_products')
