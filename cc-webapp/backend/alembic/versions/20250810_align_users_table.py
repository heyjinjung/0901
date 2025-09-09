"""align users table with ORM (invite_code, cyber_token_balance, profile fields)

Revision ID: 20250810_align_users
Revises: 20250809_add_crash_real
Create Date: 2025-08-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '20250810_align_users'
down_revision: Union[str, None] = '20250809_add_crash_real'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    def has_column(table: str, col: str) -> bool:
        try:
            return any(c['name'] == col for c in insp.get_columns(table))
        except Exception:
            return False

    # Add missing columns to users table if not present (idempotent)
    with op.batch_alter_table('users') as batch_op:
        if not has_column('users', 'invite_code'):
            batch_op.add_column(sa.Column('invite_code', sa.String(length=10), nullable=False, server_default='5858'))
        if not has_column('users', 'cyber_token_balance'):
            batch_op.add_column(sa.Column('cyber_token_balance', sa.Integer(), nullable=False, server_default='200'))
        if not has_column('users', 'avatar_url'):
            batch_op.add_column(sa.Column('avatar_url', sa.String(length=255), nullable=True))
        if not has_column('users', 'bio'):
            batch_op.add_column(sa.Column('bio', sa.Text(), nullable=True))
        if not has_column('users', 'updated_at'):
            batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))

    # Optional: remove server_default after backfilling (only if column exists)
    if has_column('users', 'invite_code'):
        try:
            op.execute("ALTER TABLE users ALTER COLUMN invite_code DROP DEFAULT")
        except Exception:
            pass
    if has_column('users', 'cyber_token_balance'):
        try:
            op.execute("ALTER TABLE users ALTER COLUMN cyber_token_balance DROP DEFAULT")
        except Exception:
            pass


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('updated_at')
        batch_op.drop_column('bio')
        batch_op.drop_column('avatar_url')
        batch_op.drop_column('cyber_token_balance')
        batch_op.drop_column('invite_code')
