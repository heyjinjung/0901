#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔗 BaseRepository: 모든 리포지토리의 기본 클래스
공통적인 CRUD 작업과 유틸리티 메서드를 제공합니다.
"""

from typing import List, Optional, Generic, TypeVar, Type
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import logging

T = TypeVar('T')

logger = logging.getLogger(__name__)

class BaseRepository(Generic[T]):
    """모든 리포지토리의 기본 클래스"""

    def __init__(self, db: Session, model_class: Type[T]):
        self.db = db
        self.model_class = model_class

    def get_by_id(self, id: int) -> Optional[T]:
        """ID로 단일 레코드 조회"""
        try:
            return self.db.query(self.model_class).filter(
                self.model_class.id == id
            ).first()
        except Exception as e:
            logger.error(f"Error getting {self.model_class.__name__} by id {id}: {e}")
            return None

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """모든 레코드 조회 (페이지네이션)"""
        try:
            return self.db.query(self.model_class).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting all {self.model_class.__name__}: {e}")
            return []

    def create(self, **kwargs) -> Optional[T]:
        """새로운 레코드 생성"""
        try:
            instance = self.model_class(**kwargs)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except Exception as e:
            logger.error(f"Error creating {self.model_class.__name__}: {e}")
            self.db.rollback()
            return None

    def update(self, id: int, **kwargs) -> Optional[T]:
        """기존 레코드 업데이트"""
        try:
            instance = self.get_by_id(id)
            if not instance:
                return None
            
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            instance.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except Exception as e:
            logger.error(f"Error updating {self.model_class.__name__} id {id}: {e}")
            self.db.rollback()
            return None

    def delete(self, id: int) -> bool:
        """레코드 삭제"""
        try:
            instance = self.get_by_id(id)
            if not instance:
                return False
            
            self.db.delete(instance)
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting {self.model_class.__name__} id {id}: {e}")
            self.db.rollback()
            return False

    def soft_delete(self, id: int) -> bool:
        """소프트 삭제 (deleted_at 필드 설정)"""
        try:
            instance = self.get_by_id(id)
            if not instance:
                return False
            
            if hasattr(instance, 'deleted_at'):
                instance.deleted_at = datetime.utcnow()
                self.db.commit()
                return True
            else:
                # deleted_at 필드가 없으면 하드 삭제
                return self.delete(id)
        except Exception as e:
            logger.error(f"Error soft deleting {self.model_class.__name__} id {id}: {e}")
            self.db.rollback()
            return False

    def count_all(self) -> int:
        """전체 레코드 수 조회"""
        try:
            return self.db.query(func.count(self.model_class.id)).scalar()
        except Exception as e:
            logger.error(f"Error counting {self.model_class.__name__}: {e}")
            return 0

    def exists(self, id: int) -> bool:
        """레코드 존재 여부 확인"""
        try:
            return self.db.query(self.model_class).filter(
                self.model_class.id == id
            ).first() is not None
        except Exception as e:
            logger.error(f"Error checking if {self.model_class.__name__} id {id} exists: {e}")
            return False

    def filter_by(self, **kwargs) -> List[T]:
        """조건에 따른 필터링"""
        try:
            query = self.db.query(self.model_class)
            for key, value in kwargs.items():
                if hasattr(self.model_class, key):
                    query = query.filter(getattr(self.model_class, key) == value)
            return query.all()
        except Exception as e:
            logger.error(f"Error filtering {self.model_class.__name__}: {e}")
            return []

    def filter_by_date_range(self, date_field: str, start_date: datetime, end_date: datetime) -> List[T]:
        """날짜 범위로 필터링"""
        try:
            if not hasattr(self.model_class, date_field):
                logger.error(f"{self.model_class.__name__} has no field {date_field}")
                return []
            
            field = getattr(self.model_class, date_field)
            return self.db.query(self.model_class).filter(
                field >= start_date,
                field <= end_date
            ).all()
        except Exception as e:
            logger.error(f"Error filtering {self.model_class.__name__} by date range: {e}")
            return []
