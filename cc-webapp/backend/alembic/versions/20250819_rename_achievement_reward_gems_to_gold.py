"""rename achievement reward_gems to reward_gold

Revision ID: 20250819_rename_achievement_reward_gems_to_gold
Revises: 5406d1d5345d
Create Date: 2025-08-19

변경 내용:
    - achievements.reward_gems 컬럼을 reward_gold 로 rename
    - 기존 데이터 값은 그대로 유지
주의:
    - ORM 모델은 이미 reward_gold 로 반영됨
    - downgrade 시 역방향 rename
"""
from __future__ import annotations

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '20250819_rename_achievement_reward_gems_to_gold'
down_revision: Union[str, None] = '5406d1d5345d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 컬럼 존재 여부 안전 검사 (일부 환경에서 중복 실행 대비)
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    cols = [c['name'] for c in inspector.get_columns('achievements')]
    if 'reward_gold' in cols and 'reward_gems' not in cols:
        return  # 이미 적용됨
    if 'reward_gems' not in cols:
        # 예상치 못한 상태 (이미 수동 삭제된 경우) → noop
        return
    if 'reward_gold' in cols:
        # 둘 다 있으면 충돌 가능성 → reward_gold 제거 후 rename 진행
        op.drop_column('achievements', 'reward_gold')
    op.alter_column('achievements', 'reward_gems', new_column_name='reward_gold', existing_type=sa.Integer(), existing_nullable=False, existing_server_default=sa.text('0'))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    cols = [c['name'] for c in inspector.get_columns('achievements')]
    if 'reward_gems' in cols and 'reward_gold' not in cols:
        return  # 이미 되돌려짐
    if 'reward_gold' not in cols:
        return
    if 'reward_gems' in cols:
        op.drop_column('achievements', 'reward_gems')
    op.alter_column('achievements', 'reward_gold', new_column_name='reward_gems', existing_type=sa.Integer(), existing_nullable=False, existing_server_default=sa.text('0'))
