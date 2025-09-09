"""add index on user_actions(action_type, created_at)

Revision ID: 20250813_user_actions_ix_type_created
Revises: 20250811_add_invite_codes
Create Date: 2025-08-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250813_user_actions_ix_type_created'
# Chain after the current single head merge revision to keep a single head
down_revision: Union[str, None] = 'f79d04ea1016'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create composite index on user_actions for (action_type, created_at|timestamp)."""
    bind = op.get_bind()
    insp = sa.inspect(bind)

    def has_table(table: str) -> bool:
        try:
            return table in insp.get_table_names()
        except Exception:
            return False

    def cols(table: str) -> set[str]:
        try:
            return {c['name'] for c in insp.get_columns(table)}
        except Exception:
            return set()

    def index_exists(table: str, name: str) -> bool:
        try:
            return any(ix.get('name') == name for ix in insp.get_indexes(table))
        except Exception:
            return False

    if not has_table('user_actions'):
        return

    c = cols('user_actions')
    if 'action_type' not in c:
        return

    # Prefer created_at; fall back to legacy timestamp
    if 'created_at' in c and not index_exists('user_actions', 'ix_user_actions_type_created'):
        op.create_index('ix_user_actions_type_created', 'user_actions', ['action_type', 'created_at'], unique=False)
    elif 'timestamp' in c and not index_exists('user_actions', 'ix_user_actions_type_created'):
        op.create_index('ix_user_actions_type_created', 'user_actions', ['action_type', 'timestamp'], unique=False)


def downgrade() -> None:
    """Drop composite index if present."""
    bind = op.get_bind()
    insp = sa.inspect(bind)

    def has_table(table: str) -> bool:
        try:
            return table in insp.get_table_names()
        except Exception:
            return False

    def has_index(table: str, name: str) -> bool:
        try:
            return any(ix.get('name') == name for ix in insp.get_indexes(table))
        except Exception:
            return False

    if has_table('user_actions') and has_index('user_actions', 'ix_user_actions_type_created'):
        op.drop_index('ix_user_actions_type_created', table_name='user_actions')
