"""create events and missions tables

Revision ID: events_missions_001
Revises: 79b9722f373c
Create Date: 2024-12-10

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'events_missions_001'
down_revision: Union[str, None] = '79b9722f373c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Events 테이블
    op.create_table('events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('rewards', postgresql.JSON(), nullable=True),
        sa.Column('requirements', postgresql.JSON(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('priority', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    # Event Participations 테이블
    op.create_table('event_participations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('event_id', sa.Integer(), sa.ForeignKey('events.id')),
        sa.Column('progress', postgresql.JSON(), default={}),
        sa.Column('completed', sa.Boolean(), default=False),
        sa.Column('claimed_rewards', sa.Boolean(), default=False),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )
    
    # Missions 테이블
    op.create_table('missions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('mission_type', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('target_value', sa.Integer(), nullable=False),
        sa.Column('target_type', sa.String(), nullable=False),
        sa.Column('rewards', postgresql.JSON(), nullable=True),
        sa.Column('requirements', postgresql.JSON(), nullable=True),
        sa.Column('reset_period', sa.String(), nullable=True),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    # User Missions 테이블
    op.create_table('user_missions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('mission_id', sa.Integer(), sa.ForeignKey('missions.id')),
        sa.Column('current_progress', sa.Integer(), default=0),
        sa.Column('completed', sa.Boolean(), default=False),
        sa.Column('claimed', sa.Boolean(), default=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('claimed_at', sa.DateTime(), nullable=True),
        sa.Column('reset_at', sa.DateTime(), nullable=True),
    )
    
    # 인덱스 생성
    op.create_index('idx_event_active', 'events', ['is_active'])
    op.create_index('idx_event_dates', 'events', ['start_date', 'end_date'])
    op.create_index('idx_participation_user', 'event_participations', ['user_id'])
    op.create_index('idx_mission_type', 'missions', ['mission_type'])
    op.create_index('idx_user_mission', 'user_missions', ['user_id', 'mission_id'])

def downgrade():
    op.drop_table('user_missions')
    op.drop_table('missions')
    op.drop_table('event_participations')
    op.drop_table('events')