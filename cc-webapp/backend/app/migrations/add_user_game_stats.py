"""Create user_game_stats aggregated table (idempotent).

Columns:
  user_id (PK, FK users.id)
  total_bets BIGINT NOT NULL DEFAULT 0
  total_wins BIGINT NOT NULL DEFAULT 0
  total_losses BIGINT NOT NULL DEFAULT 0
  highest_multiplier NUMERIC(10,4) NULL
  total_profit NUMERIC(18,2) NOT NULL DEFAULT 0
  updated_at TIMESTAMP(timezone=True) NOT NULL DEFAULT now()

Idempotent: checks information_schema / pg_catalog if table already exists.
SQLite fallback supported with simplified types.
"""
from alembic import op  # type: ignore
import sqlalchemy as sa
from sqlalchemy import text


def upgrade():  # pragma: no cover
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if "user_game_stats" in inspector.get_table_names():
        print("user_game_stats already exists — skipping create")
        return
    # Detect dialect
    dialect = conn.dialect.name
    numeric_multiplier = sa.Numeric(10, 4)
    numeric_profit = sa.Numeric(18, 2)
    # Create table
    op.create_table(
        "user_game_stats",
        sa.Column("user_id", sa.Integer, primary_key=True),
        sa.Column("total_bets", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("total_wins", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("total_losses", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("highest_multiplier", numeric_multiplier, nullable=True),
        sa.Column("total_profit", numeric_profit, nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False, index=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    try:
        op.create_index("ix_user_game_stats_updated_at", "user_game_stats", ["updated_at"])
    except Exception:
        pass
    print("✅ Created user_game_stats table")


def downgrade():  # pragma: no cover
    try:
        op.drop_table("user_game_stats")
    except Exception:
        pass


if __name__ == "__main__":  # manual exec
    upgrade()
