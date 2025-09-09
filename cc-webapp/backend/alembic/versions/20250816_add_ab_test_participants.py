"""create ab_test_participants table

Revision ID: 20250816_add_ab_test_participants
Revises: 20250816_add_tx_integrity_and_refund_fields
Create Date: 2025-08-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250816_add_ab_test_participants'
down_revision = '20250816_add_tx_integrity_and_refund_fields'
branch_labels = None
depends_on = None

def upgrade():
    if not op.get_bind().dialect.has_table(op.get_bind(), 'ab_test_participants'):  # type: ignore
        op.create_table(
            'ab_test_participants',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False, index=True),
            sa.Column('test_name', sa.String(100), nullable=False, index=True),
            sa.Column('variant', sa.String(50), nullable=False),
            sa.Column('assigned_at', sa.DateTime(timezone=False), server_default=sa.text('CURRENT_TIMESTAMP')),
            sa.Column('converted_at', sa.DateTime(timezone=False), nullable=True),
            sa.Column('conversion_value', sa.Float, nullable=True),
        )
        op.create_index('ix_abtest_user_test', 'ab_test_participants', ['user_id', 'test_name'], unique=True)
        op.create_index('ix_abtest_test_variant', 'ab_test_participants', ['test_name', 'variant'], unique=False)


def downgrade():
    conn = op.get_bind()
    if conn.dialect.has_table(conn, 'ab_test_participants'):  # type: ignore
        op.drop_index('ix_abtest_user_test', table_name='ab_test_participants')
        op.drop_index('ix_abtest_test_variant', table_name='ab_test_participants')
        op.drop_table('ab_test_participants')
