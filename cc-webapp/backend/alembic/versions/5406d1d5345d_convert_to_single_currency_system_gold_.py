"""Convert to single currency system - gold only

Revision ID: 5406d1d5345d
Revises: d9dfca4f3c81
Create Date: 2025-08-19 00:45:48.335332

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5406d1d5345d'
down_revision: Union[str, None] = 'd9dfca4f3c81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # gold_balance 컬럼이 이미 존재하는지 확인
    from sqlalchemy import inspect
    from sqlalchemy.engine import Engine
    
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    # gold_balance가 없으면 추가
    if 'gold_balance' not in columns:
        op.add_column('users', sa.Column('gold_balance', sa.Integer(), nullable=False, server_default='1000'))
    
    # 기존 잔액을 골드로 통합 (cyber_token + regular_coin + premium_gem * 10)
    # 프리미엄 젬은 1:10 비율로 변환
    op.execute("""
        UPDATE users 
        SET gold_balance = GREATEST(
            COALESCE(cyber_token_balance, 0) + 
            COALESCE(regular_coin_balance, 0) + 
            COALESCE(premium_gem_balance, 0) * 10,
            1000
        )
    """)
    
    # gem_balance 컬럼 제거 (있으면)
    if 'gem_balance' in columns:
        op.drop_column('users', 'gem_balance')
    
    # 기존 통화 컬럼들 제거
    if 'cyber_token_balance' in columns:
        op.drop_column('users', 'cyber_token_balance')
    if 'regular_coin_balance' in columns:
        op.drop_column('users', 'regular_coin_balance') 
    if 'premium_gem_balance' in columns:
        op.drop_column('users', 'premium_gem_balance')


def downgrade() -> None:
    """Downgrade schema."""
    # 기존 통화 컬럼들 복원
    op.add_column('users', sa.Column('premium_gem_balance', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('regular_coin_balance', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('cyber_token_balance', sa.Integer(), nullable=True))
    
    # 골드를 다시 분리 (대략적인 역변환)
    op.execute("""
        UPDATE users 
        SET cyber_token_balance = gold_balance / 3,
            regular_coin_balance = gold_balance / 3,
            premium_gem_balance = gold_balance / 30
    """)
    
    # gold_balance 컬럼 제거
    op.drop_column('users', 'gold_balance')
