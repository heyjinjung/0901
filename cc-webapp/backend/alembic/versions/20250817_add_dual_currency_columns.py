"""Add dual currency columns to users table

Revision ID: 20250817_add_dual_currency_columns
Revises: 20250816_add_ab_test_participants
Create Date: 2025-08-17

Adds regular_coin_balance and premium_gem_balance columns with default 0.
Keeps existing cyber_token_balance for backward compatibility (to be deprecated).
"""
from __future__ import annotations
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '20250817_add_dual_currency_columns'
down_revision: Union[str, None] = '20250816_add_ab_test_participants'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp, table: str, col: str) -> bool:
    try:
        return any(c['name'] == col for c in insp.get_columns(table))
    except Exception:
        return False

"""Add dual currency columns to users table

Revision ID: 20250817_add_dual_currency_columns
Revises: 20250816_add_ab_test_participants
Create Date: 2025-08-17

Adds regular_coin_balance and premium_gem_balance columns with default 0.
Keeps existing cyber_token_balance for backward compatibility (to be deprecated).
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '20250817_add_dual_currency_columns'
down_revision: Union[str, None] = '20250816_add_ab_test_participants'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp, table: str, col: str) -> bool:
    try:
        return any(c['name'] == col for c in insp.get_columns(table))
    except Exception:
        return False


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    table = 'users'

    # If users table exists, add balances idempotently
    if _has_column(insp, table, 'id'):
        if not _has_column(insp, table, 'regular_coin_balance'):
            op.add_column(table, sa.Column('regular_coin_balance', sa.Integer(), nullable=False, server_default='0'))
        if not _has_column(insp, table, 'premium_gem_balance'):
            op.add_column(table, sa.Column('premium_gem_balance', sa.Integer(), nullable=False, server_default='0'))

    # Drop server defaults to match ORM defaults after backfill
    try:
        if _has_column(insp, table, 'regular_coin_balance'):
            op.execute("ALTER TABLE users ALTER COLUMN regular_coin_balance DROP DEFAULT")
    except Exception:
        pass

    try:
        if _has_column(insp, table, 'premium_gem_balance'):
            op.execute("ALTER TABLE users ALTER COLUMN premium_gem_balance DROP DEFAULT")
    except Exception:
        pass


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    table = 'users'
    try:
        if _has_column(insp, table, 'regular_coin_balance'):
            op.drop_column(table, 'regular_coin_balance')
    except Exception:
        pass
    try:
        if _has_column(insp, table, 'premium_gem_balance'):
            op.drop_column(table, 'premium_gem_balance')
    except Exception:
        pass

