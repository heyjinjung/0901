"""Add deleted_at soft delete columns to events & shop_products (idempotent)."""
from alembic import op  # type: ignore
import sqlalchemy as sa
from sqlalchemy import text


def _add_column_if_absent(table: str, column: str, coltype):
    conn = op.get_bind()
    dialect = conn.dialect.name
    # Generic information_schema check (works on Postgres/MySQL); fallback simple pragma for SQLite
    exists = False
    try:
        exists = conn.execute(text(
            "SELECT 1 FROM information_schema.columns WHERE table_name=:t AND column_name=:c"))\
            .params(t=table, c=column).fetchone() is not None
    except Exception:
        # SQLite fallback
        try:
            res = conn.execute(text(f"PRAGMA table_info({table})"))
            for row in res:  # type: ignore
                if row[1] == column:
                    exists = True
                    break
        except Exception:
            pass
    if exists:
        print(f"[soft_delete] {table}.{column} already exists – skip")
        return
    try:
        op.add_column(table, sa.Column(column, coltype, nullable=True))
        print(f"✅ Added {column} to {table}")
    except Exception as e:
        print(f"⚠️ Failed adding {column} to {table}: {e}")


def upgrade():  # pragma: no cover
    _add_column_if_absent('events', 'deleted_at', sa.DateTime())
    _add_column_if_absent('shop_products', 'deleted_at', sa.DateTime())


def downgrade():  # pragma: no cover
    try:
        op.drop_column('events', 'deleted_at')
    except Exception:
        pass
    try:
        op.drop_column('shop_products', 'deleted_at')
    except Exception:
        pass

if __name__ == '__main__':
    upgrade()
