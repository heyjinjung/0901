"""consolidate constraint cleanup and game_stats fk hardening

Revision ID: 20250909_consolidate_constraints_batch
Revises: 20250816_add_receipt_signature
Create Date: 2025-09-09
"""
from alembic import op
import sqlalchemy as sa

revision = '20250909_consolidate_constraints_batch'
down_revision = '20250816_add_receipt_signature'
branch_labels = None
depends_on = None

# Helper inspection utilities
from typing import List

def _idx_exists(table: str, name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    for idx in insp.get_indexes(table):
        if idx.get('name') == name:
            return True
    return False


def _unique_constraint_exists(table: str, columns: List[str]) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    targets = set(columns)
    for uc in insp.get_unique_constraints(table):
        if set(uc.get('column_names') or []) == targets:
            return True
    return False


def _column_nullable(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    for col in insp.get_columns(table):
        if col['name'] == column:
            return col.get('nullable', True)
    return True


def upgrade():
    # 1. shop_transactions: drop legacy single-column uniques (user_id, product_id) if present
    #    keep composite (user_id, product_id, idempotency_key)
    composite = ['user_id', 'product_id', 'idempotency_key']
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # gather existing uniques for shop_transactions
    for uc in insp.get_unique_constraints('shop_transactions'):
        cols = uc.get('column_names') or []
        name = uc.get('name')
        if cols and len(cols) == 1 and cols[0] in ('user_id','product_id'):
            op.drop_constraint(name, 'shop_transactions', type_='unique')

    # 2. follow_relations: drop single-column uniques if both user_id / target_user_id appear individually
    try:
        for uc in insp.get_unique_constraints('follow_relations'):
            cols = uc.get('column_names') or []
            name = uc.get('name')
            if cols and len(cols) == 1 and cols[0] in ('user_id','target_user_id'):
                op.drop_constraint(name, 'follow_relations', type_='unique')
    except Exception:
        pass

    # 3. event_mission_links: drop single-column uniques similar pattern
    try:
        for uc in insp.get_unique_constraints('event_mission_links'):
            cols = uc.get('column_names') or []
            name = uc.get('name')
            if cols and len(cols) == 1 and cols[0] in ('event_id','mission_template_id'):
                op.drop_constraint(name, 'event_mission_links', type_='unique')
    except Exception:
        pass

    # 4. game_stats: enforce user_id NOT NULL
    if _column_nullable('game_stats','user_id'):
        with op.batch_alter_table('game_stats') as batch:
            batch.alter_column('user_id', existing_type=sa.Integer(), nullable=False)


def downgrade():
    # Non-destructive downgrade attempt: can't restore exact previous unique names deterministically
    # Provide minimal safety by re-adding single column uniques if missing.
    for table, col in (
        ('shop_transactions','user_id'),
        ('shop_transactions','product_id'),
        ('follow_relations','user_id'),
        ('follow_relations','target_user_id'),
        ('event_mission_links','event_id'),
        ('event_mission_links','mission_template_id'),
    ):
        if not _unique_constraint_exists(table, [col]):
            try:
                op.create_unique_constraint(f'uq_restore_{table}_{col}', table, [col])
            except Exception:
                pass

    # Relax NOT NULL for game_stats.user_id (best effort)
    if not _column_nullable('game_stats','user_id'):
        with op.batch_alter_table('game_stats') as batch:
            batch.alter_column('user_id', existing_type=sa.Integer(), nullable=True)
