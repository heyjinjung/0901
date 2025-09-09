# 빠른 참조 가이드

## 🚀 빠른 시작

### 설치 및 설정
```bash
# 프로젝트 클론
git clone <repository-url>
cd cj-ai-dashboard

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

### 기본 사용법
```tsx
import { TokenBalanceWidget, CJChatBubble, CJAIChatBubble } from './components';

// 토큰 위젯
<TokenBalanceWidget amount={1234567} status="normal" />

// 채팅 버블
<CJChatBubble message="안녕하세요!" avatarMood="happy" />

// AI 채팅 인터페이스
<CJAIChatBubble position="bottom-right" />
```

---

## 🎨 스타일 치트시트

### 색상 클래스
```css
/* 상태 색상 */
.text-token-normal { color: #10b981; }
.text-token-warning { color: #f59e0b; }
.text-token-critical { color: #ef4444; }

/* 배경 색상 */
.bg-token-normal { background-color: rgb(16 185 129 / 0.1); }
.bg-token-warning { background-color: rgb(245 158 11 / 0.1); }
.bg-token-critical { background-color: rgb(239 68 68 / 0.1); }

/* 그라디언트 */
.bg-gradient-primary { background: linear-gradient(135deg, #3b82f6, #8b5cf6); }
.bg-gradient-success { background: linear-gradient(135deg, #10b981, #06b6d4); }
.bg-gradient-warning { background: linear-gradient(135deg, #f59e0b, #fb923c); }
```

### 애니메이션 클래스
```css
/* 기본 애니메이션 */
.animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
.animate-slide-up { animation: slideUp 0.5s ease-out; }
.animate-scale { animation: scale 0.4s ease-out; }
.animate-pulse-slow { animation: pulse 3s ease-in-out infinite; }

/* 호버 효과 */
.hover-scale { transition: transform 0.2s; }
.hover-scale:hover { transform: scale(1.05); }
.hover-glow { transition: box-shadow 0.3s; }
.hover-glow:hover { box-shadow: 0 0 20px rgba(59, 130, 246, 0.3); }
```

---

## 🔧 유틸리티 함수

### 포맷팅 함수
```typescript
// 숫자 포맷팅
export const formatNumber = (num: number): string => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
  return num.toLocaleString();
};

// 통화 포맷팅
export const formatCurrency = (amount: number, currency = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0
  }).format(amount);
};

// 시간 포맷팅
export const formatTime = (date: Date): string => {
  return date.toLocaleTimeString('ko-KR', {
    hour: '2-digit',
    minute: '2-digit'
  });
};
```

### 애니메이션 헬퍼
```typescript
// 애니메이션 프리셋
export const animations = {
  fadeIn: { initial: { opacity: 0 }, animate: { opacity: 1 } },
  slideUp: { initial: { y: 20, opacity: 0 }, animate: { y: 0, opacity: 1 } },
  scale: { initial: { scale: 0.8 }, animate: { scale: 1 } },
  bounce: { animate: { y: [0, -10, 0] }, transition: { duration: 0.6 } }
};

// 지연 애니메이션
export const staggerChildren = {
  animate: { transition: { staggerChildren: 0.1 } }
};
```

### 상태 관리 훅
```typescript
// 토큰 상태 훅
export const useTokenStatus = (amount: number) => {
  return useMemo(() => {
    if (amount < 100000) return 'critical';
    if (amount < 500000) return 'warning';
    return 'normal';
  }, [amount]);
};

// 로컬 스토리지 훅
export const useLocalStorage = <T>(key: string, initialValue: T) => {
  const [value, setValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setStoredValue = (value: T) => {
    setValue(value);
    window.localStorage.setItem(key, JSON.stringify(value));
  };

  return [value, setStoredValue] as const;
};
```

---

## 📱 반응형 치트시트

### 브레이크포인트
```css
/* Tailwind 브레이크포인트 */
sm: 640px   /* 태블릿 */
md: 768px   /* 작은 노트북 */
lg: 1024px  /* 데스크톱 */
xl: 1280px  /* 큰 데스크톱 */
2xl: 1536px /* 초대형 화면 */
```

### 반응형 클래스 패턴
```tsx
// 그리드 레이아웃
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

// 텍스트 크기
<h1 className="text-2xl md:text-3xl lg:text-4xl">

// 패딩/마진
<div className="p-4 md:p-6 lg:p-8">

// 숨김/표시
<div className="hidden md:block">
<div className="block md:hidden">
```

---

## 🎯 컴포넌트 Props 요약

### TokenBalanceWidget
```typescript
interface TokenBalanceProps {
  amount: number;                    // 필수: 토큰 수량
  status?: 'normal'|'warning'|'critical'; // 상태
  change?: 'none'|'increase'|'decrease';  // 변화
  className?: string;                // CSS 클래스
}
```

### CJChatBubble
```typescript
interface CJChatBubbleProps {
  message: string;                   // 필수: 메시지
  state?: 'idle'|'typing'|'speaking'; // AI 상태
  avatarMood?: 'normal'|'happy'|'sad'|'angry'; // 감정
  showVoiceToggle?: boolean;         // 음성 토글
  onVoiceToggle?: () => void;        // 음성 핸들러
  className?: string;                // CSS 클래스
}
```

### CJAIChatBubble
```typescript
interface CJAIChatBubbleProps {
  className?: string;                // CSS 클래스
  position?: 'bottom-right'|'bottom-left'|'top-right'|'top-left'; // 위치
  onSendMessage?: (msg: string) => Promise<string>; // 메시지 핸들러
}
```

---

## 🐛 디버깅 가이드

### 일반적인 문제들

#### 1. 애니메이션이 작동하지 않음
```typescript
// 해결책: Framer Motion 설정 확인
import { motion } from 'framer-motion';

// 올바른 사용법
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.3 }}
>
```

#### 2. 반응형이 제대로 적용되지 않음
```css
/* 해결책: 모바일 우선 접근법 사용 */
.widget {
  @apply w-full;      /* 기본 (모바일) */
  @apply md:w-1/2;    /* 태블릿 */
  @apply lg:w-1/3;    /* 데스크톱 */
}
```

#### 3. 상태 변경이 반영되지 않음
```typescript
// 해결책: 의존성 배열 확인
useEffect(() => {
  // 상태 변경 로직
}, [dependency]); // 의존성 누락 확인
```

### 성능 최적화 팁

#### 1. 메모이제이션 사용
```typescript
// React.memo로 리렌더링 방지
export const TokenBalanceWidget = React.memo(({ amount, status }) => {
  // 컴포넌트 로직
});

// useMemo로 계산 최적화
const formattedAmount = useMemo(() => formatNumber(amount), [amount]);
```

#### 2. 애니메이션 최적화
```typescript
// will-change 속성 사용
<motion.div
  style={{ willChange: 'transform' }}
  animate={{ scale: [1, 1.1, 1] }}
>

// 애니메이션 조건부 적용
const shouldAnimate = !prefersReducedMotion && isVisible;
```

---

## 📋 체크리스트

### 컴포넌트 구현 체크리스트
- [ ] Props 타입 정의
- [ ] 반응형 디자인 적용
- [ ] 애니메이션 구현
- [ ] 접근성 속성 추가
- [ ] 에러 처리
- [ ] 성능 최적화
- [ ] 테스트 작성
- [ ] 문서화

### 코드 리뷰 체크리스트
- [ ] TypeScript 타입 안정성
- [ ] 컴포넌트 재사용성
- [ ] 성능 최적화
- [ ] 접근성 준수
- [ ] 코드 가독성
- [ ] 테스트 커버리지
- [ ] 문서 업데이트

---

## 🆘 도움말

### 자주 묻는 질문

**Q: 컴포넌트가 렌더링되지 않아요**
A: 다음을 확인해보세요:
1. 필수 props가 전달되었는지
2. 컴포넌트가 올바르게 import되었는지
3. 콘솔에 에러가 있는지

**Q: 애니메이션이 너무 빨라요/느려요**
A: `transition` 속성의 `duration` 값을 조정하세요:
```typescript
transition={{ duration: 0.5 }} // 0.5초로 설정
```

**Q: 모바일에서 레이아웃이 깨져요**
A: 반응형 클래스를 확인하고 모바일 우선 접근법을 사용하세요:
```css
.container {
  @apply w-full px-4;     /* 모바일 */
  @apply md:w-auto md:px-6; /* 데스크톱 */
}
```

### 추가 리소스
- [React 공식 문서](https://react.dev/)
- [Tailwind CSS 공식 문서](https://tailwindcss.com/)
- [Framer Motion 공식 문서](https://www.framer.com/motion/)
- [TypeScript 공식 문서](https://www.typescriptlang.org/)

---

*이 가이드는 빠른 개발을 위한 참조 자료입니다. 더 자세한 정보는 각 컴포넌트의 상세 문서를 참조하세요.*