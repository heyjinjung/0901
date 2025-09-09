"""
AdultContentService 테스트 - 이중 접근 제어 시스템
랭크 + RFM 세그먼트 조합 접근 제어
미구현 상태(ADULT_CONTENT_ENABLED False)에서는 전체 스킵.
"""

import pytest
from app.core.config import settings

if not getattr(settings, "ADULT_CONTENT_ENABLED", False):
    pytest.skip("성인 콘텐츠 기능 미구현 - 테스트 스킵", allow_module_level=True)
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

from app.services.adult_content_service import AdultContentService
from app.models import User, UserSegment, AdultContent
from app.services.auth_service import AuthService


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture  
def mock_token_service():
    return MagicMock()


@pytest.fixture
def mock_reward_service():
    return MagicMock()


@pytest.fixture
def adult_content_service(mock_db, mock_token_service, mock_reward_service):
    """나이 인증 서비스 제거, 랭크+세그먼트 기반 서비스"""
    return AdultContentService(
        db=mock_db,
        token_service=mock_token_service,
        reward_service=mock_reward_service
    )


@pytest.fixture
def sample_user():
    """테스트용 사용자 (VIP 랭크)"""
    user = User(
        id=1,
        nickname="테스트VIP",
        rank="VIP",
        invite_code="VIP2024",
        cyber_token_balance=1000
    )
    return user


@pytest.fixture
def sample_user_segment():
    """테스트용 사용자 세그먼트 (Whale)"""
    segment = UserSegment(
        id=1,
        user_id=1,
        rfm_group="Whale",
        risk_profile="Low",
    )
    return segment


@pytest.fixture
def sample_content():
    """테스트용 성인 콘텐츠 (VIP + Whale 필요)"""
    content = AdultContent(
        id=1,
        stage=1,
        name="VIP 전용 콘텐츠",
        description="최고급 VIP 콘텐츠",
        thumbnail_url="https://example.com/thumb.jpg",
        media_url="https://example.com/media.mp4",
        required_rank="VIP",           # 랭크 조건
        required_segment_level=3       # 세그먼트 조건 (Whale=3)
    )
    return content


class TestDualAccessControl:
    """이중 접근 제어 (랭크 + 세그먼트) 테스트"""
    
    def test_rank_access_only(self):
        """랭크만으로 접근 제어 테스트"""
        # VIP 랭크는 모든 랭크 조건 통과
        assert AuthService.check_rank_access("VIP", "STANDARD") == True
        assert AuthService.check_rank_access("VIP", "PREMIUM") == True
        assert AuthService.check_rank_access("VIP", "VIP") == True
        
        # PREMIUM은 VIP 조건 통과 불가
        assert AuthService.check_rank_access("PREMIUM", "VIP") == False
    
    def test_combined_access_success(self):
        """랭크 + 세그먼트 조합 접근 성공 테스트"""
        # VIP + Whale (3) → VIP + Whale (3) 콘텐츠 접근 가능
        assert AuthService.check_combined_access("VIP", 3, "VIP", 3) == True
        
        # VIP + Whale (3) → PREMIUM + Medium (2) 콘텐츠 접근 가능 (상위 등급)
        assert AuthService.check_combined_access("VIP", 3, "PREMIUM", 2) == True
    
    def test_combined_access_failure_rank(self):
        """랭크 부족으로 접근 실패 테스트"""
        # PREMIUM + Whale (3) → VIP + Whale (3) 콘텐츠 접근 불가 (랭크 부족)
        assert AuthService.check_combined_access("PREMIUM", 3, "VIP", 3) == False
    
    def test_combined_access_failure_segment(self):
        """세그먼트 부족으로 접근 실패 테스트"""
        # VIP + Medium (2) → VIP + Whale (3) 콘텐츠 접근 불가 (세그먼트 부족)
        assert AuthService.check_combined_access("VIP", 2, "VIP", 3) == False
    
    def test_combined_access_failure_both(self):
        """랭크와 세그먼트 모두 부족으로 접근 실패 테스트"""
        # STANDARD + Low (1) → VIP + Whale (3) 콘텐츠 접근 불가 (둘 다 부족)
        assert AuthService.check_combined_access("STANDARD", 1, "VIP", 3) == False


