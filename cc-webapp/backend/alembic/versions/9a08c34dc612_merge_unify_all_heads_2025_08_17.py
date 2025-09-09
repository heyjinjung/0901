"""merge: unify all heads 2025-08-17

Revision ID: 9a08c34dc612
Revises: 20250816_add_achievements_tables, 20250817_add_composite_idempotency_constraint, 20250817_merge_heads_unify, d1993e6fdab6
Create Date: 2025-08-17 07:06:57.512035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a08c34dc612'
down_revision: Union[str, None] = ('20250816_add_achievements_tables', '20250817_add_composite_idempotency_constraint', '20250817_merge_heads_unify', 'd1993e6fdab6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
