"""merge heads unify

Revision ID: b1ea2144217e
Revises: 20250811_add_invite_codes, 20250813_add_shop_tables, 20250815_admin_audit_action_created_idx
Create Date: 2025-08-15 06:55:37.669620

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1ea2144217e'
down_revision: Union[str, None] = ('20250811_add_invite_codes', '20250813_add_shop_tables', '20250815_admin_audit_action_created_idx')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
