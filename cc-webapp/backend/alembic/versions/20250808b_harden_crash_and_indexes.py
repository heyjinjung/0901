"""harden crash tables and add indexes (placeholder)

Revision ID: 20250808b_harden_crash
Revises: 20250808_add_crash
Create Date: 2025-08-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250808b_harden_crash'
down_revision: Union[str, None] = '20250808_add_crash'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""No-op placeholder upgrade for crash hardening."""
	pass


def downgrade() -> None:
	"""No-op placeholder downgrade."""
	pass
