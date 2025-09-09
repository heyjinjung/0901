"""add crash tables (placeholder)

Revision ID: 20250808_add_crash
Revises: 79b9722f373c
Create Date: 2025-08-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250808_add_crash'
down_revision: Union[str, None] = '79b9722f373c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""No-op placeholder upgrade for crash tables seed revision."""
	pass


def downgrade() -> None:
	"""No-op placeholder downgrade."""
	pass
