"""추가 테스트: game_service.py의 위임 패턴과 초기화 로직 테스트."""

import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

import pytest
from app.services.game_service import GameService
from app.services.slot_service import SlotService, SlotSpinResult
from app.services.roulette_service import RouletteService, RouletteSpinResult
from app.services.gacha_service import GachaService, GachaPullResult
from app.repositories.game_repository import GameRepository


class TestGameServiceDelegation(unittest.TestCase):
    """GameService의 위임 패턴과 초기화 테스트."""

    def setUp(self):
        """테스트를 위한 기본 설정."""
        self.mock_repo = MagicMock(spec=GameRepository)
        self.mock_db = MagicMock(spec=Session)
        
        # 서비스 모킹
        self.mock_slot_service = MagicMock(spec=SlotService)
        self.mock_roulette_service = MagicMock(spec=RouletteService)
        self.mock_gacha_service = MagicMock(spec=GachaService)
        
        # 패치 설정
        self.mock_slot_class = MagicMock(return_value=self.mock_slot_service)
        self.mock_roulette_class = MagicMock(return_value=self.mock_roulette_service)
        self.mock_gacha_class = MagicMock(return_value=self.mock_gacha_service)
        
        self.patcher_slot = patch('app.services.game_service.SlotService', self.mock_slot_class)
        self.patcher_roulette = patch('app.services.game_service.RouletteService', self.mock_roulette_class)
        self.patcher_gacha = patch('app.services.game_service.GachaService', self.mock_gacha_class)
        
        self.patcher_slot.start()
        self.patcher_roulette.start()
        self.patcher_gacha.start()
        
        # 서비스 객체 생성
        self.service = GameService(repository=self.mock_repo)
    
    def tearDown(self):
        """테스트 후 정리."""
        self.patcher_slot.stop()
        self.patcher_roulette.stop()
        self.patcher_gacha.stop()

    def test_initialization(self):
        """올바른 초기화 테스트."""
        # 초기화 검증
        self.assertEqual(self.service.repo, self.mock_repo)
        self.assertIsInstance(self.service.slot_service, MagicMock)
        self.assertIsInstance(self.service.roulette_service, MagicMock)
        self.assertIsInstance(self.service.gacha_service, MagicMock)
        
        # 각 서비스가 올바른 저장소로 초기화되었는지 검증
        self.mock_slot_class.assert_called_once_with(self.mock_repo)
        self.mock_roulette_class.assert_called_once_with(self.mock_repo)
        self.mock_gacha_class.assert_called_once_with(self.mock_repo)

    def test_default_repository_initialization(self):
        """저장소 기본값 초기화 테스트."""
        with patch('app.services.game_service.GameRepository') as mock_game_repo:
            mock_repo_instance = MagicMock()
            mock_game_repo.return_value = mock_repo_instance
            
            # 저장소 없이 초기화
            service = GameService()
            
            # 기본 저장소 생성 확인
            mock_game_repo.assert_called_once()
            self.assertEqual(service.repo, mock_repo_instance)

    def test_slot_spin_delegation(self):
        """슬롯 스핀 위임 테스트."""
        # 모의 결과 설정
        mock_result = MagicMock(spec=SlotSpinResult)
        self.mock_slot_service.spin.return_value = mock_result
        
        # 메서드 호출
        result = self.service.slot_spin(user_id=123, db=self.mock_db)
        
        # 위임 검증
        self.mock_slot_service.spin.assert_called_once_with(123, self.mock_db)
        self.assertEqual(result, mock_result)

    def test_roulette_spin_delegation(self):
        """룰렛 스핀 위임 테스트."""
        # 모의 결과 설정
        mock_result = MagicMock(spec=RouletteSpinResult)
        self.mock_roulette_service.spin.return_value = mock_result
        
        # 메서드 호출
        result = self.service.roulette_spin(
            user_id=123, 
            bet=10, 
            bet_type="color", 
            value="red", 
            db=self.mock_db
        )
        
        # 위임 검증
        self.mock_roulette_service.spin.assert_called_once_with(
            123, 10, "color", "red", self.mock_db
        )
        self.assertEqual(result, mock_result)

    def test_gacha_pull_delegation(self):
        """가챠 풀 위임 테스트."""
        # 모의 결과 설정
        mock_result = MagicMock(spec=GachaPullResult)
        self.mock_gacha_service.pull.return_value = mock_result
        
        # 메서드 호출
        result = self.service.gacha_pull(user_id=123, count=5, db=self.mock_db)
        
        # 위임 검증
        self.mock_gacha_service.pull.assert_called_once_with(123, 5, self.mock_db)
        self.assertEqual(result, mock_result)

    def test_delegation_with_exception(self):
        """예외 발생 시 위임 테스트."""
        # 예외 발생하도록 설정
        self.mock_slot_service.spin.side_effect = ValueError("테스트 예외")
        
        # 예외가 제대로 전파되는지 검증
        with self.assertRaises(ValueError):
            self.service.slot_spin(user_id=123, db=self.mock_db)
        
        # 호출 확인
        self.mock_slot_service.spin.assert_called_once_with(123, self.mock_db)


