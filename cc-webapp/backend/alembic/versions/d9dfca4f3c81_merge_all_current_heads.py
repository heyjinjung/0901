"""merge all current heads

Revision ID: d9dfca4f3c81
Revises: 20250817_fix_game_sessions_id_type, 9a08c34dc612
Create Date: 2025-08-17 07:16:38.670313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9dfca4f3c81'
down_revision: Union[str, None] = ('20250817_fix_game_sessions_id_type', '9a08c34dc612')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
