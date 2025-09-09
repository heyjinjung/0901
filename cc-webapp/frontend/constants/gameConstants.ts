import { 
  Dice1,
  Swords,
  Gift,
  Zap
} from 'lucide-react';
import { GameDashboardGame, User } from '../types';

// 🎮 게임 목록 데이터
export const createGamesData = (user: User): GameDashboardGame[] => [
  {
    id: 'slot',
    name: '모델 포인트슬롯',
    type: 'slot',
    icon: Dice1,
    color: 'from-primary to-primary-light',
    description: '잭팟의 짜릿함! 모델회원 전용 슬롯서비스',
    // 전역 selector(useGameTileStats) 사용 권장. 여기서는 레거시 직참조 제거.
    playCount: 0,
    bestScore: 0,
    lastPlayed: new Date(),
    difficulty: 'Easy',
    rewards: ['골드', '경험치', '특별 스킨'],

    trending: true,
    cost: 100
  },
  {
    id: 'rps',
    name: '가위바위보',
    type: 'rps',
    icon: Swords,
    color: 'from-success to-info',
    description: 'AI와 두뇌 대결! 승부의 짜릿함!',
    // 전역 selector(useGameTileStats) 사용 권장. 레거시 직참조 제거.
    playCount: 0,
    bestScore: 0,
    lastPlayed: new Date(),
    difficulty: 'Medium',
    rewards: ['골드', '전략 포인트', '승부사 배지'],

    trending: false,
    cost: 50
  },
  {
    id: 'gacha',
    name: '랜덤뽑기',
    type: 'gacha',
    icon: Gift,
    color: 'from-error to-warning',
    description: '엄청난 아이템혜택! 지금 바로 도전하세요!',
    // 전역 selector(useGameTileStats) 사용 권장. 레거시 직참조 제거.
    playCount: 0,
    bestScore: 0,
    lastPlayed: new Date(),
    difficulty: 'Extreme',
    rewards: ['전설 아이템', '희귀 스킨', '특별 캐릭터'],

    trending: true,
    cost: 500
  },
  {
    id: 'crash',
    name: '모델 그래프',
    type: 'crash',
    icon: Zap,
    color: 'from-error to-primary',
    description: '배율 상승의 스릴! 언제 터질까?',
    // 전역 selector(useGameTileStats) 사용 권장. 레거시 직참조 제거.
    playCount: 0,
    bestScore: 0,
    lastPlayed: new Date(),
    difficulty: 'Hard',
    rewards: ['고배율 골드', '크래시 배지', '스릴 포인트'],

    trending: true,
    cost: 100
  }
];

// 🎯 리더보드 더미 데이터
export const createLeaderboardData = (user: User) => [
  { id: 'leader-1', rank: 1, name: '네온킹', score: 98765, badge: '💎' },
  { id: 'leader-2', rank: 2, name: '크래시마스터', score: 87654, badge: '🏆' },
  { id: 'leader-3', rank: 3, name: '슬롯황제', score: 76543, badge: '👑' },
  { id: 'leader-4', rank: 4, name: user.nickname, score: 65432, badge: '🌟' },
  { id: 'leader-5', rank: 5, name: '럭키세븐', score: 54321, badge: '🎰' },
  { id: 'leader-6', rank: 6, name: '가챠신', score: 43210, badge: '🎁' }
];