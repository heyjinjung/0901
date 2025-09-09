"""add limited packages and promo codes tables

Revision ID: 20250813_add_limited_packages_and_promos
Revises: 20250813_create_shop_tables
Create Date: 2025-08-13

Idempotent migration creating:
- shop_limited_packages
- shop_promo_codes

Keeps a single head by chaining after 20250813_create_shop_tables.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250813_add_limited_packages_and_promos'
down_revision: Union[str, None] = '20250813_create_shop_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(insp, table: str) -> bool:
    try:
        return table in insp.get_table_names()
    except Exception:
        return False


def _has_index(insp, table: str, name: str) -> bool:
    try:
        return any(ix.get('name') == name for ix in insp.get_indexes(table))
    except Exception:
        return False


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # shop_limited_packages
    if not _has_table(insp, 'shop_limited_packages'):
        op.create_table(
            'shop_limited_packages',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('package_id', sa.String(length=100), nullable=False),
            sa.Column('name', sa.String(length=200), nullable=False),
            sa.Column('description', sa.String(length=1000), nullable=True),
            sa.Column('price', sa.Integer(), nullable=False),
            sa.Column('starts_at', sa.DateTime(), nullable=True),
            sa.Column('ends_at', sa.DateTime(), nullable=True),
            sa.Column('stock_total', sa.Integer(), nullable=True),
            sa.Column('stock_remaining', sa.Integer(), nullable=True),
            sa.Column('per_user_limit', sa.Integer(), nullable=True),
            sa.Column('emergency_disabled', sa.Boolean(), nullable=False, server_default=sa.text('false')),
            sa.Column('contents', sa.JSON(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
        )
        # unique and index on package_id
        op.create_index('ix_shop_limited_packages_package_id', 'shop_limited_packages', ['package_id'], unique=True)

    # shop_promo_codes
    if not _has_table(insp, 'shop_promo_codes'):
        op.create_table(
            'shop_promo_codes',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('code', sa.String(length=64), nullable=False),
            sa.Column('package_id', sa.String(length=100), nullable=True),
            sa.Column('discount_type', sa.String(length=20), nullable=False, server_default='flat'),
            sa.Column('value', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('starts_at', sa.DateTime(), nullable=True),
            sa.Column('ends_at', sa.DateTime(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
            sa.Column('max_uses', sa.Integer(), nullable=True),
            sa.Column('used_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
        )
        # unique code, and index package_id
        op.create_index('uq_shop_promo_codes_code', 'shop_promo_codes', ['code'], unique=True)
        op.create_index('ix_shop_promo_codes_package_id', 'shop_promo_codes', ['package_id'], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Drop promo codes first (independent)
    if _has_table(insp, 'shop_promo_codes'):
        try:
            if _has_index(insp, 'shop_promo_codes', 'ix_shop_promo_codes_package_id'):
                op.drop_index('ix_shop_promo_codes_package_id', table_name='shop_promo_codes')
        except Exception:
            pass
        try:
            if _has_index(insp, 'shop_promo_codes', 'uq_shop_promo_codes_code'):
                op.drop_index('uq_shop_promo_codes_code', table_name='shop_promo_codes')
        except Exception:
            pass
        op.drop_table('shop_promo_codes')

    # Then limited packages
    if _has_table(insp, 'shop_limited_packages'):
        try:
            if _has_index(insp, 'shop_limited_packages', 'ix_shop_limited_packages_package_id'):
                op.drop_index('ix_shop_limited_packages_package_id', table_name='shop_limited_packages')
        except Exception:
            pass
        op.drop_table('shop_limited_packages')
