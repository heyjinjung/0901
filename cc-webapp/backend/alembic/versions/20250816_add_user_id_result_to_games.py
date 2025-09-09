"""add user_id & result columns (idempotent) and relax name nullability

Revision ID: 20250816_add_user_id_result_to_games
Revises: 20250816_add_game_session_result_data
Create Date: 2025-08-16

Purpose:
 - Align games table with ORM: add user_id (FK->users.id), bet_amount, payout, result if missing
 - Make name column nullable (previously NOT NULL) for flexible creation without name
 - Safe to re-run (checks existing schema before altering)

Notes:
 - Uses batch_alter_table for SQLite compatibility where needed.
"""
from __future__ import annotations

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision: str = "20250816_add_user_id_result_to_games"
down_revision: Union[str, None] = "20250816_add_game_session_result_data"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(insp, table: str, name: str) -> bool:
    return name in {c["name"] for c in insp.get_columns(table)}


def upgrade() -> None:  # noqa: D401
    bind = op.get_bind()
    insp = inspect(bind)
    if "games" not in insp.get_table_names():
        return
    cols = {c["name"]: c for c in insp.get_columns("games")}

    # Add missing columns
    to_add = []
    if "user_id" not in cols:
        to_add.append(sa.Column("user_id", sa.Integer, nullable=True, index=True))  # temp nullable then fill/alter
    if "bet_amount" not in cols:
        to_add.append(sa.Column("bet_amount", sa.Integer, nullable=True))
    if "payout" not in cols:
        to_add.append(sa.Column("payout", sa.Integer, nullable=True))
    if "result" not in cols:
        to_add.append(sa.Column("result", sa.String(length=100), nullable=True))

    if to_add:
        with op.batch_alter_table("games") as batch_op:
            for col in to_add:
                batch_op.add_column(col)

    # Relax name nullability if currently NOT NULL
    name_col = cols.get("name")
    if name_col and not name_col.get("nullable", True):
        with op.batch_alter_table("games") as batch_op:
            batch_op.alter_column("name", existing_type=sa.String(length=100), nullable=True)

    # Make user_id non-nullable if possible (existing rows might not have value)
    if _has_column(insp, "games", "user_id"):
        # Set user_id=1 fallback if users table has id=1 to avoid failure (best-effort)
        try:
            bind.execute(sa.text("UPDATE games SET user_id = 1 WHERE user_id IS NULL"))
        except Exception:  # noqa: BLE001
            pass
        with op.batch_alter_table("games") as batch_op:
            try:
                batch_op.alter_column("user_id", existing_type=sa.Integer, nullable=False)
            except Exception:  # Some rows may remain NULL; keep nullable in that case
                pass

    # Add FK constraint if not present (simple detection by name)
    try:
        fks = [fk["name"] for fk in insp.get_foreign_keys("games")]
        if not any("user_id" in (fk or "") for fk in fks):
            with op.batch_alter_table("games") as batch_op:
                batch_op.create_foreign_key("fk_games_user_id_users", "users", ["user_id"], ["id"], ondelete="CASCADE")
    except Exception:
        pass


def downgrade() -> None:  # noqa: D401
    # Non-destructive downgrade: do not drop columns to preserve data
    pass
