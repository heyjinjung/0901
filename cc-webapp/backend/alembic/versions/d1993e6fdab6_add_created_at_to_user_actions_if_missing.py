"""add created_at to user_actions if missing

Revision ID: d1993e6fdab6
Revises: d1993e6fdab5
Create Date: 2025-08-16 16:23:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1993e6fdab6'
down_revision: Union[str, None] = 'd1993e6fdab5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""Add created_at column to user_actions if it does not exist."""
	bind = op.get_bind()
	insp = sa.inspect(bind)
	try:
		if 'user_actions' in insp.get_table_names():
			cols = {c['name'] for c in insp.get_columns('user_actions')}
			if 'created_at' not in cols:
				op.add_column('user_actions', sa.Column('created_at', sa.DateTime()))
	except Exception:
		pass


def downgrade() -> None:
	"""Drop created_at column if present (best-effort)."""
	bind = op.get_bind()
	insp = sa.inspect(bind)
	try:
		if 'user_actions' in insp.get_table_names():
			cols = {c['name'] for c in insp.get_columns('user_actions')}
			if 'created_at' in cols:
				with op.batch_alter_table('user_actions') as batch_op:
					batch_op.drop_column('created_at')
	except Exception:
		pass

