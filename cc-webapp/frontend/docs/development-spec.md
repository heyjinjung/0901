# CJ AI Dashboard - 개발용 스펙 문서

## 📋 목차
1. [CSS Variables 목록](#css-variables-목록)
2. [애니메이션 타이밍 함수](#애니메이션-타이밍-함수)
3. [반응형 브레이크포인트](#반응형-브레이크포인트)
4. [컴포넌트 Props 정의](#컴포넌트-props-정의)
5. [상태 전환 다이어그램](#상태-전환-다이어그램)
6. [디자인 시스템](#디자인-시스템)
7. [개발 가이드라인](#개발-가이드라인)

---

## 🎨 CSS Variables 목록

### 기본 색상 토큰
```css
/* Light Theme */
:root {
  /* 기본 배경 및 텍스트 */
  --background: #ffffff;
  --foreground: oklch(0.145 0 0);
  
  /* 카드 및 컨테이너 */
  --card: #ffffff;
  --card-foreground: oklch(0.145 0 0);
  
  /* 팝오버 */
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0 0);
  
  /* 주요 컬러 */
  --primary: #030213;
  --primary-foreground: oklch(1 0 0);
  
  /* 보조 컬러 */
  --secondary: oklch(0.95 0.0058 264.53);
  --secondary-foreground: #030213;
  
  /* 음소거 컬러 */
  --muted: #ececf0;
  --muted-foreground: #717182;
  
  /* 액센트 컬러 */
  --accent: #e9ebef;
  --accent-foreground: #030213;
  
  /* 위험 컬러 */
  --destructive: #d4183d;
  --destructive-foreground: #ffffff;
  
  /* 테두리 및 입력 */
  --border: rgba(0, 0, 0, 0.1);
  --input: transparent;
  --input-background: #f3f3f5;
  --switch-background: #cbced4;
  
  /* 링 및 포커스 */
  --ring: oklch(0.708 0 0);
  
  /* 반지름 */
  --radius: 0.625rem;
}

/* Dark Theme */
.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --card: oklch(0.145 0 0);
  --card-foreground: oklch(0.985 0 0);
  --popover: oklch(0.145 0 0);
  --popover-foreground: oklch(0.985 0 0);
  --primary: oklch(0.985 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --secondary: oklch(0.269 0 0);
  --secondary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --accent: oklch(0.269 0 0);
  --accent-foreground: oklch(0.985 0 0);
  --destructive: oklch(0.396 0.141 25.723);
  --destructive-foreground: oklch(0.637 0.237 25.331);
  --border: oklch(0.269 0 0);
  --input: oklch(0.269 0 0);
  --ring: oklch(0.439 0 0);
}
```

### 커스텀 컴포넌트 색상
```css
/* Token Balance Widget */
--token-normal: #10b981;     /* emerald-500 */
--token-warning: #f59e0b;    /* amber-500 */
--token-critical: #ef4444;   /* red-500 */

/* CJ AI Avatar Moods */
--avatar-normal: linear-gradient(to bottom right, #3b82f6, #8b5cf6);
--avatar-happy: linear-gradient(to bottom right, #10b981, #06b6d4);
--avatar-sad: linear-gradient(to bottom right, #60a5fa, #6366f1);
--avatar-angry: linear-gradient(to bottom right, #f87171, #fb923c);

/* Chat Bubble */
--bubble-background: #2d2d2d;
--bubble-border: rgba(148, 163, 184, 0.5);
--bubble-tail: #2d2d2d;
```

### 타이포그래피 토큰
```css
/* Font Weights */
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;

/* Font Sizes */
--font-size: 14px;
--text-xs: 0.75rem;
--text-sm: 0.875rem;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.25rem;
--text-2xl: 1.5rem;
--text-3xl: 1.875rem;
--text-4xl: 2.25rem;
--text-5xl: 3rem;
```

---

## ⚡ 애니메이션 타이밍 함수

### Framer Motion 설정
```typescript
// 기본 애니메이션 설정
export const animations = {
  // 페이드 인/아웃
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: { duration: 0.3 }
  },
  
  // 슬라이드 업
  slideUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: { duration: 0.5, type: "spring", stiffness: 100 }
  },
  
  // 스케일 애니메이션
  scale: {
    initial: { scale: 0.8, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
    exit: { scale: 0.8, opacity: 0 },
    transition: { duration: 0.4, type: "spring", stiffness: 150 }
  },
  
  // 호버 효과
  hover: {
    whileHover: { scale: 1.05 },
    whileTap: { scale: 0.95 },
    transition: { duration: 0.2 }
  },
  
  // 펄스 효과
  pulse: {
    animate: { scale: [1, 1.05, 1] },
    transition: { duration: 2, repeat: Infinity }
  },
  
  // 로테이션
  rotate: {
    animate: { rotate: 360 },
    transition: { duration: 8, repeat: Infinity, ease: "linear" }
  },
  
  // 타이핑 인디케이터
  typing: {
    animate: { opacity: [0.4, 1, 0.4] },
    transition: { duration: 1.5, repeat: Infinity }
  }
};

// 이징 함수
export const easings = {
  easeInOut: [0.4, 0, 0.2, 1],
  easeOut: [0, 0, 0.2, 1],
  easeIn: [0.4, 0, 1, 1],
  bounce: [0.68, -0.55, 0.265, 1.55],
  anticipate: [0.68, -0.55, 0.265, 1.55]
};
```

### CSS 트랜지션
```css
/* 기본 트랜지션 */
.transition-base {
  transition: all 0.2s ease-in-out;
}

.transition-colors {
  transition: color 0.2s ease-in-out, background-color 0.2s ease-in-out;
}

.transition-transform {
  transition: transform 0.2s ease-in-out;
}

.transition-shadow {
  transition: box-shadow 0.3s ease-in-out;
}

/* 커스텀 애니메이션 */
@keyframes breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 0; }
}

@keyframes rotate-slow {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

---

## 📱 반응형 브레이크포인트

### Tailwind CSS 브레이크포인트
```css
/* Mobile First 접근법 */
/* xs: 0px 이상 (기본) */
/* sm: 640px 이상 */
/* md: 768px 이상 */
/* lg: 1024px 이상 */
/* xl: 1280px 이상 */
/* 2xl: 1536px 이상 */
```

### 컴포넌트별 반응형 설정
```typescript
// TokenBalanceWidget
const responsiveClasses = {
  container: "w-full max-w-md mx-auto lg:mx-0",
  amount: "text-4xl md:text-5xl",
  description: "text-sm md:text-base"
};

// CJAIChatBubble
const chatResponsive = {
  container: "w-80 md:w-96",
  position: {
    mobile: "bottom-4 right-4",
    desktop: "bottom-4 right-4"
  }
};

// CJChatBubble
const bubbleResponsive = {
  maxWidth: "max-w-xs md:max-w-sm lg:max-w-md",
  padding: "px-3 py-2 md:px-4 md:py-3",
  avatar: "w-10 h-10 md:w-12 md:h-12"
};
```

### 반응형 유틸리티 함수
```typescript
export const useResponsive = () => {
  const [screenSize, setScreenSize] = useState<'mobile' | 'tablet' | 'desktop'>('mobile');
  
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) {
        setScreenSize('mobile');
      } else if (window.innerWidth < 1024) {
        setScreenSize('tablet');
      } else {
        setScreenSize('desktop');
      }
    };
    
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  return screenSize;
};
```

---

## 🏗️ 컴포넌트 Props 정의

### TokenBalanceWidget
```typescript
interface TokenBalanceProps {
  /** 토큰 잔고 수량 */
  amount: number;
  
  /** 토큰 상태 */
  status?: 'normal' | 'warning' | 'critical';
  
  /** 토큰 변화 방향 */
  change?: 'none' | 'increase' | 'decrease';
  
  /** 추가 CSS 클래스 */
  className?: string;
  
  /** 토큰 심볼 (옵션) */
  symbol?: string;
  
  /** 클릭 핸들러 (옵션) */
  onClick?: () => void;
  
  /** 로딩 상태 */
  isLoading?: boolean;
  
  /** 애니메이션 비활성화 */
  disableAnimation?: boolean;
}
```

### CJChatBubble
```typescript
interface CJChatBubbleProps {
  /** 표시할 메시지 */
  message: string;
  
  /** AI 상태 */
  state?: 'idle' | 'typing' | 'speaking';
  
  /** 아바타 감정 상태 */
  avatarMood?: 'normal' | 'happy' | 'sad' | 'angry';
  
  /** 음성 토글 버튼 표시 여부 */
  showVoiceToggle?: boolean;
  
  /** 음성 토글 핸들러 */
  onVoiceToggle?: () => void;
  
  /** 추가 CSS 클래스 */
  className?: string;
  
  /** 타임스탬프 표시 여부 */
  showTimestamp?: boolean;
  
  /** 커스텀 아바타 이미지 */
  avatarImage?: string;
  
  /** 메시지 최대 길이 */
  maxLength?: number;
  
  /** 지연 시간 (ms) */
  delay?: number;
}
```

### CJAIChatBubble
```typescript
interface CJAIChatBubbleProps {
  /** 추가 CSS 클래스 */
  className?: string;
  
  /** 채팅 버블 위치 */
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  
  /** 메시지 전송 핸들러 */
  onSendMessage?: (message: string) => Promise<string>;
  
  /** 초기 메시지 목록 */
  initialMessages?: Message[];
  
  /** 플레이스홀더 텍스트 */
  placeholder?: string;
  
  /** 최대 메시지 길이 */
  maxMessageLength?: number;
  
  /** 자동 스크롤 비활성화 */
  disableAutoScroll?: boolean;
  
  /** 타이핑 지연 시간 */
  typingDelay?: number;
  
  /** 테마 설정 */
  theme?: 'light' | 'dark' | 'auto';
}

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  isTyping?: boolean;
  attachments?: string[];
}
```

---

## 🔄 상태 전환 다이어그램

### TokenBalanceWidget 상태 다이어그램
```
┌─────────────┐
│   LOADING   │
└─────┬───────┘
      │
      ▼
┌─────────────┐    amount < 100K     ┌─────────────┐
│   NORMAL    │─────────────────────▶│  CRITICAL   │
└─────┬───────┘                     └─────────────┘
      │                                     ▲
      │ amount < 500K                       │
      ▼                                     │
┌─────────────┐                            │
│   WARNING   │────────────────────────────┘
└─────────────┘    amount < 100K

States:
- LOADING: 데이터 로딩 중
- NORMAL: 정상 상태 (녹색)
- WARNING: 경고 상태 (주황색)
- CRITICAL: 위험 상태 (빨간색)

Triggers:
- amount: 토큰 수량 변화
- status: 직접 상태 변경
```

### CJChatBubble 상태 다이어그램
```
┌─────────────┐
│    IDLE     │
└─────┬───────┘
      │
      │ message received
      ▼
┌─────────────┐    typing complete    ┌─────────────┐
│   TYPING    │─────────────────────▶│  SPEAKING   │
└─────┬───────┘                     └─────┬───────┘
      │                                   │
      │ typing cancelled                  │ speaking complete
      ▼                                   ▼
┌─────────────┐◀──────────────────────────┘
│    IDLE     │
└─────────────┘

Avatar Mood States:
┌─────────────┐    positive event    ┌─────────────┐
│   NORMAL    │─────────────────────▶│    HAPPY    │
└─────┬───────┘                     └─────┬───────┘
      │                                   │
      │ negative event                    │ timeout
      ▼                                   ▼
┌─────────────┐                     ┌─────────────┐
│     SAD     │                     │   NORMAL    │
└─────┬───────┘                     └─────────────┘
      │                                   ▲
      │ error event                       │
      ▼                                   │
┌─────────────┐                          │
│    ANGRY    │──────────────────────────┘
└─────────────┘    timeout
```

### CJAIChatBubble 상태 다이어그램
```
┌─────────────┐
│   CLOSED    │
└─────┬───────┘
      │
      │ button click
      ▼
┌─────────────┐    close button      ┌─────────────┐
│    OPEN     │─────────────────────▶│   CLOSED    │
└─────┬───────┘                     └─────────────┘
      │
      │ send message
      ▼
┌─────────────┐    response received ┌─────────────┐
│   LOADING   │─────────────────────▶│    OPEN     │
└─────────────┘                     └─────────────┘

Message States:
┌─────────────┐    user input        ┌─────────────┐
│    EMPTY    │─────────────────────▶│   PENDING   │
└─────────────┘                     └─────┬───────┘
      ▲                                   │
      │                                   │ send
      │ message sent                      ▼
      └───────────────────────────────────┤
                                    ┌─────────────┐
                                    │    SENT     │
                                    └─────────────┘
```

---

## 🎨 디자인 시스템

### 색상 팔레트
```scss
// Primary Colors
$primary-blue: #3b82f6;
$primary-purple: #8b5cf6;
$primary-gradient: linear-gradient(135deg, $primary-blue, $primary-purple);

// Status Colors
$success: #10b981;
$warning: #f59e0b;
$error: #ef4444;
$info: #06b6d4;

// Neutral Colors
$slate-50: #f8fafc;
$slate-100: #f1f5f9;
$slate-200: #e2e8f0;
$slate-300: #cbd5e1;
$slate-400: #94a3b8;
$slate-500: #64748b;
$slate-600: #475569;
$slate-700: #334155;
$slate-800: #1e293b;
$slate-900: #0f172a;

// Semantic Colors
$background-light: #ffffff;
$background-dark: #1e1e1e;
$text-primary: #0f172a;
$text-secondary: #64748b;
$text-muted: #94a3b8;
```

### 그림자 시스템
```css
/* 그림자 레벨 */
.shadow-sm { box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05); }
.shadow { box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1); }
.shadow-md { box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1); }
.shadow-lg { box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1); }
.shadow-xl { box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1); }
.shadow-2xl { box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.25); }