@pytest.fixture
def game_service_with_mocks():
    """모의 객체가 설정된 게임 서비스 픽스처."""
    # 서비스 모킹
    mock_repo = MagicMock(spec=GameRepository)
    mock_slot = MagicMock(spec=SlotService)
    mock_roulette = MagicMock(spec=RouletteService)
    mock_gacha = MagicMock(spec=GachaService)
    
    with patch.multiple(
        'app.services.game_service',
        SlotService=MagicMock(return_value=mock_slot),
        RouletteService=MagicMock(return_value=mock_roulette),
        GachaService=MagicMock(return_value=mock_gacha)
    ):
        service = GameService(repository=mock_repo)
        return service, mock_repo, mock_slot, mock_roulette, mock_gacha


def test_integration_flow(game_service_with_mocks):
    """통합 흐름 테스트."""
    service, repo, slot, roulette, gacha = game_service_with_mocks
    mock_db = MagicMock(spec=Session)
    
    # 슬롯 테스트
    mock_slot_result = MagicMock(spec=SlotSpinResult)
    slot.spin.return_value = mock_slot_result
    
    assert service.slot_spin(123, mock_db) == mock_slot_result
    
    # 룰렛 테스트
    mock_roulette_result = MagicMock(spec=RouletteSpinResult)
    roulette.spin.return_value = mock_roulette_result
    
    assert service.roulette_spin(123, 10, "color", "red", mock_db) == mock_roulette_result
    
    # 가챠 테스트
    mock_gacha_result = MagicMock(spec=GachaPullResult)
    gacha.pull.return_value = mock_gacha_result
    
    assert service.gacha_pull(123, 5, mock_db) == mock_gacha_result


def test_duplicate_init_ignored(game_service_with_mocks):
    """중복된 __init__ 메서드 무시 테스트."""
    service, repo, *_ = game_service_with_mocks
    
    # 코드 내에 중복된 __init__ 메서드가 있으므로, 잘못된 사용이 발생하지 않는지 확인
    # 슬롯 서비스가 제대로 초기화되었는지 확인
    assert hasattr(service, 'slot_service')
    assert hasattr(service, 'roulette_service')
    assert hasattr(service, 'gacha_service')


def test_old_code_not_executed():
    """기존 미사용 코드가 실행되지 않는지 테스트."""
    # 초기화 시 실제로 사용되는 코드만 실행되는지 확인
    with patch('app.services.game_service.SlotService') as mock_slot_service:
        with patch('app.services.game_service.RouletteService') as mock_roulette_service:
            with patch('app.services.game_service.GachaService') as mock_gacha_service:
                # 잘못된 코드가 실행되지 않는지 확인
                # 서비스 인스턴스 생성
                service = GameService()
                
                # 실제 사용되는 메서드 호출
                mock_db = MagicMock()
                
                # 슬롯 서비스에 예외를 발생시키는 mock 설정
                service.slot_service.spin.side_effect = Exception("임시 예외")
                
                # 이 호출이 slot_service.spin()으로 직접 위임되는지 확인 
                with pytest.raises(Exception, match="임시 예외"):
                    service.slot_spin(123, mock_db)
                    
                # 올바른 위임이 이루어졌는지 확인
                service.slot_service.spin.assert_called_once_with(123, mock_db)
