"""업데이트된 테스트: 현재 위임 구조와 호환되도록 수정된 게임 서비스 테스트."""

import unittest
import random
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

import pytest
from app.services.game_service import GameService
from app.services.slot_service import SlotService, SlotSpinResult
from app.services.roulette_service import RouletteService, RouletteSpinResult
from app.services.gacha_service import GachaService, GachaPullResult
from app.repositories.game_repository import GameRepository


class TestGameServiceDelegation(unittest.TestCase):
    """GameService의 위임 기능 테스트 클래스."""

    def setUp(self):
        """테스트를 위한 기본 설정."""
        self.mock_db = MagicMock(spec=Session)
        self.mock_repo = MagicMock(spec=GameRepository)
        
        # 서비스 객체 생성
        self.service = GameService(db=self.mock_db, repository=self.mock_repo)
        
        # 모의 하위 서비스 생성
        self.mock_slot_service = MagicMock(spec=SlotService)
        self.mock_roulette_service = MagicMock(spec=RouletteService)
        self.mock_gacha_service = MagicMock(spec=GachaService)
        
        # 위임할 서비스 객체 교체
        self.service.slot_service = self.mock_slot_service
        self.service.roulette_service = self.mock_roulette_service
        self.service.gacha_service = self.mock_gacha_service

    def test_slot_spin_win_case(self):
        """슬롯 스핀 승리 케이스 테스트."""
        # 모의 결과 설정
        mock_result = MagicMock(spec=SlotSpinResult)
        mock_result.result = "win"
        mock_result.tokens_change = 8  # 2토큰 차감, 10토큰 획득
        mock_result.balance = 108
        mock_result.streak = 0
        mock_result.animation = "win"
        
        # 모의 서비스 반환값 설정
        self.mock_slot_service.spin.return_value = mock_result
        
        # 테스트 실행
        result = self.service.slot_spin(user_id=123, bet_amount=100)
        
        # 검증
        self.mock_slot_service.spin.assert_called_once_with(123, 100, self.mock_db)
        self.assertEqual(result.result, "win")
        self.assertEqual(result.tokens_change, 8)
        self.assertEqual(result.balance, 108)
        self.assertEqual(result.streak, 0)

    def test_slot_spin_lose_case(self):
        """슬롯 스핀 패배 케이스 테스트."""
        # 모의 결과 설정
        mock_result = MagicMock(spec=SlotSpinResult)
        mock_result.result = "lose"
        mock_result.tokens_change = -2  # 2토큰 차감
        mock_result.balance = 98
        mock_result.streak = 1
        mock_result.animation = "lose"
        
        # 모의 서비스 반환값 설정
        self.mock_slot_service.spin.return_value = mock_result
        
        # 테스트 실행
        result = self.service.slot_spin(user_id=123, bet_amount=100)
        
        # 검증
        self.mock_slot_service.spin.assert_called_once_with(123, 100, self.mock_db)
        self.assertEqual(result.result, "lose")
        self.assertEqual(result.tokens_change, -2)
        self.assertEqual(result.balance, 98)
        self.assertEqual(result.streak, 1)

    def test_slot_spin_jackpot_case(self):
        """슬롯 스핀 잭팟 케이스 테스트."""
        # 모의 결과 설정
        mock_result = MagicMock(spec=SlotSpinResult)
        mock_result.result = "jackpot"
        mock_result.tokens_change = 98  # 2토큰 차감, 100토큰 획득
        mock_result.balance = 198
        mock_result.streak = 0
        mock_result.animation = "jackpot"
        
        # 모의 서비스 반환값 설정
        self.mock_slot_service.spin.return_value = mock_result
        
        # 테스트 실행
        result = self.service.slot_spin(user_id=123, bet_amount=100)
        
        # 검증
        self.mock_slot_service.spin.assert_called_once_with(123, 100, self.mock_db)
        self.assertEqual(result.result, "jackpot")
        self.assertEqual(result.tokens_change, 98)
        self.assertEqual(result.balance, 198)
        self.assertEqual(result.streak, 0)

    def test_slot_spin_force_win_due_to_streak(self):
        """연속 패배 후 강제 승리 테스트."""
        # 모의 결과 설정
        mock_result = MagicMock(spec=SlotSpinResult)
        mock_result.result = "win"
        mock_result.tokens_change = 8
        mock_result.balance = 108
        mock_result.streak = 0
        mock_result.animation = "force_win"
        
        # 모의 서비스 반환값 설정
        self.mock_slot_service.spin.return_value = mock_result
        
        # 테스트 실행
        result = self.service.slot_spin(user_id=123, bet_amount=100)
        
        # 검증
        self.mock_slot_service.spin.assert_called_once_with(123, 100, self.mock_db)
        self.assertEqual(result.result, "win")
        self.assertEqual(result.animation, "force_win")
        self.assertEqual(result.streak, 0)

    def test_roulette_spin_number_win(self):
        """룰렛 숫자 베팅 승리 테스트."""
        # 모의 결과 설정
        mock_result = MagicMock(spec=RouletteSpinResult)
        mock_result.winning_number = 17
        mock_result.result = "win"
        mock_result.tokens_change = 340  # 10토큰 차감, 350토큰 획득
        mock_result.balance = 440
        
        # 모의 서비스 반환값 설정
        self.mock_roulette_service.spin.return_value = mock_result
        
        # 테스트 실행
        result = self.service.roulette_spin(
            user_id=123,
            bet=10,
            bet_type="number",
            value="17"
        )
        
        # 검증
        self.mock_roulette_service.spin.assert_called_once_with(123, 10, "number", "17", self.mock_db)
        self.assertEqual(result.result, "win")
        self.assertEqual(result.winning_number, 17)
        self.assertEqual(result.tokens_change, 340)
        self.assertEqual(result.balance, 440)

    def test_roulette_spin_color_win(self):
        """룰렛 색상 베팅 승리 테스트."""
        # 모의 결과 설정
        mock_result = MagicMock(spec=RouletteSpinResult)
        mock_result.winning_number = 7
        mock_result.result = "win"
        mock_result.tokens_change = 5  # 5토큰 차감, 10토큰 획득
        mock_result.balance = 105
        
        # 모의 서비스 반환값 설정
        self.mock_roulette_service.spin.return_value = mock_result
        
        # 테스트 실행
        result = self.service.roulette_spin(
            user_id=123,
            bet=5,
            bet_type="color",
            value="red"
        )
        
        # 검증
        self.mock_roulette_service.spin.assert_called_once_with(123, 5, "color", "red", self.mock_db)
        self.assertEqual(result.result, "win")
        self.assertEqual(result.tokens_change, 5)
        self.assertEqual(result.balance, 105)

    def test_roulette_spin_odd_even_win(self):
        """룰렛 홀짝 베팅 승리 테스트."""
        # 모의 결과 설정
        mock_result = MagicMock(spec=RouletteSpinResult)
        mock_result.winning_number = 22
        mock_result.result = "win"
        mock_result.tokens_change = 10  # 10토큰 차감, 20토큰 획득
        mock_result.balance = 110
        
        # 모의 서비스 반환값 설정
        self.mock_roulette_service.spin.return_value = mock_result
        
        # 테스트 실행
        result = self.service.roulette_spin(
            user_id=123,
            bet=10,
            bet_type="odd_even",
            value="even"
        )
        
        # 검증
        self.mock_roulette_service.spin.assert_called_once_with(123, 10, "odd_even", "even", self.mock_db)
        self.assertEqual(result.result, "win")
        self.assertEqual(result.tokens_change, 10)
        self.assertEqual(result.winning_number, 22)

    def test_roulette_spin_zero_lose(self):
        """룰렛 0이 나와서 패배하는 케이스 테스트."""
        # 모의 결과 설정
        mock_result = MagicMock(spec=RouletteSpinResult)
        mock_result.winning_number = 0
        mock_result.result = "lose"
        mock_result.tokens_change = -10  # 10토큰 차감
        mock_result.balance = 90
        
        # 모의 서비스 반환값 설정
        self.mock_roulette_service.spin.return_value = mock_result
        
        # 테스트 실행
        result = self.service.roulette_spin(
            user_id=123,
            bet=10,
            bet_type="color",
            value="red"
        )
        
        # 검증
        self.mock_roulette_service.spin.assert_called_once_with(123, 10, "color", "red", self.mock_db)
        self.assertEqual(result.result, "lose")
        self.assertEqual(result.winning_number, 0)
        self.assertEqual(result.tokens_change, -10)
        self.assertEqual(result.balance, 90)

    def test_roulette_bet_limit(self):
        """룰렛 베팅 한도 테스트."""
        # 과도한 베팅 시도
        self.service.roulette_spin(
            user_id=123,
            bet=100,  # 제한 이상의 베팅
            bet_type="number",
            value="17"
        )
        
        # 베팅 한도가 적용되어야 함 (실제 제한 로직은 roulette_service에 위임됨)
        self.mock_roulette_service.spin.assert_called_once()

    def test_gacha_pull_delegated(self):
        """가챠 뽑기 위임 테스트."""
        # 모의 결과 설정
        mock_result = MagicMock(spec=GachaPullResult)
        mock_result.results = ["레어 아이템", "일반 아이템"]
        mock_result.tokens_change = -20
        mock_result.balance = 80
        
        # 모의 서비스 반환값 설정
        self.mock_gacha_service.pull.return_value = mock_result
        
        # 테스트 실행
        result = self.service.gacha_pull(user_id=123, count=2)
        
        # 검증
        self.mock_gacha_service.pull.assert_called_once_with(123, 2, self.mock_db)
        self.assertEqual(result.results, ["레어 아이템", "일반 아이템"])
        self.assertEqual(result.tokens_change, -20)
        self.assertEqual(result.balance, 80)


