"""add_game_stats_fields_to_users

Revision ID: 63d16ce09e51
Revises: dfc50f6893e3
Create Date: 2025-09-07 05:03:18.332760

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63d16ce09e51'
down_revision: Union[str, None] = 'dfc50f6893e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
