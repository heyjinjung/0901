"""Auth schema alignment

Revision ID: 3f9d2c1b7a10
Revises: 2a962f1d3366
Create Date: 2025-08-16 12:00:00.000000

Purpose:
 - Align user_sessions table with current ORM (session_token, refresh_token, last_used_at)
 - Create token_blacklist table if missing
 - Create refresh_tokens table if missing
 - Add indexes matching models

This migration is defensive/conditional to safely run against existing
SQLite test databases that may have been partially created via metadata.create_all.
"""

from __future__ import annotations

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "3f9d2c1b7a10"
down_revision: Union[str, None] = "2a962f1d3366"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(inspector, table: str, column: str) -> bool:
    try:
        cols = [c["name"] for c in inspector.get_columns(table)]
        return column in cols
    except Exception:
        return False


def upgrade() -> None:  # noqa: D401
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    # 1. Align user_sessions
    if "user_sessions" in tables:
        # Rename token -> session_token if needed
        has_token_col = _has_column(inspector, "user_sessions", "token")
        has_session_token_col = _has_column(inspector, "user_sessions", "session_token")
        if has_token_col and not has_session_token_col:
            try:
                with op.batch_alter_table("user_sessions") as batch_op:
                    batch_op.alter_column("token", new_column_name="session_token")
            except Exception:
                # Fallback: create session_token column copying data
                if not _has_column(inspector, "user_sessions", "session_token"):
                    with op.batch_alter_table("user_sessions") as batch_op:
                        batch_op.add_column(sa.Column("session_token", sa.String(length=255), nullable=True))
                    # Copy data (best effort)
                    bind.execute(sa.text(
                        "UPDATE user_sessions SET session_token = token WHERE session_token IS NULL"))
            # Ensure NOT NULL + uniqueness
            with op.batch_alter_table("user_sessions") as batch_op:
                batch_op.alter_column("session_token", existing_type=sa.String(length=255), nullable=False)
                # Create index if missing
                idx_names = {ix["name"] for ix in inspector.get_indexes("user_sessions")}
                if "ix_user_sessions_session_token" not in idx_names:
                    batch_op.create_index("ix_user_sessions_session_token", ["session_token"], unique=True)

        # Add refresh_token column if missing
        if not _has_column(inspector, "user_sessions", "refresh_token"):
            with op.batch_alter_table("user_sessions") as batch_op:
                batch_op.add_column(sa.Column("refresh_token", sa.String(length=255), nullable=True))
                idx_names = {ix["name"] for ix in inspector.get_indexes("user_sessions")}
                if "ix_user_sessions_refresh_token" not in idx_names:
                    batch_op.create_index("ix_user_sessions_refresh_token", ["refresh_token"], unique=True)

        # Add last_used_at column if missing
        if not _has_column(inspector, "user_sessions", "last_used_at"):
            with op.batch_alter_table("user_sessions") as batch_op:
                batch_op.add_column(sa.Column("last_used_at", sa.DateTime(), nullable=True))
            # Populate with created_at values for existing rows
            if _has_column(inspector, "user_sessions", "created_at"):
                try:
                    bind.execute(sa.text(
                        "UPDATE user_sessions SET last_used_at = created_at WHERE last_used_at IS NULL"))
                except Exception:
                    pass

    # 2. token_blacklist table
    if "token_blacklist" not in tables:
        op.create_table(
            "token_blacklist",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("token", sa.String(length=255), nullable=False),
            sa.Column("jti", sa.String(length=36), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("blacklisted_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("blacklisted_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("reason", sa.String(length=100), nullable=True),
            sa.UniqueConstraint("token"),
            sa.UniqueConstraint("jti"),
        )
        op.create_index("ix_token_blacklist_token", "token_blacklist", ["token"], unique=False)
        op.create_index("ix_token_blacklist_jti", "token_blacklist", ["jti"], unique=False)

    # 3. refresh_tokens table
    if "refresh_tokens" not in tables:
        op.create_table(
            "refresh_tokens",
            sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("token", sa.String(length=255), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("is_revoked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.UniqueConstraint("token"),
        )
        op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"], unique=False)


def downgrade() -> None:  # noqa: D401
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if "refresh_tokens" in tables:
        op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
        op.drop_table("refresh_tokens")

    if "token_blacklist" in tables:
        try:
            op.drop_index("ix_token_blacklist_token", table_name="token_blacklist")
        except Exception:
            pass
        try:
            op.drop_index("ix_token_blacklist_jti", table_name="token_blacklist")
        except Exception:
            pass
        op.drop_table("token_blacklist")

    if "user_sessions" in tables:
        has_session_token_col = _has_column(inspector, "user_sessions", "session_token")
        has_token_col = _has_column(inspector, "user_sessions", "token")
        if has_session_token_col and not has_token_col:
            try:
                with op.batch_alter_table("user_sessions") as batch_op:
                    batch_op.alter_column("session_token", new_column_name="token")
            except Exception:
                pass
        for col in ["refresh_token", "last_used_at"]:
            if _has_column(inspector, "user_sessions", col):
                try:
                    with op.batch_alter_table("user_sessions") as batch_op:
                        batch_op.drop_column(col)
                except Exception:
                    pass
        try:
            op.drop_index("ix_user_sessions_session_token", table_name="user_sessions")
        except Exception:
            pass
        try:
            op.drop_index("ix_user_sessions_refresh_token", table_name="user_sessions")
        except Exception:
            pass