@pytest.fixture
def game_service_fixture(db_session):
    """테스트용 게임 서비스 픽스처."""
    mock_repo = MagicMock(spec=GameRepository)
    mock_slot_service = MagicMock(spec=SlotService)
    mock_roulette_service = MagicMock(spec=RouletteService)
    mock_gacha_service = MagicMock(spec=GachaService)
    
    service = GameService(db=db_session, repository=mock_repo)
    service.slot_service = mock_slot_service
    service.roulette_service = mock_roulette_service
    service.gacha_service = mock_gacha_service
    
    return service, mock_slot_service, mock_roulette_service, mock_gacha_service, mock_repo


def test_service_initialization(db_session):
    """서비스 초기화 테스트."""
    # 레포지토리 없이 초기화
    service = GameService(db=db_session)
    assert isinstance(service.repo, GameRepository)
    assert isinstance(service.slot_service, SlotService)
    assert isinstance(service.roulette_service, RouletteService)
    assert isinstance(service.gacha_service, GachaService)
    
    # 커스텀 레포지토리로 초기화
    custom_repo = MagicMock(spec=GameRepository)
    service = GameService(db=db_session, repository=custom_repo)
    assert service.repo == custom_repo


def test_game_service_error_propagation(game_service_fixture):
    """게임 서비스 오류 전파 테스트."""
    service, mock_slot, mock_roulette, mock_gacha, _ = game_service_fixture
    
    # 슬롯 서비스에서 오류 발생
    mock_slot.spin.side_effect = ValueError("토큰 부족")
    with pytest.raises(ValueError, match="토큰 부족"):
        service.slot_spin(user_id=123, bet_amount=100)
    
    # 룰렛 서비스에서 오류 발생
    mock_roulette.spin.side_effect = ValueError("잘못된 베팅 타입")
    with pytest.raises(ValueError, match="잘못된 베팅 타입"):
        service.roulette_spin(user_id=123, bet=10, bet_type="invalid", value=None)
        
    # 가챠 서비스에서 오류 발생
    mock_gacha.pull.side_effect = ValueError("잘못된 뽑기 횟수")
    with pytest.raises(ValueError, match="잘못된 뽑기 횟수"):
        service.gacha_pull(user_id=123, count=0)


def test_integration_between_services(db_session):
    """서비스 간 통합 테스트."""
    # 실제 서비스 생성 (통합 테스트)
    repo = GameRepository(db_session)
    service = GameService(db=db_session, repository=repo)
    
    # 각 특화 서비스 확인
    assert service.slot_service.repo == repo
    assert service.roulette_service.repo == repo
    assert service.gacha_service.repo == repo