/* 글로우 효과 */
.glow-blue { box-shadow: 0 0 20px rgb(59 130 246 / 0.3); }
.glow-purple { box-shadow: 0 0 20px rgb(139 92 246 / 0.3); }
.glow-emerald { box-shadow: 0 0 20px rgb(16 185 129 / 0.3); }
.glow-amber { box-shadow: 0 0 20px rgb(245 158 11 / 0.3); }
.glow-red { box-shadow: 0 0 20px rgb(239 68 68 / 0.3); }
```

### 간격 시스템
```css
/* 스페이싱 스케일 */
.spacing-xs: 0.25rem;   /* 4px */
.spacing-sm: 0.5rem;    /* 8px */
.spacing-md: 1rem;      /* 16px */
.spacing-lg: 1.5rem;    /* 24px */
.spacing-xl: 2rem;      /* 32px */
.spacing-2xl: 3rem;     /* 48px */
.spacing-3xl: 4rem;     /* 64px */
```

---

## 📝 개발 가이드라인

### 파일 구조 규칙
```
components/
├── ui/              # 재사용 가능한 기본 컴포넌트
├── feature/         # 특정 기능별 컴포넌트
├── layout/          # 레이아웃 컴포넌트
└── common/          # 공통 컴포넌트

utils/
├── animations.ts    # 애니메이션 유틸리티
├── constants.ts     # 상수 정의
├── helpers.ts       # 헬퍼 함수
└── types.ts         # 타입 정의

