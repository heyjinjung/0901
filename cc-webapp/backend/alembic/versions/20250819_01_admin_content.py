"""admin content persistence (events, mission templates, reward catalog, reward audit)

Revision ID: 20250819_01_admin_content
Revises: 
Create Date: 2025-08-19

Single consolidated initial revision for new admin persistence tables.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20250819_01_admin_content"
down_revision = None  # consolidate as first formal revision for these tables
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    if not insp.has_table("admin_events"):
        op.create_table(
        "admin_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("start_at", sa.DateTime(), nullable=False),
        sa.Column("end_at", sa.DateTime(), nullable=False),
        sa.Column("reward_scheme", sa.JSON(), nullable=False),
    sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("name", name="uq_admin_events_name"),
    )
        op.create_index("ix_admin_events_active_window", "admin_events", ["is_active", "start_at", "end_at"])  # composite
    if not insp.has_table("mission_templates"):
        op.create_table(
        "mission_templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("mission_type", sa.String(20), nullable=False),
        sa.Column("target", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("reward", sa.JSON(), nullable=False),
    sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
        op.create_index("ix_mission_templates_active_type", "mission_templates", ["is_active", "mission_type"])  # composite
    if not insp.has_table("event_mission_links"):
        op.create_table(
        "event_mission_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("admin_events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mission_template_id", sa.Integer(), sa.ForeignKey("mission_templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("event_id", "mission_template_id", name="uq_event_mission_pair"),
    )
    if not insp.has_table("reward_catalog"):
        op.create_table(
        "reward_catalog",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("reward_type", sa.String(50), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
    # 'metadata' column maps to model attribute 'meta' (SQLAlchemy reserved attr workaround)
    sa.Column("metadata", sa.JSON(), nullable=False),
    sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.UniqueConstraint("code", name="uq_reward_catalog_code"),
    )
        op.create_index("ix_reward_catalog_active_type", "reward_catalog", ["active", "reward_type"])  # composite
    if not insp.has_table("reward_audit"):
        op.create_table(
        "reward_audit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reward_type", sa.String(50), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("admin_events.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
        op.create_index("ix_reward_audit_user_created", "reward_audit", ["user_id", "created_at"])  # composite
        op.create_index("ix_reward_audit_event_created", "reward_audit", ["event_id", "created_at"])  # composite


def downgrade() -> None:
    op.drop_index("ix_reward_audit_event_created", table_name="reward_audit")
    op.drop_index("ix_reward_audit_user_created", table_name="reward_audit")
    op.drop_table("reward_audit")

    op.drop_index("ix_reward_catalog_active_type", table_name="reward_catalog")
    op.drop_table("reward_catalog")

    op.drop_table("event_mission_links")

    op.drop_index("ix_mission_templates_active_type", table_name="mission_templates")
    op.drop_table("mission_templates")

    op.drop_index("ix_admin_events_active_window", table_name="admin_events")
    op.drop_table("admin_events")
