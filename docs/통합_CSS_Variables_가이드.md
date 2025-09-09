# 🎨 CSS Variables 통합 가이드

## 📋 목차
- 색상 시스템(네온/슬레이트/상태/그라데이션 등)
- 간격/그리드/스페이싱 시스템
- 버튼/카드/위젯/버블 등 컴포넌트별 변수
- 타이포그래피/폰트/라인/무게
- 그림자/글로우/애니메이션
- 경계선/반지름/레이어
- 사용 예시(TypeScript/Tailwind 등)
- 확장/오버라이드/다크모드
- ⚠️ 양립불가/오류 케이스

---

## 색상 시스템 (통합)
```css
:root {
  /* 네온 퍼플/그라데이션 */
  --neon-purple-1: #7b29cd;
  --neon-purple-2: #870dd1;
  --neon-purple-3: #5b30f6;
  --neon-purple-4: #8054f2;
  --neon-gradient-1: linear-gradient(45deg, #7b29cd, #870dd1);
  --neon-gradient-2: linear-gradient(45deg, #870dd1, #5b30f6);
  --neon-gradient-3: linear-gradient(45deg, #5b30f6, #8054f2);
  --neon-gradient-4: linear-gradient(45deg, #8054f2, #7b29cd);

  /* Slate/Blue/Purple/Emerald/Amber/Red */
  --color-slate-900: #0f172a;
  --color-blue-500: #3b82f6;
  --color-purple-500: #a855f7;
  --color-emerald-500: #10b981;
  --color-amber-500: #f59e0b;
  --color-red-500: #ef4444;

  /* 상태별 의미론적 색상 */
  --color-success: var(--color-emerald-500);
  --color-warning: var(--color-amber-500);
  --color-error: var(--color-red-500);
  --color-info: var(--color-blue-500);

  /* Token/Widget/ChatBubble 등 컴포넌트별 색상 */
  --token-widget-normal-bg: rgba(16, 185, 129, 0.1);
  --token-widget-warning-bg: rgba(245, 158, 11, 0.1);
  --token-widget-critical-bg: rgba(239, 68, 68, 0.1);
  --chat-bubble-bg: rgba(15, 23, 42, 0.95);
  --chat-bubble-user-bg: var(--color-blue-500);
  --chat-bubble-ai-bg: var(--color-slate-800);
}
```

---

## 간격/그리드/스페이싱 시스템 (통합)
```css
:root {
  /* 8px/4px 기반 스페이싱 */
  --spacing-0: 0px;
  --spacing-1: 8px;
  --spacing-2: 16px;
  --spacing-3: 24px;
  --spacing-4: 32px;
  --spacing-5: 40px;
  --spacing-6: 48px;
  --spacing-8: 64px;
  --spacing-10: 80px;
  --spacing-12: 96px;
  /* 4px 계열도 포함 */
  --spacing-0-5: 2px;
  --spacing-1-5: 6px;
  --spacing-2-5: 10px;
  --spacing-3-5: 14px;
}
```

---

## 버튼/카드/위젯/버블 등 컴포넌트별 변수 (통합)
```css
:root {
  /* 버튼 */
  --btn-padding-sm: var(--spacing-1) var(--spacing-2);
  --btn-padding-md: var(--spacing-2) var(--spacing-3);
  --btn-padding-lg: var(--spacing-2) var(--spacing-4);
  --btn-height-sm: 32px;
  --btn-height-md: 40px;
  --btn-height-lg: 48px;
  --icon-sm: 16px;
  --icon-md: 20px;
  --icon-lg: 24px;

  /* 카드/게임/미션/리워드 */
  --card-min-height-base: 320px;
  --card-min-height-game: 380px;
  --card-padding: 24px;
  --card-gap: 16px;
  --radius-card: 16px;
  --radius-image: 12px;
  --radius-button: 12px;
  --radius-badge: 9999px;

  /* TokenBalanceWidget */
  --token-widget-padding: var(--spacing-6);
  --token-widget-gap: var(--spacing-4);
  --token-widget-radius: 16px;
  --token-widget-width: 100%;
  --token-widget-max-width: 28rem;
  --token-widget-min-height: 12rem;
  --token-widget-icon-size: 1.25rem;
  --token-widget-animation-duration: 0.5s;

  /* ChatBubble */
  --chat-bubble-width: 20rem;
  --chat-bubble-radius: 16px;
  --chat-bubble-padding: var(--spacing-4);
}
```

