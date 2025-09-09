"""
초대코드 모델 업그레이드 스크립트
- 기존 모델에 만료 시간, 사용 횟수 제한 등 필드 추가
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta

def upgrade():
    # Add new columns to invite_codes table
    try:
        # Add expires_at column
        op.add_column(
            'invite_codes',
            sa.Column('expires_at', sa.DateTime(), nullable=True)
        )
        
        # Add max_uses column
        op.add_column(
            'invite_codes',
            sa.Column('max_uses', sa.Integer(), nullable=True, server_default='1')
        )
        
        # Add use_count column
        op.add_column(
            'invite_codes',
            sa.Column('use_count', sa.Integer(), nullable=False, server_default='0')
        )
        
        # Update existing records to set default expiration date (30 days from now)
        conn = op.get_bind()
        default_expiration = datetime.utcnow() + timedelta(days=30)
        conn.execute(
            sa.text(f"UPDATE invite_codes SET expires_at = '{default_expiration}' WHERE expires_at IS NULL")
        )
        
        print("✅ 초대코드 모델 업데이트 완료: expires_at, max_uses, use_count 필드 추가")
    except Exception as e:
        print(f"⚠️ 초대코드 모델 업데이트 실패: {str(e)}")

def downgrade():
    # Remove added columns
    try:
        op.drop_column('invite_codes', 'use_count')
        op.drop_column('invite_codes', 'max_uses')
        op.drop_column('invite_codes', 'expires_at')
        print("✅ 초대코드 모델 다운그레이드 완료")
    except Exception as e:
        print(f"⚠️ 초대코드 모델 다운그레이드 실패: {str(e)}")

if __name__ == "__main__":
    print("초대코드 모델 업그레이드 스크립트 실행")
    upgrade()
