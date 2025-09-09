"""add composite index for game_history (user_id, game_type, created_at)

Revision ID: 20250816_add_game_history_indexes
Revises: 20250816_merge_game_history_receipt_heads
Create Date: 2025-08-16

최소 필요 인덱스: ix_game_history_user_game_created
쿼리 패턴 커버:
- /api/games/history?game_type=...
- /api/games/{game_type}/stats
- /api/games/profile/stats (left-prefix user_id + created_at 활용)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250816_add_game_history_indexes'
down_revision: Union[str, None] = '20250816_merge_game_history_receipt_heads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

INDEX_NAME = 'ix_game_history_user_game_created'
TABLE_NAME = 'game_history'
COLUMNS = ['user_id', 'game_type', 'created_at']


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    if TABLE_NAME not in insp.get_table_names():
        return

    existing_cols = {c['name'] for c in insp.get_columns(TABLE_NAME)}
    if not all(c in existing_cols for c in COLUMNS):
        return

    existing_indexes = {ix['name'] for ix in insp.get_indexes(TABLE_NAME)}
    if INDEX_NAME not in existing_indexes:
        op.create_index(INDEX_NAME, TABLE_NAME, COLUMNS, unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if TABLE_NAME in insp.get_table_names():
        existing_indexes = {ix['name'] for ix in insp.get_indexes(TABLE_NAME)}
        if INDEX_NAME in existing_indexes:
            op.drop_index(INDEX_NAME, table_name=TABLE_NAME)
