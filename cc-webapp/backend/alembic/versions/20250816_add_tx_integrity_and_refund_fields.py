"""add integrity_hash & original_tx_id to shop_transactions

Revision ID: 20250816_add_tx_integrity_and_refund_fields
Revises: 20250815_add_promo_usage_and_admin_audit
Create Date: 2025-08-16

Adds columns for future refund/VOID workflows and tamper detection hash.
Keeps single head chaining after latest promo/admin audit migration.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '20250816_add_tx_integrity_and_refund_fields'
down_revision: Union[str, None] = '20250815_add_promo_usage_and_admin_audit'
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
        if not _has_column(insp, table, 'integrity_hash'):
            op.add_column(table, sa.Column('integrity_hash', sa.String(length=64), nullable=True))
            if not _has_index(insp, table, 'ix_shop_transactions_integrity_hash'):
                op.create_index('ix_shop_transactions_integrity_hash', table, ['integrity_hash'], unique=False)
        if not _has_column(insp, table, 'original_tx_id'):
            op.add_column(table, sa.Column('original_tx_id', sa.Integer(), nullable=True))
            try:
                op.create_foreign_key('fk_shop_tx_original', source_table=table, referent_table=table,
                                      local_cols=['original_tx_id'], remote_cols=['id'])
            except Exception:
                pass

def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    table = 'shop_transactions'
    try:
        op.drop_constraint('fk_shop_tx_original', table, type_='foreignkey')
    except Exception:
        pass
    if _has_column(insp, table, 'integrity_hash'):
        try:
            if _has_index(insp, table, 'ix_shop_transactions_integrity_hash'):
                op.drop_index('ix_shop_transactions_integrity_hash', table_name=table)
        except Exception:
            pass
        op.drop_column(table, 'integrity_hash')
    if _has_column(insp, table, 'original_tx_id'):
        op.drop_column(table, 'original_tx_id')
