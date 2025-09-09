"""Initial database schema

Revision ID: 79b9722f373c
Revises: 
Create Date: 2025-08-06 00:38:28.382749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import relationship


# revision identifiers, used by Alembic.
revision: str = '79b9722f373c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 사용자 및 인증 관련 테이블
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('site_id', sa.String(length=100), nullable=False),
        sa.Column('nickname', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('vip_tier', sa.String(length=20), server_default='STANDARD', nullable=False),
        sa.Column('battlepass_level', sa.Integer(), server_default='0', nullable=False),
        sa.Column('total_spent', sa.Integer(), server_default='0', nullable=False),
        sa.Column('gold_balance', sa.Integer(), server_default='1000', nullable=False),
        sa.Column('gem_balance', sa.Integer(), server_default='50', nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('is_admin', sa.Boolean(), server_default='false', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('site_id'),
        sa.UniqueConstraint('nickname')
    )
    
    # 사용자 세션 테이블 (User.sessions 관계를 위한 테이블)
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('token', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 초대 코드 테이블
    op.create_table(
        'invite_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('max_uses', sa.Integer(), nullable=True),
        sa.Column('uses', sa.Integer(), server_default='0', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # 사용자 세그먼트 테이블
    op.create_table(
        'user_segments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('rfm_group', sa.String(length=20), nullable=True),
        sa.Column('ltv_score', sa.Float(), nullable=True),
        sa.Column('risk_profile', sa.String(length=20), nullable=True),
        sa.Column('last_updated', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 게임 기록 관련 테이블
    op.create_table(
        'user_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 인덱스 생성
    op.create_index(op.f('ix_user_sessions_user_id'), 'user_sessions', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_segments_user_id'), 'user_segments', ['user_id'], unique=True)
    op.create_index(op.f('ix_user_actions_action_type'), 'user_actions', ['action_type'], unique=False)
    op.create_index(op.f('ix_user_actions_user_id'), 'user_actions', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # 역순으로 테이블 삭제
    op.drop_index(op.f('ix_user_actions_user_id'), table_name='user_actions')
    op.drop_index(op.f('ix_user_actions_action_type'), table_name='user_actions')
    op.drop_index(op.f('ix_user_segments_user_id'), table_name='user_segments')
    op.drop_index(op.f('ix_user_sessions_user_id'), table_name='user_sessions')
    
    op.drop_table('user_actions')
    op.drop_table('user_segments')
    op.drop_table('invite_codes')
    op.drop_table('user_sessions')
    op.drop_table('users')


# User 클래스 내부의 sessions 관계 정의 예시
sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
