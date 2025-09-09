"""merge game_history_indexes + game_sessions

Revision ID: 2a962f1d3366
Revises: 20250816_add_game_history_indexes, 20250816_add_game_sessions_table
Create Date: 2025-08-16 13:54:03.530466

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a962f1d3366'
down_revision: Union[str, None] = ('20250816_add_game_history_indexes', '20250816_add_game_sessions_table')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