hooks/
├── useAnimation.ts  # 애니메이션 훅
├── useResponsive.ts # 반응형 훅
└── useLocalStorage.ts # 로컬 스토리지 훅
```

### 네이밍 컨벤션
```typescript
// 컴포넌트: PascalCase
export const TokenBalanceWidget = () => {};

// 프로퍼티: camelCase
interface Props {
  avatarMood: string;
  showVoiceToggle: boolean;
}

// 상수: SCREAMING_SNAKE_CASE
const ANIMATION_DURATION = 300;
const DEFAULT_AVATAR_SIZE = 48;

// 함수: camelCase
const handleVoiceToggle = () => {};
const getAvatarColors = () => {};

// 타입: PascalCase
type AvatarMood = 'normal' | 'happy' | 'sad' | 'angry';
interface ChatMessage {
  id: string;
  text: string;
}
```

### 성능 최적화 가이드
```typescript
// 1. React.memo 사용
export const TokenBalanceWidget = React.memo(({ amount, status }: Props) => {
  // 컴포넌트 로직
});

// 2. useMemo로 계산 최적화
const formattedAmount = useMemo(() => {
  return formatCurrency(amount);
}, [amount]);

// 3. useCallback으로 함수 최적화
const handleClick = useCallback(() => {
  onClick?.(amount);
}, [onClick, amount]);

