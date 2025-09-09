"""add idempotency_key to shop_transactions

Revision ID: 20250817_add_idempotency_key_to_shop_transactions
Revises: 20250817_add_dual_currency_columns
Create Date: 2025-08-17
"""
from __future__ import annotations
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '20250817_add_idempotency_key_to_shop_transactions'
down_revision: Union[str, None] = '20250817_add_dual_currency_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def _has_column(insp, table: str, col: str) -> bool:
    try:
        return any(c['name'] == col for c in insp.get_columns(table))
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
    table = 'shop_transactions'
    if _has_column(insp, table, 'id'):
        if not _has_column(insp, table, 'idempotency_key'):
            op.add_column(table, sa.Column('idempotency_key', sa.String(length=80), nullable=True))
        if not _has_index(insp, table, 'ix_shop_transactions_idempotency_key'):
            op.create_index('ix_shop_transactions_idempotency_key', table, ['idempotency_key'], unique=True)

def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    table = 'shop_transactions'
    try:
        if _has_index(insp, table, 'ix_shop_transactions_idempotency_key'):
            op.drop_index('ix_shop_transactions_idempotency_key', table_name=table)
    except Exception:
        pass
    try:
        if _has_column(insp, table, 'idempotency_key'):
            op.drop_column(table, 'idempotency_key')
    except Exception:
        pass
