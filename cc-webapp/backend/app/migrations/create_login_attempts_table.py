"""Create login_attempts table if missing.

Ad-hoc migration because prior schema reset dropped the table while
the model (LoginAttempt) is still referenced. Running upgrade() is
idempotent; it will skip if the table already exists.
"""
from alembic import op  # type: ignore
import sqlalchemy as sa


def upgrade():  # pragma: no cover
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if "login_attempts" in inspector.get_table_names():
        print("login_attempts table already exists — skipping create")
        return
    op.create_table(
        "login_attempts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("site_id", sa.String(50), nullable=False, index=True),
        sa.Column("success", sa.Boolean, nullable=False, index=True),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("user_agent", sa.Text),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now(), index=True),
        sa.Column("failure_reason", sa.String(100)),
    )
    try:
        op.create_index(
            "ix_login_attempts_site_created",
            "login_attempts",
            ["site_id", "created_at"],
        )
    except Exception:
        pass
    print("✅ Created login_attempts table")


def downgrade():  # pragma: no cover
    try:
        op.drop_table("login_attempts")
    except Exception:
        pass


if __name__ == "__main__":  # For manual invocation
    try:
        upgrade()
    except Exception as e:  # pragma: no cover
        print(f"Failed creating login_attempts: {e}")
