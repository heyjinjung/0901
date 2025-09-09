"""merge heads after version len extend

Revision ID: 889936e3a236
Revises: 20250819_rename_achievement_reward_gems_to_gold, 00000001_extend_alembic_version_len
Create Date: 2025-08-19 04:51:23.420507

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '889936e3a236'
down_revision: Union[str, None] = ('20250819_rename_achievement_reward_gems_to_gold', '00000001_extend_alembic_version_len')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
