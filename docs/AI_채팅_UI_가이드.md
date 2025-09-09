# AI 채팅창(감정 기반 컬러) UI 가이드

## 1. 개요
- 이 가이드는 감정(무드) 기반 컬러 시스템을 적용한 AI 채팅 UI의 설계 및 구현 원칙을 설명합니다.
- atomic CSS 시스템(global.css)과 연동하여, 일관된 스타일과 반응형, 애니메이션, 접근성을 보장합니다.

---

## 2. 디자인 원칙
- **감정(무드)별 컬러 매핑**: 각 감정 상태에 따라 채팅 버블, 배경, 텍스트, 이펙트 컬러가 동적으로 변합니다.
- **Atomic Class 구조**: 모든 스타일은 global.css의 atomic 유틸리티와 변수 기반으로 조합합니다.
- **상태/애니메이션**: 등장, 전환, 강조 등 다양한 애니메이션 효과를 제공합니다.
- **접근성**: 색상 대비, 스크린리더, 키보드 내비게이션을 고려합니다.

---

## 3. 감정(무드) 컬러 매핑 예시
| 무드      | 배경색                | 텍스트색           | 강조/이펙트           |
|-----------|----------------------|--------------------|-----------------------|
| 기본      | var(--card)          | var(--foreground)  | var(--gradient-purple-primary) |
| 기쁨      | #FFE066              | #1A1A1A            | var(--color-accent-amber)      |
| 슬픔      | #3B4A6B              | #FFFFFF            | var(--color-info)             |
| 분노      | #FF4516              | #FFFFFF            | var(--color-accent-red)        |
| 놀람      | #F59E0B              | #1A1A1A            | var(--color-accent-amber)      |
| 차분      | #135B79              | #FFFFFF            | var(--color-info)             |
| 사랑      | #FFB6B9              | #1A1A1A            | #FF6F91                      |
| 중립      | var(--card)          | var(--foreground)  | var(--gradient-dark)           |

> **Tip:** 컬러 변수는 global.css에 등록하거나, 컴포넌트 내에서 style prop으로 동적 할당합니다.

---

## 4. Atomic Class 구조 예시
- `.chat-bubble` : 채팅 버블 기본 스타일
- `.chat-bubble-mood-joy` : 기쁨 무드 배경/텍스트
- `.chat-bubble-mood-sad` : 슬픔 무드 배경/텍스트
- `.chat-bubble-mood-angry` : 분노 무드 배경/텍스트
- ... (각 무드별로 확장)
- `.chat-bubble-animate` : 등장/강조 애니메이션

### 예시 CSS (global.css에 추가)
```css
.chat-bubble {
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-lg);
  font-size: var(--font-size-body);
  max-width: 80%;
  margin-bottom: var(--spacing-2);
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: background var(--transition-normal), color var(--transition-normal);
}
.chat-bubble-mood-joy { background: #FFE066; color: #1A1A1A; }
.chat-bubble-mood-sad { background: #3B4A6B; color: #FFFFFF; }
.chat-bubble-mood-angry { background: #FF4516; color: #FFFFFF; }
.chat-bubble-mood-calm { background: #135B79; color: #FFFFFF; }
.chat-bubble-mood-love { background: #FFB6B9; color: #1A1A1A; }
.chat-bubble-mood-neutral { background: var(--card); color: var(--foreground); }
.chat-bubble-animate { animation: fadeIn 0.5s ease, scaleIn 0.3s ease; }
```

---

## 5. 주요 Props 및 상태 설계
- `mood`: 감정 상태 ("joy", "sad", "angry", "calm", "love", "neutral" 등)
- `message`: 채팅 텍스트
- `from`: "user" | "ai"
- `isActive`: 강조/애니메이션 여부
- `timestamp`: 시간 표시 (선택)

---

## 6. React 컴포넌트 예시
```tsx
import React from 'react';
import clsx from 'clsx';

const moodClassMap = {
  joy: 'chat-bubble-mood-joy',
  sad: 'chat-bubble-mood-sad',
  angry: 'chat-bubble-mood-angry',
  calm: 'chat-bubble-mood-calm',
  love: 'chat-bubble-mood-love',
  neutral: 'chat-bubble-mood-neutral',
};

export function AIChatBubble({ mood = 'neutral', message, from = 'ai', isActive = false, timestamp }) {
  return (
    <div
      className={clsx(
        'chat-bubble',
        moodClassMap[mood],
        isActive && 'chat-bubble-animate',
        from === 'user' ? 'ml-auto' : 'mr-auto'
      )}
      tabIndex={0} // 접근성
      aria-live={isActive ? 'polite' : undefined}
    >
      <span>{message}</span>
      {timestamp && <span className="text-caption ml-2">{timestamp}</span>}
    </div>
  );
}
```

---

## 7. 애니메이션/UX
- 등장: `fadeIn`, `scaleIn` 키프레임 활용
- 강조: `neon-text`, `neon-border` 등 atomic 효과 조합 가능
- 무드 전환: background/color 트랜지션 smooth하게 적용
- 반응형: max-width, padding, font-size 등 atomic 유틸리티 활용

---

## 8. 베스트 프랙티스
- 컬러 변수와 atomic class를 최대한 활용해 유지보수성을 높입니다.
- 무드별 스타일은 CSS 변수/클래스 조합으로 확장성을 확보합니다.
- 접근성(A11y) 속성(tabIndex, aria-live 등) 필수 적용
- 애니메이션은 prefers-reduced-motion 대응
- 글로벌 스타일(global.css)과 컴포넌트 스타일을 분리하되, atomic 시스템을 일관되게 사용합니다.

---

## 9. 확장/커스터마이즈
- 무드 추가 시 `.chat-bubble-mood-XXX` 클래스와 컬러 변수만 추가하면 됩니다.
- 다국어, 이모지, 이미지, 첨부파일 등 다양한 메시지 타입도 동일한 구조로 확장 가능합니다.

---

## 10. 참고
- global.css의 atomic 유틸리티와 변수 시스템을 적극 활용하세요.
- 실제 구현 예시는 프로젝트 내 컴포넌트 폴더 참고.
