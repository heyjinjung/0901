"""
🎰 Casino-Club F2P - 통합 데이터베이스 Base 클래스
==================================================
모든 모델의 기반이 되는 Base 클래스와 공통 설정
"""

from sqlalchemy import Column, Integer, DateTime, String, Index
from sqlalchemy.orm import declarative_base
from datetime import datetime

# SQLAlchemy Base 클래스
Base = declarative_base()

# 공통 메타데이터 설정
Base.metadata.schema = None  # 스키마 없음 (기본 스키마 사용)

# 공통 컬럼 패턴들을 위한 Mixin 클래스들
class TimestampMixin:
    """생성일/수정일 자동 관리를 위한 Mixin"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class UserRelatedMixin:
    """사용자 연관 모델을 위한 Mixin"""
    user_id = Column(Integer, nullable=False, index=True)

class AdminMixin:
    """관리자 기능을 위한 Mixin"""
    is_active = Column("is_active", nullable=False, default=True)
    created_by = Column(Integer, nullable=True)  # 관리자 ID

class SoftDeleteMixin:
    """Soft delete 지원 Mixin (행 물리 삭제 대신 deleted_at 타임스탬프 기록)"""
    deleted_at = Column(DateTime, nullable=True, index=True)

    def soft_delete(self):  # runtime helper
        if not getattr(self, 'deleted_at', None):  # idempotent
            from datetime import datetime as _dt
            self.deleted_at = _dt.utcnow()

    def restore(self):  # runtime helper
        self.deleted_at = None
    
# 공통 인덱스 헬퍼
def create_compound_index(table_name: str, *columns):
    """복합 인덱스 생성 헬퍼"""
    index_name = f"ix_{table_name}_{'_'.join(columns)}"
    return Index(index_name, *columns)

# 테이블 명명 규칙
class TableNameMixin:
    """테이블 명명 규칙을 위한 기본 설정"""
    
    @classmethod
    def get_table_name(cls, model_name: str) -> str:
        """모델명을 테이블명으로 변환 (snake_case)"""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', model_name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# Export할 주요 클래스들
__all__ = [
    'Base',
    'TimestampMixin', 
    'UserRelatedMixin',
    'AdminMixin',
    'SoftDeleteMixin',
    'TableNameMixin',
    'create_compound_index'
]
