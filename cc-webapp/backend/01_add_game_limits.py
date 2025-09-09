"""Add user_game_limits table

Revision ID: 01_add_game_limits
Create Date: 2025-08-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01_add_game_limits'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_game_limits table if it doesn't exist
    op.create_table(
        'user_game_limits',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('game_type', sa.String(), nullable=True),
        sa.Column('daily_max', sa.Integer(), nullable=True),
        sa.Column('daily_used', sa.Integer(), nullable=True),
        sa.Column('last_reset', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_game_limits_game_type'), 'user_game_limits', ['game_type'], unique=False)
    op.create_index(op.f('ix_user_game_limits_id'), 'user_game_limits', ['id'], unique=False)
    op.create_index(op.f('ix_user_game_limits_user_id'), 'user_game_limits', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop user_game_limits table
    op.drop_index(op.f('ix_user_game_limits_user_id'), table_name='user_game_limits')
    op.drop_index(op.f('ix_user_game_limits_id'), table_name='user_game_limits')
    op.drop_index(op.f('ix_user_game_limits_game_type'), table_name='user_game_limits')
    op.drop_table('user_game_limits')
