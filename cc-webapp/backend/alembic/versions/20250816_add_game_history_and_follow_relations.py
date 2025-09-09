"""add game_history and follow_relations tables

Revision ID: 20250816_add_game_history_and_follow_relations
Revises: 20250816_add_ab_test_participants
Create Date: 2025-08-16
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250816_add_game_history_and_follow_relations'
down_revision = '20250816_add_ab_test_participants'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect

    # game_history
    if not dialect.has_table(bind, 'game_history'):  # type: ignore
        # create session_id as plain Integer if game_sessions table is not yet present
        if dialect.has_table(bind, 'game_sessions'):
            session_col = sa.Column('session_id', sa.Integer, sa.ForeignKey('game_sessions.id'), nullable=True)
        else:
            session_col = sa.Column('session_id', sa.Integer, nullable=True)

        op.create_table(
            'game_history',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
            sa.Column('game_type', sa.String(50), nullable=False),
            session_col,
            sa.Column('action_type', sa.String(30), nullable=False),
            sa.Column('delta_coin', sa.Integer, nullable=False, server_default='0'),
            sa.Column('delta_gem', sa.Integer, nullable=False, server_default='0'),
            sa.Column('result_meta', sa.JSON, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        )
        op.create_index('ix_game_history_user_created', 'game_history', ['user_id', 'created_at'])
        op.create_index('ix_game_history_game_created', 'game_history', ['game_type', 'created_at'])
        op.create_index('ix_game_history_session', 'game_history', ['session_id'])
        op.create_index('ix_game_history_action_created', 'game_history', ['action_type', 'created_at'])

    # follow_relations
    if not dialect.has_table(bind, 'follow_relations'):  # type: ignore
        op.create_table(
            'follow_relations',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
            sa.Column('target_user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
            sa.UniqueConstraint('user_id', 'target_user_id', name='uq_follow_user_target'),
        )
        op.create_index('ix_follow_target_user', 'follow_relations', ['target_user_id'])
        op.create_index('ix_follow_user', 'follow_relations', ['user_id'])


def downgrade():
    bind = op.get_bind()
    dialect = bind.dialect

    if dialect.has_table(bind, 'game_history'):  # type: ignore
        op.drop_index('ix_game_history_user_created', table_name='game_history')
        op.drop_index('ix_game_history_game_created', table_name='game_history')
        op.drop_index('ix_game_history_session', table_name='game_history')
        op.drop_index('ix_game_history_action_created', table_name='game_history')
        op.drop_table('game_history')

    if dialect.has_table(bind, 'follow_relations'):  # type: ignore
        op.drop_index('ix_follow_target_user', table_name='follow_relations')
        op.drop_index('ix_follow_user', table_name='follow_relations')
        op.drop_table('follow_relations')