// 4. 조건부 렌더링 최적화
const shouldShowAnimation = useMemo(() => {
  return !disableAnimation && isVisible;
}, [disableAnimation, isVisible]);
```

### 접근성 가이드라인
```typescript
// ARIA 속성 사용
<button
  aria-label="음성 토글"
  aria-pressed={isVoiceEnabled}
  role="button"
  tabIndex={0}
>

// 키보드 내비게이션 지원
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Enter' || e.key === ' ') {
    handleClick();
  }
};

// 색상 대비 확인
const getContrastColor = (backgroundColor: string) => {
  // 대비 비율 계산 로직
};

// 스크린 리더 지원
<div aria-live="polite" aria-atomic="true">
  {statusMessage}
</div>
```

### 테스트 가이드
```typescript
// 컴포넌트 단위 테스트
describe('TokenBalanceWidget', () => {
  it('should display formatted amount', () => {
    render(<TokenBalanceWidget amount={1234567} />);
    expect(screen.getByText('1.2M')).toBeInTheDocument();
  });
  
  it('should show warning status', () => {
    render(<TokenBalanceWidget amount={1000} status="warning" />);
    expect(screen.getByText(/warning/i)).toBeInTheDocument();
  });
});

// 애니메이션 테스트
it('should animate state changes', async () => {
  const { rerender } = render(<CJChatBubble state="idle" />);
  rerender(<CJChatBubble state="typing" />);
  
  await waitFor(() => {
    expect(screen.getByTestId('typing-indicator')).toBeInTheDocument();
  });
});
```

---

## 🚀 배포 및 빌드 설정

### 환경 변수
```env
# 개발 환경
NEXT_PUBLIC_API_URL=http://localhost:3000/api
NEXT_PUBLIC_ANIMATION_DURATION=300
NEXT_PUBLIC_DEBUG_MODE=true

# 프로덕션 환경
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_ANIMATION_DURATION=200
NEXT_PUBLIC_DEBUG_MODE=false
```

### 빌드 최적화
```javascript
// next.config.js
module.exports = {
  experimental: {
    optimizeCss: true,
    optimizeImages: true,
  },
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  images: {
    formats: ['image/webp', 'image/avif'],
    minimumCacheTTL: 60,
  },
};
```

---

## 📚 참고 자료

### 라이브러리 버전
- React: ^18.0.0
- Next.js: ^14.0.0
- TypeScript: ^5.0.0
- Tailwind CSS: ^4.0.0
- Framer Motion: ^11.0.0
- Lucide React: ^0.400.0

### 유용한 링크
- [Tailwind CSS 공식 문서](https://tailwindcss.com/docs)
- [Framer Motion 공식 문서](https://www.framer.com/motion/)
- [React Hook Form 공식 문서](https://react-hook-form.com/)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

*이 문서는 CJ AI Dashboard 프로젝트의 개발 표준을 정의하며, 새로운 기능 추가 시 참고해야 할 가이드라인입니다.*