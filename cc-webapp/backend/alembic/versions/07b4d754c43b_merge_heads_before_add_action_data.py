"""merge heads before add action_data

Revision ID: 07b4d754c43b
Revises: 20250816_add_game_and_usersegment_cols, 20250816_add_user_id_result_to_games, 20250816_merge_game_session_result_data_heads
Create Date: 2025-08-16 16:19:04.890453

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '07b4d754c43b'
down_revision: Union[str, None] = ('20250816_add_game_and_usersegment_cols', '20250816_add_user_id_result_to_games', '20250816_merge_game_session_result_data_heads')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
