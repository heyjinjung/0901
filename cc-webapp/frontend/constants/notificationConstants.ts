// 📱 알림 시스템 상수

// 🎯 VIP 알림 필터링 키워드
export const VIP_NOTIFICATION_KEYWORDS = [
  'JACKPOT',
  'BIG WIN', 
  '레벨업',
  '회원가입',
  '로그인',
  '일일',
  '관리자',
  '로그아웃',
  '에러',
  '실패',
  '크래시'
] as const;

// ⏱️ 알림 시스템 설정
export const NOTIFICATION_CONFIG = {
  DURATION: 7000,
  MAX_COUNT: 4,
  ANIMATION_DELAY: 100
} as const;

// 🎨 알림 스타일 클래스
export const NOTIFICATION_STYLES = {
  CONTAINER: "fixed top-4 right-4 z-50 space-y-2",
  ITEM: "glass-effect text-white px-4 py-3 rounded-lg shadow-game max-w-sm text-sm border border-primary/20",
  ANIMATION: {
    INITIAL: { opacity: 0, x: 100, scale: 0.8 },
    ANIMATE: { opacity: 1, x: 0, scale: 1 },
    EXIT: { opacity: 0, x: 100, scale: 0.8 }
  }
} as const;