"""extend alembic_version.version_num length to 128

Revision ID: 00000001_extend_alembic_version_len
Revises: 79b9722f373c
Create Date: 2025-08-19
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '00000001_extend_alembic_version_len'
down_revision: Union[str, None] = '79b9722f373c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if 'alembic_version' in insp.get_table_names():
        op.execute('ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(128)')


def downgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)
    if 'alembic_version' in insp.get_table_names():
        op.execute('ALTER TABLE alembic_version ALTER COLUMN version_num TYPE VARCHAR(32)')
