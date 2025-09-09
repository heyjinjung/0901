import { GachaItem, GachaBanner } from '../../../types/gacha';

// 가챠 애니메이션 상수
export const ANIMATION_DURATIONS = {
  fadeIn: 0.3,
  pulse: 1.5,
  hover: 0.2,
  spin: 2,
  sparkle: 2,
  stagger: 0.1,
  baseDelay: 0.2
};

// 희귀도별 색상
export const RARITY_COLORS = {
  common: '#a1a1aa',    // 회색
  rare: '#60a5fa',      // 파랑
  epic: '#c084fc',      // 보라
  legendary: '#facc15', // 노랑
  mythic: '#f472b6'     // 핑크
};

// 섹시 이모지 모음
export const SEXY_EMOJIS = ['💋', '💖', '👄', '💅', '💕', '💘', '💗', '💓', '👙', '💃', '👠', '✨'];

// 가챠 아이템 목록
export const GACHA_ITEMS: GachaItem[] = [
  { id: 'glitter_lip', name: '반짝 립글로스', type: 'skin', rarity: 'common', rate: 15, quantity: 1, description: '눈부신 글리터가 가득한 섹시 립글로스', icon: '💋', value: 100, sexiness: 2 },
  { id: 'neon_nail', name: '네온 네일', type: 'skin', rarity: 'common', rate: 15, quantity: 1, description: '형광색으로 빛나는 네일아트', icon: '💅', value: 80, sexiness: 2 },
  { id: 'cute_sticker', name: '귀여운 스티커팩', type: 'collectible', rarity: 'common', rate: 15, quantity: 5, description: '초키치한 하트와 별 스티커들', icon: '🌟', value: 50, sexiness: 1 },
  { id: 'pink_coin', name: '핑크 코인백', type: 'currency', rarity: 'common', rate: 15, quantity: 500, description: '분홍빛 반짝이는 골드 코인들', icon: '💖', value: 500, sexiness: 1 },
  { id: 'lace_lingerie', name: '레이스 란제리', type: 'skin', rarity: 'rare', rate: 8, quantity: 1, description: '고급스러운 블랙 레이스 란제리 세트', icon: '🖤', value: 1000, sexiness: 4 },
  { id: 'diamond_choker', name: '다이아 초커', type: 'skin', rarity: 'rare', rate: 8, quantity: 1, description: '목을 감싸는 화려한 다이아몬드 초커', icon: '💎', value: 1200, sexiness: 4 },
  { id: 'silk_dress', name: '실크 드레스', type: 'skin', rarity: 'rare', rate: 9, quantity: 1, description: '몸매를 돋보이게 하는 실크 원피스', icon: '👗', value: 1500, sexiness: 3 },
  { id: 'angel_wings', name: '엔젤 윙', type: 'skin', rarity: 'epic', rate: 4, quantity: 1, description: '천사 같지만 악마 같은 화이트 윙', icon: '🤍', value: 5000, sexiness: 5 },
  { id: 'devil_horns', name: '데빌 혼', type: 'skin', rarity: 'epic', rate: 4, quantity: 1, description: '치명적인 매력의 붉은 뿔 헤드피스', icon: '😈', value: 5500, sexiness: 5 },
  { id: 'crystal_heels', name: '크리스탈 힐', type: 'skin', rarity: 'epic', rate: 4, quantity: 1, description: '신데렐라도 울고 갈 투명 하이힐', icon: '👠', value: 4000, sexiness: 4 },
  { id: 'goddess_crown', name: '여신의 왕관', type: 'skin', rarity: 'legendary', rate: 1, quantity: 1, description: '아프로디테가 착용했다는 전설의 왕관', icon: '👑', value: 20000, sexiness: 5 },
  { id: 'mermaid_tail', name: '인어 꼬리', type: 'skin', rarity: 'legendary', rate: 0.8, quantity: 1, description: '심해의 여왕이 내려준 신비한 꼬리', icon: '🧜‍♀️', value: 18000, sexiness: 5 },
  { id: 'phoenix_feather', name: '불사조 깃털 드레스', type: 'skin', rarity: 'legendary', rate: 0.7, quantity: 1, description: '영원히 타오르는 아름다움의 상징', icon: '🔥', value: 25000, sexiness: 5 },
  { id: 'galaxy_body', name: '갤럭시 바디슈트', type: 'skin', rarity: 'mythic', rate: 0.3, quantity: 1, description: '우주의 별빛을 담은 몸에 밀착되는 슈트', icon: '🌌', value: 100000, sexiness: 5 },
  { id: 'rainbow_aura', name: '레인보우 오라', type: 'collectible', rarity: 'mythic', rate: 0.2, quantity: 1, description: '몸 전체를 감싸는 무지개빛 오라', icon: '🌈', value: 150000, sexiness: 5 }
];

// 가챠 배너 목록
export const GACHA_BANNERS: GachaBanner[] = [
  {
    id: 'standard',
    name: '스탠다드 가챠',
    description: '일반적인 아이템을 얻을 수 있는 가챠입니다.',
    cost: 1000,
    price: 1000,
    image: '/images/gacha/standard-banner.jpg',
    theme: '기본 컬렉션',
    bonusMultiplier: 1.0,
    bgGradient: 'from-pink-400 to-pink-600',
    featuredItems: GACHA_ITEMS.filter(item => item.rarity !== 'mythic')
  },
  {
    id: 'premium',
    name: '프리미엄 가챠',
    description: '에픽 등급 이상 아이템 확률 증가!',
    cost: 2000,
    price: 2000,
    image: '/images/gacha/premium-banner.jpg',
    theme: '럭셔리 컬렉션',
    guaranteedRarity: 'epic',
    bonusMultiplier: 1.5,
    bgGradient: 'from-purple-600 to-pink-600',
    featuredItems: GACHA_ITEMS.filter(item => item.rarity !== 'common')
  },
  {
    id: 'limited',
    name: '리미티드 가챠',
    description: '레전더리 등급 이상 확정!',
    cost: 5000,
    price: 5000,
    image: '/images/gacha/limited-banner.jpg',
    theme: '익스클루시브 컬렉션',
    guaranteedRarity: 'legendary',
    bonusMultiplier: 2.0,
    bgGradient: 'from-red-500 to-yellow-400',
    featuredItems: GACHA_ITEMS.filter(item => item.rarity === 'legendary' || item.rarity === 'mythic')
  }
];