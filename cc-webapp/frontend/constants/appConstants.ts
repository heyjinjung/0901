// 🎯 앱 전체 상수 관리
export const APP_CONFIG = {
  GAME_TITLE: 'NEON QUEST',
  NOTIFICATION_DURATION: 7000,
  MAX_NOTIFICATIONS: 4,
  
  // 로딩 시간
  LOGIN_DELAY: 2000,
  SIGNUP_DELAY: 2500,
  ADMIN_LOGIN_DELAY: 1500,
} as const;

// 🔐 관리자 계정 정보
export const ADMIN_ACCOUNTS = [
  { id: 'md001', password: '123456' },
  { id: 'admin', password: '123456' }
] as const;

export const ADMIN_SECURITY_CODE = '123456';

// 🎮 게임 기본 설정
export const GAME_DEFAULTS = {
  BASIC_GOLD: 10000,
  ADMIN_GOLD: 999999,
  ADMIN_LEVEL: 99,
  SIGNUP_BONUS: 15000,
  INVITE_BONUS: 25000,
  
  // 경험치 시스템
  BASE_MAX_EXP: 1000,
  
  // 랜덤 범위
  RANDOM_GOLD_RANGE: 50000,
  RANDOM_LEVEL_RANGE: 20,
  RANDOM_EXP_RANGE: 1000,
  RANDOM_STREAK_RANGE: 10,
  RANDOM_GAMES_RANGE: 100,
  RANDOM_WINS_RANGE: 50,
  RANDOM_SCORE_RANGE: 10000,
  RANDOM_EARNINGS_RANGE: 100000,
  RANDOM_WIN_STREAK_RANGE: 10,
  RANDOM_PLAYTIME_RANGE: 100
} as const;

// 🏠 하단 네비게이션이 있는 화면들
export const SCREENS_WITH_BOTTOM_NAV = [
  'home-dashboard', 
  'game-dashboard', 
  'shop', 
  'inventory', 
  'profile'
] as const;

// 🎁 기본 아이템들
export const DEFAULT_ITEMS = {
  BEGINNER: {
    id: '1',
    name: '초보자 스킨',
    type: 'skin',
    rarity: 'common',
    quantity: 1,
    description: '새로운 플레이어를 위한 기본 스킨',
    icon: '🎭'
  },
  NEWCOMER: {
    id: '1',
    name: '신규 가입 기념 스킨',
    type: 'skin',
    rarity: 'rare',
    quantity: 1,
    description: '새로운 모험가를 환영하는 특별한 스킨',
    icon: '✨'
  }
} as const;

// 📱 알림 메시지 템플릿 - 🎯 VIP 알림만!
export const NOTIFICATION_MESSAGES = {
  // 🔥 VIP 로그인 알림
  LOGIN_SUCCESS: (nickname: string, isAdmin: boolean) => 
    `🎉 환영합니다, ${nickname}님! ${isAdmin ? '🔐 관리자 권한이 활성화되었습니다.' : ''}`,
  
  // 🎊 회원가입 보너스 알림
  SIGNUP_SUCCESS: (goldAmount: number) => 
    `🎊 회원가입 완료! 신규 회원 보너스 ${goldAmount.toLocaleString()}G 지급!`,
  
  // 🎁 일일 보너스 알림 (중요)
  DAILY_BONUS: (bonusGold: number, streak: number) => 
    `🎁 일일 로그인 보너스 ${bonusGold.toLocaleString()}G 획득! (연속 ${streak}일)`,
  
  // 🔐 관리자 로그인
  ADMIN_LOGIN_SUCCESS: '🔐 관리자 로그인 성공! 사이드 메뉴에서 관리자 패널에 접근할 수 있습니다.',
  
  // 👋 로그아웃
  LOGOUT_SUCCESS: '👋 안전하게 로그아웃되었습니다. 다음에 또 만나요!',

  // 🎰 잭팟 & 빅윈 (게임에서 큰 승리만)
  SLOT_JACKPOT: (amount: number) => `🎰 JACKPOT! ${amount.toLocaleString()}G 획득!`,
  SLOT_BIGWIN: (amount: number) => `🔥 BIG WIN! ${amount.toLocaleString()}G 획득!`,
  
  // 🎉 대형 승리 (200G 이상)
  RPS_BIGWIN: (amount: number, multiplier: number) => 
    `🎉 대승! +${amount.toLocaleString()}G${multiplier > 1 ? ` (${multiplier.toFixed(1)}x 콤보!)` : ''}`,
  
  // 🎯 룰렛 대형 승리
  ROULETTE_BIGWIN: (amount: number) => `🎯 룰렛 대승! ${amount.toLocaleString()}G 획득!`,
  
  // 🎁 가챠 레어 아이템
  GACHA_RARE: (itemName: string, rarity: string) => 
    `🎁 ${rarity.toUpperCase()} 아이템 획득! "${itemName}"`,

  // ⬆️ 레벨업 알림
  LEVEL_UP: (newLevel: number) => `⬆️ 레벨업! Lv.${newLevel} 달성!`,

  // ❌ 에러 메시지 (중요한 것만)
  INSUFFICIENT_GOLD: '❌ 골드가 부족합니다!',
  PURCHASE_FAILED: '❌ 구매에 실패했습니다. 다시 시도해주세요.',
  
  // ✅ 중요한 성공 메시지만
  PURCHASE_SUCCESS: (itemName: string) => `🛍️ "${itemName}" 구매 완료!`
} as const;

// 🎯 새로운 중독성 게임 아이디어
export const NEW_GAME_IDEAS = [
  {
    id: 'neon-crash',
    name: '네온 크래시',
    description: '배율이 상승하다가 언제 크래시될지 모르는 스릴 넘치는 게임',
    icon: '🚀',
    addiction: '극강',
    mechanics: '실시간 배율 상승, 언제든 캐시아웃 가능'
  },
  {
    id: 'color-match-rush',
    name: '컬러 매치 러시',
    description: '빠른 반응으로 색깔을 맞추는 중독성 게임',
    icon: '🌈',
    addiction: '높음',
    mechanics: '점점 빨라지는 속도, 콤보 시스템'
  },
  {
    id: 'gold-rush-timing',
    name: '골드 러시',
    description: '완벽한 타이밍으로 골드를 수집하는 게임',
    icon: '⏰',
    addiction: '높음',
    mechanics: '타이밍 기반, 멀티플라이어'
  },
  {
    id: 'neon-scratch',
    name: '네온 스크래치',
    description: '긁어서 상품을 찾는 즉석 복권 게임',
    icon: '🎫',
    addiction: '중간',
    mechanics: '즉석 결과, 다양한 상품'
  }
] as const;