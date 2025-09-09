# 컴포넌트 상세 스펙 문서

## 📋 목차
1. [TokenBalanceWidget](#tokenbalancewidget)
2. [CJChatBubble](#cjchatbubble)
3. [CJAIChatBubble](#cjaichatbubble)
4. [사용 예시](#사용-예시)
5. [커스터마이징 가이드](#커스터마이징-가이드)

---

## 💰 TokenBalanceWidget

### 개요
사용자의 토큰 잔고를 시각적으로 표시하는 위젯입니다. 토큰 상태에 따라 색상이 변경되며, 잔고 변화를 애니메이션으로 표현합니다.

### Props 상세
| Prop | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `amount` | `number` | - | ✅ | 토큰 잔고 수량 |
| `status` | `'normal' \| 'warning' \| 'critical'` | `'normal'` | ❌ | 토큰 상태 |
| `change` | `'none' \| 'increase' \| 'decrease'` | `'none'` | ❌ | 토큰 변화 방향 |
| `className` | `string` | `''` | ❌ | 추가 CSS 클래스 |

### 상태별 스타일
```typescript
const statusStyles = {
  normal: {
    color: 'emerald-400',
    background: 'emerald-500/10',
    border: 'emerald-500/30',
    glow: 'emerald-500/20'
  },
  warning: {
    color: 'amber-400',
    background: 'amber-500/10',
    border: 'amber-500/30',
    glow: 'amber-500/20'
  },
  critical: {
    color: 'red-400',
    background: 'red-500/10',
    border: 'red-500/30',
    glow: 'red-500/20'
  }
};
```

### 사용 예시
```tsx
// 기본 사용법
<TokenBalanceWidget amount={1234567} />

// 경고 상태
<TokenBalanceWidget 
  amount={50000} 
  status="warning" 
  change="decrease" 
/>

// 위험 상태
<TokenBalanceWidget 
  amount={5000} 
  status="critical" 
  change="decrease"
  className="mb-4" 
/>

// 증가 상태
<TokenBalanceWidget 
  amount={2000000} 
  status="normal" 
  change="increase" 
/>
```

### 애니메이션 트리거
- **마운트**: 페이드인 + 슬라이드업 애니메이션
- **amount 변경**: 스케일 애니메이션 + 숫자 카운터 효과
- **status 변경**: 색상 트랜지션 + 글로우 효과
- **change 변경**: 아이콘 회전 + 트렌드 표시

### 반응형 동작
```css
/* Mobile (기본) */
.token-widget {
  width: 100%;
  max-width: 28rem; /* max-w-md */
  margin: 0 auto;
}

/* Desktop (lg 이상) */
@media (min-width: 1024px) {
  .token-widget {
    margin: 0;
  }
}
```

---

## 💬 CJChatBubble

### 개요
단일 메시지를 표시하는 채팅 버블 컴포넌트입니다. AI 아바타의 감정 상태와 메시지 상태를 시각적으로 표현합니다.

### Props 상세
| Prop | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `message` | `string` | - | ✅ | 표시할 메시지 텍스트 |
| `state` | `'idle' \| 'typing' \| 'speaking'` | `'idle'` | ❌ | AI 상태 |
| `avatarMood` | `'normal' \| 'happy' \| 'sad' \| 'angry'` | `'normal'` | ❌ | 아바타 감정 상태 |
| `showVoiceToggle` | `boolean` | `false` | ❌ | 음성 토글 버튼 표시 |
| `onVoiceToggle` | `() => void` | - | ❌ | 음성 토글 핸들러 |
| `className` | `string` | `''` | ❌ | 추가 CSS 클래스 |

### 아바타 감정별 스타일
```typescript
const avatarMoods = {
  normal: {
    gradient: 'from-blue-500 to-purple-500',
    icon: 'Sparkles',
    filter: 'saturate-100',
    glow: 'shadow-blue-500/30'
  },
  happy: {
    gradient: 'from-emerald-400 to-cyan-400',
    icon: 'Heart',
    filter: 'saturate-150 brightness-110',
    glow: 'shadow-emerald-400/30'
  },
  sad: {
    gradient: 'from-blue-400 to-indigo-400',
    icon: 'Frown',
    filter: 'saturate-75 brightness-90',
    glow: 'shadow-blue-400/30'
  },
  angry: {
    gradient: 'from-red-400 to-orange-400',
    icon: 'Angry',
    filter: 'saturate-125 contrast-110',
    glow: 'shadow-red-400/30'
  }
};
```

### 상태별 애니메이션
```typescript
const stateAnimations = {
  idle: {
    scale: [1, 1.02, 1],
    transition: { duration: 3, repeat: Infinity }
  },
  typing: {
    scale: [1, 1.05, 1],
    transition: { duration: 1.5, repeat: Infinity }
  },
  speaking: {
    scale: [1, 1.1, 1],
    transition: { duration: 0.8, repeat: Infinity }
  }
};
```

### 사용 예시
```tsx
// 기본 메시지
<CJChatBubble message="안녕하세요! 도움이 필요하신가요?" />

// 타이핑 상태
<CJChatBubble 
  message="현재 답변을 준비하고 있습니다..." 
  state="typing"
  avatarMood="normal"
/>

// 기쁜 감정 + 음성 토글
<CJChatBubble 
  message="와! 정말 좋은 소식이네요! 🎉"
  state="speaking"
  avatarMood="happy"
  showVoiceToggle={true}
  onVoiceToggle={() => console.log('Voice toggled')}
/>

// 슬픈 감정
<CJChatBubble 
  message="죄송합니다. 문제가 발생했습니다."
  avatarMood="sad"
  state="idle"
/>

// 화난 감정
<CJChatBubble 
  message="시스템 오류가 발생했습니다!"
  avatarMood="angry"
  state="idle"
/>
```

### 타이핑 효과 설정
```typescript
// 타이핑 속도 조절
const typingSpeed = 50; // ms per character

// 타이핑 이벤트 핸들러
useEffect(() => {
  if (state === 'typing') {
    setDisplayedMessage('');
    let index = 0;
    const timer = setInterval(() => {
      if (index < message.length) {
        setDisplayedMessage(prev => prev + message[index]);
        index++;
      } else {
        clearInterval(timer);
      }
    }, typingSpeed);
    return () => clearInterval(timer);
  }
}, [message, state]);
```

---

## 🤖 CJAIChatBubble

### 개요
완전한 채팅 인터페이스를 제공하는 컴포넌트입니다. 사용자와 AI 간의 대화를 관리하며, 플로팅 형태로 표시됩니다.

### Props 상세
| Prop | Type | Default | Required | Description |
|------|------|---------|----------|-------------|
| `className` | `string` | `''` | ❌ | 추가 CSS 클래스 |
| `position` | `'bottom-right' \| 'bottom-left' \| 'top-right' \| 'top-left'` | `'bottom-right'` | ❌ | 채팅 위치 |
| `onSendMessage` | `(message: string) => Promise<string>` | - | ❌ | 메시지 전송 핸들러 |

### Message 인터페이스
```typescript
interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  isTyping?: boolean;
}
```

### 위치별 CSS 클래스
```typescript
const positionClasses = {
  'bottom-right': 'bottom-4 right-4',
  'bottom-left': 'bottom-4 left-4',
  'top-right': 'top-4 right-4',
  'top-left': 'top-4 left-4'
};
```

### 사용 예시
```tsx
// 기본 사용법
<CJAIChatBubble />

// 커스텀 위치
<CJAIChatBubble position="bottom-left" />

// 커스텀 메시지 핸들러
<CJAIChatBubble 
  position="bottom-right"
  onSendMessage={async (message) => {
    // API 호출
    const response = await fetch('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message })
    });
    const data = await response.json();
    return data.reply;
  }}
/>

// 추가 스타일링
<CJAIChatBubble 
  className="z-[100]"
  position="top-right"
  onSendMessage={handleAIMessage}
/>
```

### 상태 관리
```typescript
// 채팅 상태
const [isOpen, setIsOpen] = useState(false);
const [messages, setMessages] = useState<Message[]>([]);
const [inputValue, setInputValue] = useState('');
const [isLoading, setIsLoading] = useState(false);

// 메시지 전송 플로우
const handleSendMessage = async () => {
  // 1. 사용자 메시지 추가
  const userMessage = { id: Date.now().toString(), text: inputValue, sender: 'user', timestamp: new Date() };
  setMessages(prev => [...prev, userMessage]);
  
  // 2. 타이핑 인디케이터 표시
  const typingMessage = { id: 'typing', text: '...', sender: 'ai', timestamp: new Date(), isTyping: true };
  setMessages(prev => [...prev, typingMessage]);
  
  // 3. API 호출
  try {
    const response = await onSendMessage(inputValue);
    setMessages(prev => {
      const filtered = prev.filter(m => m.id !== 'typing');
      return [...filtered, { id: Date.now().toString(), text: response, sender: 'ai', timestamp: new Date() }];
    });
  } catch (error) {
    // 에러 처리
  }
};
```

---

## 🎯 사용 예시

### 완전한 대시보드 구성
```tsx
import { TokenBalanceWidget } from './components/TokenBalanceWidget';
import { CJChatBubble } from './components/CJChatBubble';
import { CJAIChatBubble } from './components/CJAIChatBubble';

export default function Dashboard() {
  const [tokenData, setTokenData] = useState({
    amount: 1234567,
    status: 'normal' as const,
    change: 'increase' as const
  });

  const handleAIMessage = async (message: string) => {
    // AI 응답 로직
    return `AI 응답: ${message}`;
  };

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      {/* 토큰 위젯 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <TokenBalanceWidget
          amount={tokenData.amount}
          status={tokenData.status}
          change={tokenData.change}
        />
      </div>

      {/* 메시지 피드 */}
      <div className="space-y-4 mb-8">
        <CJChatBubble
          message="환영합니다! 오늘도 좋은 하루 되세요!"
          avatarMood="happy"
          state="idle"
          showVoiceToggle={true}
        />
        
        <CJChatBubble
          message="현재 시스템 상태를 확인하고 있습니다..."
          avatarMood="normal"
          state="typing"
        />
      </div>

      {/* 플로팅 채팅 */}
      <CJAIChatBubble
        position="bottom-right"
        onSendMessage={handleAIMessage}
      />
    </div>
  );
}
```

### 실시간 업데이트 예시
```tsx
// 웹소켓을 통한 실시간 토큰 업데이트
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8080');
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'token_update') {
      setTokenData(prev => ({
        ...prev,
        amount: data.amount,
        status: data.amount < 100000 ? 'critical' : data.amount < 500000 ? 'warning' : 'normal',
        change: data.amount > prev.amount ? 'increase' : 'decrease'
      }));
    }
  };

  return () => ws.close();
}, []);

// AI 상태 변화에 따른 메시지 업데이트
const [currentMessage, setCurrentMessage] = useState('');
const [aiState, setAiState] = useState<'idle' | 'typing' | 'speaking'>('idle');

const simulateAIResponse = async () => {
  setAiState('typing');
  await new Promise(resolve => setTimeout(resolve, 2000));
  setCurrentMessage('답변이 준비되었습니다!');
  setAiState('speaking');
  await new Promise(resolve => setTimeout(resolve, 3000));
  setAiState('idle');
};
```

---

## 🎨 커스터마이징 가이드

### 테마 커스터마이징
```typescript
// 커스텀 테마 생성
const customTheme = {
  colors: {
    primary: '#6366f1',
    secondary: '#8b5cf6',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444'
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem'
  },
  borderRadius: {
    sm: '0.25rem',
    md: '0.5rem',
    lg: '0.75rem',
    xl: '1rem'
  }
};

// 테마 적용 예시
<TokenBalanceWidget
  amount={1000000}
  className="bg-purple-500/10 border-purple-500/30"
  style={{
    '--token-normal': customTheme.colors.primary,
    '--token-warning': customTheme.colors.warning,
    '--token-critical': customTheme.colors.error
  }}
/>
```

### 애니메이션 커스터마이징
```typescript
// 커스텀 애니메이션 설정
const customAnimations = {
  duration: {
    fast: 0.2,
    normal: 0.3,
    slow: 0.5
  },
  easing: {
    smooth: [0.4, 0, 0.2, 1],
    bounce: [0.68, -0.55, 0.265, 1.55],
    spring: { type: "spring", stiffness: 100, damping: 15 }
  }
};

// 애니메이션 적용
<motion.div
  initial={{ opacity: 0, scale: 0.8 }}
  animate={{ opacity: 1, scale: 1 }}
  transition={customAnimations.easing.spring}
>
  <CJChatBubble message="커스텀 애니메이션 테스트" />
</motion.div>
```

### 반응형 커스터마이징
```css
/* 커스텀 브레이크포인트 */
@media (max-width: 480px) {
  .token-widget {
    padding: 1rem;
    margin: 0 0.5rem;
  }
  
  .chat-bubble {
    max-width: calc(100vw - 2rem);
    font-size: 0.875rem;
  }
}

@media (min-width: 1440px) {
  .token-widget {
    max-width: 32rem;
  }
  
  .chat-bubble {
    max-width: 24rem;
  }
}
```

### 접근성 커스터마이징
```tsx
// 고대비 모드 지원
const useHighContrast = () => {
  const [highContrast, setHighContrast] = useState(false);
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-contrast: high)');
    setHighContrast(mediaQuery.matches);
    
    const handler = (e: MediaQueryListEvent) => setHighContrast(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);
  
  return highContrast;
};

// 사용 예시
const MyComponent = () => {
  const highContrast = useHighContrast();
  
  return (
    <TokenBalanceWidget
      amount={1000000}
      className={highContrast ? 'contrast-high' : 'contrast-normal'}
    />
  );
};
```

---

*이 문서는 각 컴포넌트의 상세한 사용법과 커스터마이징 방법을 제공합니다. 추가 질문이나 요구사항이 있으시면 언제든 문의해 주세요.*