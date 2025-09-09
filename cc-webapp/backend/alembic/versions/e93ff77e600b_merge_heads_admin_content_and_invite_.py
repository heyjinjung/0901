"""merge heads admin_content and invite_code

Revision ID: e93ff77e600b
Revises: 20250819_01_admin_content, 20250819_add_invite_code_to_users
Create Date: 2025-08-20 02:39:47.201616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e93ff77e600b'
down_revision: Union[str, None] = ('20250819_01_admin_content', '20250819_add_invite_code_to_users')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
