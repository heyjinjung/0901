"""add promo usage and admin audit logs tables

Revision ID: 20250815_add_promo_usage_and_admin_audit
Revises: 20250813_add_limited_packages_and_promos
Create Date: 2025-08-15

Idempotent migration creating:
- shop_promo_usage
- admin_audit_logs

Chained after limited packages and promos to keep a single head.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250815_add_promo_usage_and_admin_audit'
down_revision: Union[str, None] = '20250813_add_limited_packages_and_promos'
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

    # shop_promo_usage
    if not _has_table(insp, 'shop_promo_usage'):
        op.create_table(
            'shop_promo_usage',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('promo_code', sa.String(length=64), nullable=False),
            sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('package_code', sa.String(length=100), nullable=True),
            sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('used_at', sa.DateTime(), nullable=True),
            sa.Column('details', sa.JSON(), nullable=True),
        )
        op.create_index('ix_shop_promo_usage_code', 'shop_promo_usage', ['promo_code'], unique=False)
        op.create_index('ix_shop_promo_usage_package_code', 'shop_promo_usage', ['package_code'], unique=False)

    # admin_audit_logs
    if not _has_table(insp, 'admin_audit_logs'):
        op.create_table(
            'admin_audit_logs',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('actor_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
            sa.Column('action', sa.String(length=100), nullable=False),
            sa.Column('target_type', sa.String(length=100), nullable=True),
            sa.Column('target_id', sa.String(length=200), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('details', sa.JSON(), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Drop indexes then tables to be safe
    if _has_table(insp, 'shop_promo_usage'):
        try:
            if _has_index(insp, 'shop_promo_usage', 'ix_shop_promo_usage_package_code'):
                op.drop_index('ix_shop_promo_usage_package_code', table_name='shop_promo_usage')
        except Exception:
            pass
        try:
            if _has_index(insp, 'shop_promo_usage', 'ix_shop_promo_usage_code'):
                op.drop_index('ix_shop_promo_usage_code', table_name='shop_promo_usage')
        except Exception:
            pass
        op.drop_table('shop_promo_usage')

    if _has_table(insp, 'admin_audit_logs'):
        op.drop_table('admin_audit_logs')
