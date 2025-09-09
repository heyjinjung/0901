"""add user_actions.action_data column if missing

Revision ID: d1993e6fdab5
Revises: 07b4d754c43b
Create Date: 2025-08-16 16:22:46.024380

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1993e6fdab5'
down_revision: Union[str, None] = '07b4d754c43b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add action_data column to user_actions if it does not exist (idempotent)."""
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        if 'user_actions' in insp.get_table_names():
            cols = {c['name'] for c in insp.get_columns('user_actions')}
            if 'action_data' not in cols:
                op.add_column('user_actions', sa.Column('action_data', sa.Text()))
    except Exception:
        # Non-fatal in test/dev environments
        pass


def downgrade() -> None:
    """Drop action_data column if present (best-effort)."""
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        if 'user_actions' in insp.get_table_names():
            cols = {c['name'] for c in insp.get_columns('user_actions')}
            if 'action_data' in cols:
                with op.batch_alter_table('user_actions') as batch_op:
                    batch_op.drop_column('action_data')
    except Exception:
        pass
