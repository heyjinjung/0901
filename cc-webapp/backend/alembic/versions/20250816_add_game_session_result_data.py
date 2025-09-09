"""add result_data column to game_sessions (conditional)

Revision ID: 20250816_add_game_session_result_data
Revises: 3f9d2c1b7a10
Create Date: 2025-08-16

Purpose:
 - Ensure game_sessions has result_data JSON/Text capable column matching ORM (Column(JSON))
 - Safe to run on existing DBs (adds column only if missing)

Notes:
 - SQLite: uses batch_alter_table for ALTER TABLE compatibility.
 - Postgres/MySQL: simple add column.
 - Type chosen: JSON when supported; fallback to TEXT for older SQLite (SQLAlchemy JSON maps to TEXT w/ serializer)
"""
from __future__ import annotations

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "20250816_add_game_session_result_data"
down_revision: Union[str, None] = "3f9d2c1b7a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:  # noqa: D401
    bind = op.get_bind()
    insp = inspect(bind)
    if "game_sessions" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("game_sessions")}
    if "result_data" in cols:
        return
    # Use batch_alter_table for SQLite safety
    with op.batch_alter_table("game_sessions") as batch_op:
        batch_op.add_column(sa.Column("result_data", sa.JSON, nullable=True))


def downgrade() -> None:  # noqa: D401
    bind = op.get_bind()
    insp = inspect(bind)
    if "game_sessions" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("game_sessions")}
    if "result_data" not in cols:
        return
    with op.batch_alter_table("game_sessions") as batch_op:
        try:
            batch_op.drop_column("result_data")
        except Exception:
            # Ignore failures (e.g., dialect limitations)
            pass
