"""merge heads after adding receipt_signature and vip_points

Revision ID: 20250820_merge_heads_admin_stats_shop_receipt_sig
Revises: 3d77179e36e1, 20250820_add_shop_receipt_signature
Create Date: 2025-08-20

No schema changes; establishes a single linear head.
"""
from typing import Sequence, Union

from alembic import op  # noqa: F401
import sqlalchemy as sa  # noqa: F401

revision: str = '20250820_merge_heads_admin_stats_shop_receipt_sig'
down_revision: Union[str, None] = ('3d77179e36e1', '20250820_add_shop_receipt_signature')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:  # pragma: no cover
    pass


def downgrade() -> None:  # pragma: no cover
    pass
