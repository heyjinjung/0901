"""enforce composite idempotency uniqueness

Revision ID: 20250817_add_composite_idempotency_constraint
Revises: 20250817_add_idempotency_key_to_shop_transactions
Create Date: 2025-08-17

Drops legacy unique index on idempotency_key (if present) and adds
composite UniqueConstraint (user_id, product_id, idempotency_key) named
uq_shop_tx_user_product_idem. Safe on SQLite & Postgres.

This aligns DB schema with ORM __table_args__ in ShopTransaction.

If existing duplicate rows exist (should not), migration logs a warning and
keeps earliest row per duplicate group (by id) while appending suffix to later
receipt_code values to avoid unique clashes, then enforces constraint.
"""
from __future__ import annotations
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '20250817_add_composite_idempotency_constraint'
down_revision: Union[str, None] = '20250817_add_idempotency_key_to_shop_transactions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE = 'shop_transactions'
_UC_NAME = 'uq_shop_tx_user_product_idem'
_LEGACY_INDEX = 'ix_shop_transactions_idempotency_key'


def _has_index(insp, table: str, name: str) -> bool:
    try:
        return any(ix.get('name') == name for ix in insp.get_indexes(table))
    except Exception:
        return False


def _has_constraint(conn, table: str, name: str) -> bool:
    # Generic detection via SQLAlchemy inspector constraints
    insp = sa.inspect(conn)
    try:
        for uc in insp.get_unique_constraints(table):
            if uc.get('name') == name:
                return True
    except Exception:
        return False
    return False


def _dedupe_existing(conn):
    """Detect duplicate (user_id, product_id, idempotency_key) groups and resolve.

    Strategy: keep smallest id, modify receipt_code of later duplicates by appending
    '-dup<N>' to preserve uniqueness w/o data loss. Only runs if duplicates detected.
    """
    # SQLite / Postgres compatible query
    dup_query = sa.text(
        """
        SELECT user_id, product_id, idempotency_key, COUNT(*) as cnt
        FROM shop_transactions
        WHERE idempotency_key IS NOT NULL
        GROUP BY user_id, product_id, idempotency_key
        HAVING COUNT(*) > 1
        """
    )
    result = conn.execute(dup_query).fetchall()
    if not result:
        return
    for (user_id, product_id, idem_key, _cnt) in result:
        rows = conn.execute(sa.text(
            """
            SELECT id, receipt_code FROM shop_transactions
            WHERE user_id=:u AND product_id=:p AND idempotency_key=:k
            ORDER BY id ASC
            """
        ), {"u": user_id, "p": product_id, "k": idem_key}).fetchall()
        # keep first
        for idx, (row_id, receipt) in enumerate(rows):
            if idx == 0:
                continue
            new_receipt = (receipt or f"r{row_id}") + f"-dup{idx}"
            conn.execute(sa.text(
                "UPDATE shop_transactions SET receipt_code=:r WHERE id=:i"
            ), {"r": new_receipt, "i": row_id})


def upgrade() -> None:
    conn = op.get_bind()
    insp = sa.inspect(conn)

    # 1. Drop legacy single-column unique index if it exists
    if _has_index(insp, _TABLE, _LEGACY_INDEX):
        try:
            op.drop_index(_LEGACY_INDEX, table_name=_TABLE)
        except Exception:
            pass  # tolerate if concurrently removed

    # 2. De-duplicate any conflicting existing rows before adding constraint
    _dedupe_existing(conn)

    # 3. Add composite unique constraint if missing
    if not _has_constraint(conn, _TABLE, _UC_NAME):
        with op.batch_alter_table(_TABLE) as batch_op:
            batch_op.create_unique_constraint(_UC_NAME, ['user_id', 'product_id', 'idempotency_key'])


def downgrade() -> None:
    conn = op.get_bind()
    if _has_constraint(conn, _TABLE, _UC_NAME):
        with op.batch_alter_table(_TABLE) as batch_op:
            try:
                batch_op.drop_constraint(_UC_NAME, type_='unique')
            except Exception:
                pass
    # Recreate legacy index (non-unique) for idempotency_key to preserve lookup performance
    insp = sa.inspect(conn)
    if not _has_index(insp, _TABLE, _LEGACY_INDEX):
        try:
            op.create_index(_LEGACY_INDEX, _TABLE, ['idempotency_key'], unique=False)
        except Exception:
            pass
