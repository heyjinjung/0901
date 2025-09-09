"""add progress meta + uniques for events & missions

Revision ID: 86171b66491f
Revises: 20250821_merge_event_outbox_progress_meta_heads
Create Date: 2025-08-21 10:45:02.658332

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86171b66491f'
down_revision: Union[str, None] = '20250821_merge_event_outbox_progress_meta_heads'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """progress_version / last_progress_at 컬럼 및 UNIQUE/인덱스 조건부 추가"""
    conn = op.get_bind()
    insp = sa.inspect(conn)

    evt = 'event_participations'
    mis = 'user_missions'

    def has_table(t: str) -> bool:
        try:
            return t in insp.get_table_names()
        except Exception:
            return False

    def has_col(t: str, c: str) -> bool:
        try:
            return c in {col['name'] for col in insp.get_columns(t)}
        except Exception:
            return False

    def has_uq(t: str, name: str) -> bool:
        try:
            return name in {c['name'] for c in insp.get_unique_constraints(t)}
        except Exception:
            return False

    def has_index(t: str, name: str) -> bool:
        try:
            return name in {i['name'] for i in insp.get_indexes(t)}
        except Exception:
            return False

    # event_participations
    if has_table(evt):
        if not has_col(evt, 'progress_version'):
            op.add_column(evt, sa.Column('progress_version', sa.Integer(), nullable=False, server_default='0'))
        if not has_col(evt, 'last_progress_at'):
            op.add_column(evt, sa.Column('last_progress_at', sa.DateTime(), nullable=True))
        if not has_uq(evt, 'uq_event_participation_user_event'):
            try:
                op.create_unique_constraint('uq_event_participation_user_event', evt, ['user_id','event_id'])
            except Exception:
                pass
        if not has_index(evt, 'ix_event_participations_user_completed'):
            op.create_index('ix_event_participations_user_completed', evt, ['user_id','completed','claimed_rewards'])

    # user_missions
    if has_table(mis):
        if not has_col(mis, 'progress_version'):
            op.add_column(mis, sa.Column('progress_version', sa.Integer(), nullable=False, server_default='0'))
        if not has_col(mis, 'last_progress_at'):
            op.add_column(mis, sa.Column('last_progress_at', sa.DateTime(), nullable=True))
        if not has_uq(mis, 'uq_user_mission_user_mission'):
            try:
                op.create_unique_constraint('uq_user_mission_user_mission', mis, ['user_id','mission_id'])
            except Exception:
                pass
        if not has_index(mis, 'ix_user_missions_user_completed'):
            op.create_index('ix_user_missions_user_completed', mis, ['user_id','completed','claimed'])

    # backfill & drop server_default for progress_version if we added it
    for tbl in [evt, mis]:
        if has_table(tbl) and has_col(tbl, 'progress_version'):
            try:
                op.execute(f"UPDATE {tbl} SET progress_version=0 WHERE progress_version IS NULL")
            except Exception:
                pass
    for tbl in [evt, mis]:
        if has_table(tbl) and has_col(tbl, 'progress_version'):
            try:
                with op.batch_alter_table(tbl) as batch:
                    batch.alter_column('progress_version', server_default=None)
            except Exception:
                pass


def downgrade() -> None:
    # Best-effort rollback (제약/인덱스/컬럼 제거)
    for name, tbl in [
        ('ix_event_participations_user_completed','event_participations'),
        ('ix_user_missions_user_completed','user_missions'),
    ]:
        try:
            op.drop_index(name, table_name=tbl)
        except Exception:
            pass
    for name, tbl in [
        ('uq_event_participation_user_event','event_participations'),
        ('uq_user_mission_user_mission','user_missions'),
    ]:
        try:
            op.drop_constraint(name, table_name=tbl, type_='unique')
        except Exception:
            pass
    for col, tbl in [
        ('progress_version','event_participations'),
        ('last_progress_at','event_participations'),
        ('progress_version','user_missions'),
        ('last_progress_at','user_missions'),
    ]:
        try:
            op.drop_column(tbl, col)
        except Exception:
            pass