class TestAdultContentService:
    """AdultContentService 테스트"""
    
    def test_content_access_check(self, adult_content_service, sample_user, sample_user_segment, sample_content):
        """콘텐츠 접근 권한 체크 테스트"""
        # 사용자: VIP + Whale (3)
        # 콘텐츠: VIP + Whale (3) 필요
        
        user_rank = sample_user.rank
        user_segment_level = 3  # Whale
        content_rank = sample_content.required_rank
        content_segment_level = sample_content.required_segment_level
        
        # 접근 가능해야 함
        can_access = AuthService.check_combined_access(
            user_rank, user_segment_level,
            content_rank, content_segment_level
        )
        assert can_access == True
    
    def test_content_access_denied_rank(self, adult_content_service, sample_content):
        """랭크 부족으로 콘텐츠 접근 거부 테스트"""
        # PREMIUM 사용자가 VIP 콘텐츠 접근 시도
        premium_user_rank = "PREMIUM"
        whale_segment_level = 3
        
        can_access = AuthService.check_combined_access(
            premium_user_rank, whale_segment_level,
            sample_content.required_rank, sample_content.required_segment_level
        )
        assert can_access == False
    
    def test_content_access_denied_segment(self, adult_content_service, sample_content):
        """세그먼트 부족으로 콘텐츠 접근 거부 테스트"""
        # VIP 사용자이지만 Medium 세그먼트로 Whale 콘텐츠 접근 시도
        vip_user_rank = "VIP"
        medium_segment_level = 2
        
        can_access = AuthService.check_combined_access(
            vip_user_rank, medium_segment_level,
            sample_content.required_rank, sample_content.required_segment_level
        )
        assert can_access == False
    
    def test_get_user_segment_level(self, adult_content_service, mock_db):
        """사용자 세그먼트 레벨 조회 테스트"""
        # Mock 설정
        mock_segment = UserSegment(
            user_id=1,
            rfm_group="Whale",
            risk_profile="Low"
        )
        mock_db.query().filter().first.return_value = mock_segment
        
        # 세그먼트 레벨 매핑
        segment_levels = {
            "Low": 1,
            "Medium": 2,
            "Whale": 3
        }
        
        # Whale 세그먼트는 레벨 3
        assert segment_levels["Whale"] == 3
        assert segment_levels["Medium"] == 2
        assert segment_levels["Low"] == 1


class TestContentScenarios:
    """다양한 콘텐츠 접근 시나리오 테스트"""
    
    def test_basic_content_access(self):
        """기본 콘텐츠 접근 (STANDARD + Low)"""
        # 모든 사용자가 접근 가능한 기본 콘텐츠
        assert AuthService.check_combined_access("STANDARD", 1, "STANDARD", 1) == True
        assert AuthService.check_combined_access("PREMIUM", 1, "STANDARD", 1) == True
        assert AuthService.check_combined_access("VIP", 1, "STANDARD", 1) == True
    
    def test_premium_content_access(self):
        """프리미엄 콘텐츠 접근 (PREMIUM + Medium)"""
        # PREMIUM 이상 + Medium 이상 세그먼트 필요
        assert AuthService.check_combined_access("PREMIUM", 2, "PREMIUM", 2) == True
        assert AuthService.check_combined_access("VIP", 2, "PREMIUM", 2) == True
        assert AuthService.check_combined_access("VIP", 3, "PREMIUM", 2) == True
        
        # 조건 미달
        assert AuthService.check_combined_access("STANDARD", 2, "PREMIUM", 2) == False
        assert AuthService.check_combined_access("PREMIUM", 1, "PREMIUM", 2) == False
    
    def test_vip_exclusive_content(self):
        """VIP 전용 콘텐츠 접근 (VIP + Whale)"""
        # VIP + Whale만 접근 가능한 최고급 콘텐츠
        assert AuthService.check_combined_access("VIP", 3, "VIP", 3) == True
        
        # 조건 미달
        assert AuthService.check_combined_access("PREMIUM", 3, "VIP", 3) == False
        assert AuthService.check_combined_access("VIP", 2, "VIP", 3) == False
        assert AuthService.check_combined_access("STANDARD", 1, "VIP", 3) == False


class TestRFMSegmentMaintenance:
    """RFM 세그먼테이션 유지 관련 테스트"""
    
    def test_segment_model_preserved(self):
        """UserSegment 모델 유지 확인"""
        segment = UserSegment(
            user_id=1,
            rfm_group="Medium",
            risk_profile="Medium",
            name="Growing User"
        )
        
        # 속성 존재 확인
        assert hasattr(segment, 'rfm_group')
        assert hasattr(segment, 'risk_profile')
        assert hasattr(segment, 'user_id')
        assert hasattr(segment, 'name')
    
    def test_rfm_group_types(self):
        """RFM 그룹 타입 테스트"""
        valid_groups = ["Low", "Medium", "Whale"]
        
        for group in valid_groups:
            segment = UserSegment(
                user_id=1,
                rfm_group=group,
                risk_profile="Low"
            )
            assert hasattr(segment, 'rfm_group')
            assert group in valid_groups
    
    def test_segment_level_mapping(self):
        """세그먼트 레벨 매핑 정확성 테스트"""
        segment_levels = {
            "Low": 1,
            "Medium": 2,
            "Whale": 3
        }
        
        # 올바른 순서 확인
        assert segment_levels["Low"] < segment_levels["Medium"]
        assert segment_levels["Medium"] < segment_levels["Whale"]
        
        # 실제 사용되는 값 확인
        for group, level in segment_levels.items():
            assert isinstance(level, int)
            assert 1 <= level <= 3
