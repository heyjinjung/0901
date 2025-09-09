"""merge heads unify

Revision ID: 20250817_merge_heads_unify
Revises: 20250817_add_dual_currency_columns, 20250817_add_idempotency_key_to_shop_transactions
Create Date: 2025-08-17

Merge head revision to unify parallel branches.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250817_merge_heads_unify'
down_revision: Union[str, None] = ('20250817_add_dual_currency_columns', '20250817_add_idempotency_key_to_shop_transactions')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
	"""Upgrade schema."""
	pass


def downgrade() -> None:
	"""Downgrade schema."""
	pass

