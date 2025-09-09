"""merge receipt unique branch with prior head

Revision ID: 20250815_merge_receipt_unique_and_prev
Revises: 20250815_ensure_shop_receipt_unique, b1ea2144217e
Create Date: 2025-08-15

This merge keeps a single Alembic head without changing schema.
"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '20250815_merge_receipt_unique_and_prev'
down_revision: Union[str, None] = ('20250815_ensure_shop_receipt_unique', 'b1ea2144217e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No-op: merge only
    pass


def downgrade() -> None:
    # No-op: merge only
    pass
