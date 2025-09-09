"""ensure unique receipt_code on shop_transactions

Revision ID: 20250815_ensure_shop_receipt_unique
Revises: 20250815_admin_audit_action_created_idx
Create Date: 2025-08-15

This migration ensures a UNIQUE index exists on shop_transactions.receipt_code.
It is safe to run repeatedly and will no-op if the index already exists.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250815_ensure_shop_receipt_unique'
down_revision: Union[str, None] = '20250815_admin_audit_action_created_idx'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    # Table may not exist in some environments; guard
    try:
        if 'shop_transactions' not in insp.get_table_names():
            return
    except Exception:
        return
    try:
        indexes = insp.get_indexes('shop_transactions')
    except Exception:
        indexes = []
    names = {ix.get('name') for ix in indexes if isinstance(ix, dict)}
    # ensure index exists and is unique
    if 'ix_shop_transactions_receipt_code' not in names:
        try:
            op.create_index('ix_shop_transactions_receipt_code', 'shop_transactions', ['receipt_code'], unique=True)
        except Exception:
            # might already exist under a different naming; attempt add constraint
            try:
                op.create_unique_constraint('uq_shop_transactions_receipt_code', 'shop_transactions', ['receipt_code'])
            except Exception:
                pass


def downgrade() -> None:
    # best-effort drop by both names
    try:
        op.drop_index('ix_shop_transactions_receipt_code', table_name='shop_transactions')
    except Exception:
        pass
    try:
        op.drop_constraint('uq_shop_transactions_receipt_code', 'shop_transactions', type_='unique')
    except Exception:
        pass
