"""add index on admin_audit_logs(action, created_at)

Revision ID: 20250815_admin_audit_action_created_idx
Revises: 20250815_add_promo_usage_and_admin_audit
Create Date: 2025-08-15

Adds a composite index to speed up common admin audit log queries.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250815_admin_audit_action_created_idx'
down_revision: Union[str, None] = '20250815_add_promo_usage_and_admin_audit'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    try:
        indexes = insp.get_indexes('admin_audit_logs')
        if not any(ix.get('name') == 'ix_admin_audit_action_created' for ix in indexes):
            op.create_index('ix_admin_audit_action_created', 'admin_audit_logs', ['action', 'created_at'], unique=False)
    except Exception:
        # table may not exist in some environments; ignore
        pass


def downgrade() -> None:
    try:
        op.drop_index('ix_admin_audit_action_created', table_name='admin_audit_logs')
    except Exception:
        pass
