"""add receipt_signature to shop_transactions

Revision ID: 20250816_add_receipt_signature
Revises: f79d04ea1016
Create Date: 2025-08-16
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250816_add_receipt_signature'
down_revision = 'f79d04ea1016'
branch_labels = None
depends_on = None

def column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = [c['name'] for c in insp.get_columns(table)]
    return column in cols

def upgrade():
    if column_exists('shop_transactions', 'receipt_signature'):
        return
    with op.batch_alter_table('shop_transactions') as batch:
        batch.add_column(sa.Column('receipt_signature', sa.String(length=128), nullable=True))
        batch.create_index('ix_shop_transactions_receipt_signature', ['receipt_signature'])


def downgrade():
    # 안전 롤백 (존재할 때만 삭제)
    bind = op.get_bind()
    insp = sa.inspect(bind)
    cols = [c['name'] for c in insp.get_columns('shop_transactions')]
    if 'receipt_signature' in cols:
        with op.batch_alter_table('shop_transactions') as batch:
            batch.drop_index('ix_shop_transactions_receipt_signature')
            batch.drop_column('receipt_signature')
