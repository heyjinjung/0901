"""콘텐츠 관련 데이터베이스 모델"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.orm import relationship

from ..database import Base


class AdultContent(Base):
    """성인 콘텐츠 모델"""
    __tablename__ = "adult_contents"

    id = Column(Integer, primary_key=True, index=True)
    stage = Column(Integer, default=1)
    required_rank = Column(String(50), default="STANDARD")
    required_segment_level = Column(Integer, default=1)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    content_type = Column(String(50), nullable=False)  # video, image, text 등
    content_url = Column(String(500))
    thumbnail_url = Column(String(500))
    category = Column(String(100))
    tags = Column(Text)  # JSON 형태의 태그 목록
    age_rating = Column(String(10), default="18+")
    is_premium = Column(Boolean, default=False)
    price = Column(Float, default=0.0)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime)
    
    # 관계
    views = relationship("ContentView", back_populates="content")
    likes = relationship("ContentLike", back_populates="content")
    purchases = relationship("ContentPurchase", back_populates="content")


class ContentView(Base):
    """콘텐츠 조회 모델"""
    __tablename__ = "content_views"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("adult_contents.id"), nullable=False)
    viewed_at = Column(DateTime, default=datetime.utcnow)
    view_duration = Column(Integer, default=0)  # 초 단위
    device_type = Column(String(50))
    ip_address = Column(String(45))
    
    # 관계
    user = relationship("User")
    content = relationship("AdultContent", back_populates="views")


class ContentLike(Base):
    """콘텐츠 좋아요 모델"""
    __tablename__ = "content_likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("adult_contents.id"), nullable=False)
    liked_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    user = relationship("User")
    content = relationship("AdultContent", back_populates="likes")


class ContentPurchase(Base):
    """콘텐츠 구매 모델"""
    __tablename__ = "content_purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("adult_contents.id"), nullable=False)
    purchase_amount = Column(Float, nullable=False)
    purchase_method = Column(String(50))  # credit_card, paypal 등
    purchased_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # 구매한 콘텐츠 만료일 (해당하는 경우)
    
    # 관계
    user = relationship("User")
    content = relationship("AdultContent", back_populates="purchases")


class ContentCategory(Base):
    """콘텐츠 카테고리 모델"""
    __tablename__ = "content_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class ContentTag(Base):
    """콘텐츠 태그 모델"""
    __tablename__ = "content_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
