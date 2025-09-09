"""fix game_sessions id type if created as varchar

Revision ID: 20250817_fix_game_sessions_id_type
Revises: 20250817_merge_heads_unify
Create Date: 2025-08-17
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250817_fix_game_sessions_id_type'
down_revision = '20250817_merge_heads_unify'
branch_labels = None
depends_on = None


def _col_type(bind, table_name, column_name):
    insp = sa.inspect(bind)
    cols = {c['name']: c for c in insp.get_columns(table_name)}
    return cols.get(column_name, {}).get('type') if table_name in insp.get_table_names() else None


def upgrade():
    bind = op.get_bind()
    dialect = bind.dialect
    insp = sa.inspect(bind)

    if 'game_sessions' not in insp.get_table_names():
        # nothing to do
        return

    # detect current id column type
    cols = {c['name']: c for c in insp.get_columns('game_sessions')}
    id_col = cols.get('id')
    if not id_col:
        return

    # If id already integer, nothing to do
    id_type = id_col.get('type')
    # SQLAlchemy types compare by class name; look for 'VARCHAR' or 'CHARACTER VARYING' in repr
    id_type_str = repr(id_type).lower() if id_type is not None else ''
    if 'integer' in id_type_str or 'int' in id_type_str:
        return

    # If table is non-empty, abort (avoid destructive change)
    row_count = bind.execute(sa.text("SELECT count(*) FROM game_sessions")).scalar()
    if row_count and int(row_count) > 0:
        raise RuntimeError('game_sessions has rows; manual migration needed to change id type')

    # Safe to drop and recreate with correct schema
    op.drop_table('game_sessions')

    op.create_table(
        'game_sessions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('game_type', sa.String(50), nullable=False),
        sa.Column('bet_amount', sa.Integer, nullable=False, server_default='0'),
        sa.Column('win_amount', sa.Integer, nullable=False, server_default='0'),
        sa.Column('start_time', sa.DateTime(timezone=False), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=False), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('result_data', sa.JSON, nullable=True),
    )


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if 'game_sessions' in insp.get_table_names():
        op.drop_table('game_sessions')
