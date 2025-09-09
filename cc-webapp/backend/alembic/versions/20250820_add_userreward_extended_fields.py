"""add extended fields to user_rewards (reward_type, gold/xp, metadata, idempotency_key)

Revision ID: 20250820_add_userreward_extended_fields
Revises: e93ff77e600b
Create Date: 2025-08-20 03:20:00
"""
from __future__ import annotations
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.exc import NoSuchTableError

revision: str = '20250820_add_userreward_extended_fields'
down_revision: Union[str, None] = 'e93ff77e600b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE = 'user_rewards'

def upgrade() -> None:
    conn = op.get_bind()
    # Prefer sa.inspect for SQLAlchemy 1.4/2.0 compatibility
    try:
        insp = sa.inspect(conn)  # type: ignore
    except Exception:
        insp = Inspector.from_engine(conn)  # type: ignore

    # Skip if base table doesn't exist yet (defensive for older branches)
    try:
        if not insp.has_table(TABLE):
            return
    except Exception:
        # If inspector can't determine, fall back to safe return
        return

    try:
        cols = {c['name'] for c in insp.get_columns(TABLE)}
    except NoSuchTableError:
        # Table truly doesn't exist; skip migration
        return
    # Add columns if missing
    if 'reward_type' not in cols:
        op.add_column(TABLE, sa.Column('reward_type', sa.String(length=50), nullable=True))
    if 'gold_amount' not in cols:
        op.add_column(TABLE, sa.Column('gold_amount', sa.Integer(), nullable=True))
    if 'xp_amount' not in cols:
        op.add_column(TABLE, sa.Column('xp_amount', sa.Integer(), nullable=True))
    if 'reward_metadata' not in cols:
        op.add_column(TABLE, sa.Column('reward_metadata', sa.JSON(), nullable=True))
    if 'idempotency_key' not in cols:
        op.add_column(TABLE, sa.Column('idempotency_key', sa.String(length=120), nullable=True))

    # Indexes / constraints
    try:
        indexes = {i['name'] for i in insp.get_indexes(TABLE)}
    except NoSuchTableError:
        # Table vanished or not present; nothing to index
        return
    if 'ix_user_rewards_reward_type' not in indexes and 'reward_type' in (cols | {'reward_type'}):
        op.create_index('ix_user_rewards_reward_type', TABLE, ['reward_type'])
    if 'ix_user_rewards_idempotency_key' not in indexes and 'idempotency_key' in (cols | {'idempotency_key'}):
        op.create_index('ix_user_rewards_idempotency_key', TABLE, ['idempotency_key'], unique=True)


def downgrade() -> None:
    # Conservative: drop added index/columns (idempotency uniqueness first)
    try:
        op.drop_index('ix_user_rewards_idempotency_key', table_name=TABLE)
    except Exception:
        pass
    try:
        op.drop_index('ix_user_rewards_reward_type', table_name=TABLE)
    except Exception:
        pass
    for col in ['idempotency_key', 'reward_metadata', 'xp_amount', 'gold_amount', 'reward_type']:
        try:
            op.drop_column(TABLE, col)
        except Exception:
            pass
