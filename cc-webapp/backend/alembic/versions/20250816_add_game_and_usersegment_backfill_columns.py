"""add game bet/payout and usersegment name columns

Revision ID: 20250816_add_game_and_usersegment_cols
Revises: 20250816_add_game_session_result_data
Create Date: 2025-08-16

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250816_add_game_and_usersegment_cols'
down_revision = '20250816_add_game_session_result_data'
branch_labels = None
depends_on = None

def column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    # guard against missing table: check table list first
    try:
        tables = inspector.get_table_names()
    except Exception:
        return False
    if table not in tables:
        return False
    # safe to get columns now
    cols = [c['name'] for c in inspector.get_columns(table)]
    return column in cols

def upgrade():
    bind = op.get_bind()

    def table_exists(table_name: str) -> bool:
        # Use Postgres to_regclass to reliably determine table existence
        try:
            res = bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table_name}).scalar()
            return res is not None
        except Exception:
            return False

    # games.bet_amount
    if table_exists('games') and not column_exists('games', 'bet_amount'):
        try:
            op.add_column('games', sa.Column('bet_amount', sa.Integer(), server_default='0', nullable=False))
        except Exception:
            # If table disappeared between checks, skip safely
            pass
    # games.payout
    if table_exists('games') and not column_exists('games', 'payout'):
        try:
            op.add_column('games', sa.Column('payout', sa.Integer(), server_default='0', nullable=False))
        except Exception:
            pass
    # user_segments.name
    if table_exists('user_segments') and not column_exists('user_segments', 'name'):
        try:
            op.add_column('user_segments', sa.Column('name', sa.String(length=50), nullable=True))
        except Exception:
            pass


def downgrade():
    # 안전을 위해 존재할 때만 제거
    if column_exists('games', 'bet_amount'):
        op.drop_column('games', 'bet_amount')
    if column_exists('games', 'payout'):
        op.drop_column('games', 'payout')
    if column_exists('user_segments', 'name'):
        op.drop_column('user_segments', 'name')