---

## 타이포그래피/폰트/라인/무게 (통합)
```css
:root {
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-2xl: 24px;
  --font-size-3xl: 30px;
  --font-size-4xl: 36px;
  --font-size-5xl: 48px;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --line-height-normal: 1.5;
  --line-height-tight: 1.25;
  --font-family-sans: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', 'Helvetica Neue', Arial, sans-serif;
  --font-family-serif: 'Georgia', 'Times New Roman', Times, serif;
  --font-family-mono: 'Fira Code', 'Monaco', 'Consolas', 'Menlo', 'Liberation Mono', monospace;
}
```

---

## 그림자/글로우/애니메이션 (통합)
```css
:root {
  --shadow-default: 0 2px 10px rgba(0,0,0,0.2), 0 0 0 1px rgba(123,41,205,0.15);
  --shadow-hover: 0 8px 20px rgba(123,41,205,0.2), 0 0 0 1px rgba(123,41,205,0.25), 0 0 10px rgba(123,41,205,0.15);
  --shadow-active: 0 4px 15px rgba(135,13,209,0.3), 0 0 0 2px rgba(135,13,209,0.35);
  --glow-subtle: 0 0 5px rgba(123,41,205,0.2);
  --glow-medium: 0 0 10px rgba(123,41,205,0.4);
  --glow-strong: 0 0 15px rgba(123,41,205,0.6);
  --text-glow: 0 0 8px rgba(123,41,205,0.3);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
}
```

---

## 경계선/반지름/레이어 (통합)
```css
:root {
  --radius-none: 0px;
  --radius-sm: 2px;
  --radius-base: 4px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --radius-xl: 12px;
  --radius-2xl: 16px;
  --radius-3xl: 24px;
  --radius-full: 9999px;
  --z-background: 0;
  --z-card: 10;
  --z-overlay: 20;
  --z-modal: 30;
  --z-tooltip: 40;
  --z-particle: 5;
}
```

---

## 사용 예시(TypeScript/Tailwind 등)
```typescript
const buttonSizes = {
  sm: 'var(--btn-height-sm)',
  md: 'var(--btn-height-md)',
  lg: 'var(--btn-height-lg)'
} as const;

const spacing = {
  1: 'var(--spacing-1)',
  2: 'var(--spacing-2)',
  3: 'var(--spacing-3)'
} as const;
```

```tsx
// 동적 스타일 적용
const Button = ({ size = 'md' }) => {
  const style = {
    height: `var(--btn-height-${size})`,
    padding: `var(--btn-padding-${size})`,
    borderRadius: 'var(--spacing-1)'
  };
  return <button style={style}>버튼</button>;
};
```

---

## 확장/오버라이드/다크모드 (통합)
```css
:root { /* ...기본값... */ }
.dark { /* 다크모드 오버라이드 */ }
```

---

## ⚠️ 양립불가/오류 케이스
- 001/002/003/004/005의 spacing 단위(4px/8px/16px 등)와 네이밍이 혼용될 수 있으므로, 프로젝트 내 기준을 명확히 통일해야 함
- 002의 네온 계열 변수와 005의 slate/emerald/amber 계열 변수는 혼용시 색상 일관성에 주의
- 004의 8px 그리드와 005의 4px 계열 spacing은 혼용시 레이아웃 충돌 가능(통합시 하나의 기준만 사용 권장)
- 컴포넌트별 전용 변수(예: --token-widget-*, --chat-bubble-*)는 네이밍/범위가 다를 수 있으니, 공통화/확장시 충돌 주의

---

*마지막 업데이트: 2025년 6월 19일*
*버전: 1.0.0*
