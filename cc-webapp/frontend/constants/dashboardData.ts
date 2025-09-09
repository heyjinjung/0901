import { 
  Gamepad2, 
  ShoppingBag, 
  Play, 
  Trophy 
} from 'lucide-react';

export const QUICK_ACTIONS = [
  {
    title: '게임 플레이',
    description: '4가지 중독성 게임!',
    icon: Gamepad2,
    color: 'from-primary to-primary-light',
    highlight: true,
    badge: 'HOT'
  },
  {
    title: '상점',
    description: '스킨 & 아이템',
    icon: ShoppingBag,
    color: 'from-gold to-gold-light',
    highlight: false
  },
  {
    title: '방송보기',
    description: '실시간 게임 방송',
    icon: Play,
    color: 'from-success to-info',
    highlight: false,
    badge: 'LIVE'
  },
  {
    title: '랭킹',
    description: '전체 순위 확인',
    icon: Trophy,
    color: 'from-warning to-error',
    highlight: false
  }
];

export const ACHIEVEMENTS_DATA = [
  { id: 'first_login', name: '첫 로그인', icon: '🎯' },
  { id: 'level_5', name: '5레벨 달성', icon: '⭐' },
  { id: 'win_10', name: '10승 달성', icon: '🏆' },
  { id: 'treasure_hunt', name: '보물 사냥꾼', icon: '💎' },
  { id: 'gold_100k', name: '10만골드', icon: '💰' },
  { id: 'daily_7', name: '7일 연속', icon: '📅' }
];