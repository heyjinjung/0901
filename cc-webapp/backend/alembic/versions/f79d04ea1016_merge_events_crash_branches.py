"""merge events & crash branches

Revision ID: f79d04ea1016
Revises: 20250808b_harden_crash, events_missions_001
Create Date: 2025-08-08 09:52:25.526616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f79d04ea1016'
down_revision: Union[str, None] = ('20250808b_harden_crash', 'events_missions_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
