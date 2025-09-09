"""add invite_code column to users

Revision ID: 20250819_add_invite_code_to_users
Revises: 889936e3a236
Create Date: 2025-08-19 05:09:00

이전 정리 과정에서 users.invite_code 컬럼이 마이그레이션에 존재하지 않아
런타임 모델(User.invite_code)과 실제 스키마가 불일치 → 시드/테스트 실패.
멱등하게 컬럼을 추가한다.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '20250819_add_invite_code_to_users'
down_revision: Union[str, None] = '889936e3a236'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    cols = [c['name'] for c in inspector.get_columns('users')]
    if 'invite_code' not in cols:
        op.add_column('users', sa.Column('invite_code', sa.String(length=10), nullable=True))
        # 기존 행 초기화 (없을 가능성 높음)
        op.execute("UPDATE users SET invite_code='5858' WHERE invite_code IS NULL")
        op.alter_column('users', 'invite_code', existing_type=sa.String(length=10), nullable=False)


def downgrade() -> None:
    # 안전을 위해 존재할 때만 제거
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    cols = [c['name'] for c in inspector.get_columns('users')]
    if 'invite_code' in cols:
        op.drop_column('users', 'invite_code')
