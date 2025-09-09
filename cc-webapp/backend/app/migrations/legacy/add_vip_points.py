"""Add vip_points column to users table (idempotent).

Adds an integer column 'vip_points' with NOT NULL default 0.
Safe to run multiple times: checks information_schema before ALTER.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


def upgrade():
    conn = op.get_bind()
    try:
        # Detect column existence (works for PostgreSQL / MySQL style information_schema)
        exists = conn.execute(text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_name='users' AND column_name='vip_points'
        """)).fetchone()
        if exists:
            print("[add_vip_points] Column already exists, skipping.")
            return
        op.add_column('users', sa.Column('vip_points', sa.Integer(), nullable=False, server_default='0'))
        # Optional: backfill explicit zeros (server_default already covers new rows)
        conn.execute(text("UPDATE users SET vip_points = 0 WHERE vip_points IS NULL"))
        print("✅ Added vip_points column to users table")
    except Exception as e:
        print(f"⚠️ Failed to add vip_points column: {e}")


def downgrade():
    try:
        op.drop_column('users', 'vip_points')
        print("✅ Dropped vip_points column from users table")
    except Exception as e:
        print(f"⚠️ Failed to drop vip_points column: {e}")

if __name__ == "__main__":
    upgrade()
