"""add event_outbox table

Revision ID: 20250821_add_event_outbox
Revises: 20250816_add_game_history_and_follow_relations
Create Date: 2025-08-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250821_add_event_outbox'
down_revision = '20250816_add_game_history_and_follow_relations'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'event_outbox' in inspector.get_table_names():
        return
    op.create_table(
        'event_outbox',
        sa.Column('id', sa.BigInteger, primary_key=True),
        sa.Column('event_type', sa.String(120), nullable=False, index=True),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('schema_version', sa.Integer, nullable=False, server_default='1'),
        sa.Column('dedupe_key', sa.String(255), nullable=True, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('publish_attempts', sa.Integer, nullable=False, server_default='0'),
    )
    op.create_index('ix_event_outbox_unpublished', 'event_outbox', ['published_at'], postgresql_where=sa.text('published_at IS NULL'))

def downgrade():
    op.drop_table('event_outbox')
