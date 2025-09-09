"""add receipt_signature column to shop_transactions

Revision ID: 20250820_add_shop_receipt_signature
Revises: 20250815_ensure_shop_receipt_unique
Create Date: 2025-08-20

Adds nullable receipt_signature column (String(128), index) if missing.
Safe to rerun: guards existence.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '20250820_add_shop_receipt_signature'
down_revision: Union[str, None] = '20250815_ensure_shop_receipt_unique'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        if 'shop_transactions' not in insp.get_table_names():
            return
    except Exception:
        return
    cols = {c['name'] for c in insp.get_columns('shop_transactions')}
    if 'receipt_signature' not in cols:
        try:
            op.add_column('shop_transactions', sa.Column('receipt_signature', sa.String(length=128), nullable=True))
        except Exception:
            pass
    # index (non-unique)
    try:
        indexes = {ix.get('name') for ix in insp.get_indexes('shop_transactions') if isinstance(ix, dict)}
    except Exception:
        indexes = set()
    if 'ix_shop_transactions_receipt_signature' not in indexes:
        try:
            op.create_index('ix_shop_transactions_receipt_signature', 'shop_transactions', ['receipt_signature'], unique=False)
        except Exception:
            pass


def downgrade() -> None:
    # best effort drop index and column
    try:
        op.drop_index('ix_shop_transactions_receipt_signature', table_name='shop_transactions')
    except Exception:
        pass
    try:
        op.drop_column('shop_transactions', 'receipt_signature')
    except Exception:
        pass
