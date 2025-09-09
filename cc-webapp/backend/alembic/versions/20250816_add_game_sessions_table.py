"""add game_sessions table

Revision ID: 20250816_add_game_sessions_table
Revises: 20250816_add_game_history_and_follow_relations
Create Date: 2025-08-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250816_add_game_sessions_table'
down_revision = '20250816_add_game_history_and_follow_relations'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect

    # 이미 존재하면 skip (idempotent)
    if not dialect.has_table(bind, 'game_sessions'):  # type: ignore
        op.create_table(
            'game_sessions',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('external_session_id', sa.String(36), nullable=False, unique=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
            sa.Column('game_type', sa.String(50), nullable=False),
            sa.Column('initial_bet', sa.Integer, nullable=False, server_default='0'),
            sa.Column('total_win', sa.Integer, nullable=False, server_default='0'),
            sa.Column('total_bet', sa.Integer, nullable=False, server_default='0'),
            sa.Column('total_rounds', sa.Integer, nullable=False, server_default='0'),
            sa.Column('start_time', sa.DateTime(timezone=False), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
            sa.Column('end_time', sa.DateTime(timezone=False), nullable=True),
            sa.Column('status', sa.String(20), nullable=False, server_default='active'),
            sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        )
        op.create_index('ix_game_sessions_user_status', 'game_sessions', ['user_id', 'status'])
        op.create_index('ix_game_sessions_user_game', 'game_sessions', ['user_id', 'game_type'])
        op.create_index('ix_game_sessions_start_time', 'game_sessions', ['start_time'])
        op.create_index('ix_game_sessions_created_at', 'game_sessions', ['created_at'])


def downgrade():
    bind = op.get_bind()
    dialect = bind.dialect
    if dialect.has_table(bind, 'game_sessions'):  # type: ignore
        op.drop_index('ix_game_sessions_user_status', table_name='game_sessions')
        op.drop_index('ix_game_sessions_user_game', table_name='game_sessions')
        op.drop_index('ix_game_sessions_start_time', table_name='game_sessions')
        op.drop_index('ix_game_sessions_created_at', table_name='game_sessions')
        op.drop_table('game_sessions')
