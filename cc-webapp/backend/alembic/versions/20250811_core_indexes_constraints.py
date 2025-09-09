"""add core indexes and unique constraints for game/activity tables

Revision ID: 20250811_core_ix
Revises: 20250810_align_users
Create Date: 2025-08-11

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250811_core_ix'
down_revision: Union[str, None] = '20250810_align_users'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create helpful indexes/constraints if the target tables/columns exist.

    This migration is schema-aware and will safely no-op for missing tables/columns
    to accommodate environments created from different bootstrap scripts.
    """
    bind = op.get_bind()
    insp = sa.inspect(bind)

    def has_table(table: str) -> bool:
        return table in insp.get_table_names()

    def has_columns(table: str, cols: list[str]) -> bool:
        try:
            existing = {c['name'] for c in insp.get_columns(table)}
            return all(c in existing for c in cols)
        except Exception:
            return False

    def index_exists(table: str, name: str) -> bool:
        try:
            return any(ix.get('name') == name for ix in insp.get_indexes(table))
        except Exception:
            return False

    def create_index_if(table: str, cols: list[str], name: str) -> None:
        if has_table(table) and has_columns(table, cols) and not index_exists(table, name):
            op.create_index(name, table, cols, unique=False)

    # user_actions: support created_at or timestamp column variants
    if has_table('user_actions') and has_columns('user_actions', ['user_id']):
        if has_columns('user_actions', ['created_at']):
            create_index_if('user_actions', ['user_id', 'created_at'], 'ix_user_actions_user_created')
        elif has_columns('user_actions', ['timestamp']):
            create_index_if('user_actions', ['user_id', 'timestamp'], 'ix_user_actions_user_created')

    # user activity: singular or plural, created_at or activity_date
    if has_table('user_activities'):
        if has_columns('user_activities', ['user_id', 'activity_date']):
            create_index_if('user_activities', ['user_id', 'activity_date'], 'ix_user_activities_user_date')
    elif has_table('user_activity'):
        if has_columns('user_activity', ['user_id', 'created_at']):
            create_index_if('user_activity', ['user_id', 'created_at'], 'ix_user_activity_user_created')

    # user_rewards: claimed_at index
    if has_table('user_rewards') and has_columns('user_rewards', ['user_id', 'claimed_at']):
        create_index_if('user_rewards', ['user_id', 'claimed_at'], 'ix_user_rewards_user_claimed')

    # gacha_results: created_at index if table exists
    if has_table('gacha_results') and has_columns('gacha_results', ['user_id', 'created_at']):
        create_index_if('gacha_results', ['user_id', 'created_at'], 'ix_gacha_results_user_created')

    # user_progress: progress_type index
    if has_table('user_progress') and has_columns('user_progress', ['user_id', 'progress_type']):
        create_index_if('user_progress', ['user_id', 'progress_type'], 'ix_user_progress_user_type')

    # game sessions: support legacy (session_type) and detail (game_type)
    if has_table('game_sessions') and has_columns('game_sessions', ['user_id', 'session_type']):
        create_index_if('game_sessions', ['user_id', 'session_type'], 'ix_game_sessions_user_type')
    elif has_table('game_sessions_detail') and has_columns('game_sessions_detail', ['user_id', 'game_type']):
        create_index_if('game_sessions_detail', ['user_id', 'game_type'], 'ix_game_sessions_detail_user_type')

    # Unique constraints for per-user game stats (supports user_game_stats or game_stats)
    def unique_exists(table: str, name: str) -> bool:
        try:
            return any(uq.get('name') == name for uq in insp.get_unique_constraints(table))
        except Exception:
            return False

    if has_table('user_game_stats') and has_columns('user_game_stats', ['user_id', 'game_type']):
        if not unique_exists('user_game_stats', 'uq_user_game_stats_user_game'):
            op.create_unique_constraint('uq_user_game_stats_user_game', 'user_game_stats', ['user_id', 'game_type'])
    elif has_table('game_stats') and has_columns('game_stats', ['user_id', 'game_type']):
        if not unique_exists('game_stats', 'uq_game_stats_user_game'):
            op.create_unique_constraint('uq_game_stats_user_game', 'game_stats', ['user_id', 'game_type'])

    # Note: daily_game_limits shape varies across setups; skip adding a new unique here to avoid conflicts.


def downgrade() -> None:
    """Drop created indexes/constraints if they exist."""
    bind = op.get_bind()
    insp = sa.inspect(bind)

    def has_table(table: str) -> bool:
        return table in insp.get_table_names()

    def has_index(table: str, name: str) -> bool:
        try:
            return any(ix.get('name') == name for ix in insp.get_indexes(table))
        except Exception:
            return False

    def has_unique(table: str, name: str) -> bool:
        try:
            return any(uq.get('name') == name for uq in insp.get_unique_constraints(table))
        except Exception:
            return False

    # Unique constraints
    if has_table('user_game_stats') and has_unique('user_game_stats', 'uq_user_game_stats_user_game'):
        with op.batch_alter_table('user_game_stats'):
            op.drop_constraint('uq_user_game_stats_user_game', type_='unique')
    if has_table('game_stats') and has_unique('game_stats', 'uq_game_stats_user_game'):
        with op.batch_alter_table('game_stats'):
            op.drop_constraint('uq_game_stats_user_game', type_='unique')

    # Indexes
    if has_table('game_sessions') and has_index('game_sessions', 'ix_game_sessions_user_type'):
        op.drop_index('ix_game_sessions_user_type', table_name='game_sessions')
    if has_table('game_sessions_detail') and has_index('game_sessions_detail', 'ix_game_sessions_detail_user_type'):
        op.drop_index('ix_game_sessions_detail_user_type', table_name='game_sessions_detail')
    if has_table('user_progress') and has_index('user_progress', 'ix_user_progress_user_type'):
        op.drop_index('ix_user_progress_user_type', table_name='user_progress')
    if has_table('gacha_results') and has_index('gacha_results', 'ix_gacha_results_user_created'):
        op.drop_index('ix_gacha_results_user_created', table_name='gacha_results')
    if has_table('user_rewards') and has_index('user_rewards', 'ix_user_rewards_user_claimed'):
        op.drop_index('ix_user_rewards_user_claimed', table_name='user_rewards')
    if has_table('user_activities') and has_index('user_activities', 'ix_user_activities_user_date'):
        op.drop_index('ix_user_activities_user_date', table_name='user_activities')
    if has_table('user_activity') and has_index('user_activity', 'ix_user_activity_user_created'):
        op.drop_index('ix_user_activity_user_created', table_name='user_activity')
    if has_table('user_actions') and has_index('user_actions', 'ix_user_actions_user_created'):
        op.drop_index('ix_user_actions_user_created', table_name='user_actions')
