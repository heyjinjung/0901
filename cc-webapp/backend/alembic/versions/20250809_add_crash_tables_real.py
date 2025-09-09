"""add crash tables real (no-op)

Revision ID: 20250809_add_crash_real
Revises: f79d04ea1016
Create Date: 2025-08-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250809_add_crash_real'
down_revision: Union[str, None] = 'f79d04ea1016'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op upgrade to keep a single head while the real crash tables are postponed."""
    pass


def downgrade() -> None:
    """No-op downgrade."""
    pass
