# VIP 게임 플랫폼 API 명세서

## 📋 **API 엔드포인트 개요**

### 🔐 **인증 시스템**
| Method | Endpoint | 설명 | 우선순위 |
|--------|----------|------|----------|
| POST | `/auth/invite-code` | 초대코드 검증 | 🔥 최우선 |
| POST | `/auth/register` | 회원가입 (닉네임 + 비밀번호) | 🔥 최우선 |
| POST | `/auth/login` | 로그인 | 🔥 최우선 |
| POST | `/auth/refresh` | 토큰 갱신 | ⚡ 우선 |

### 💎 **토큰 시스템**
| Method | Endpoint | 설명 | 우선순위 |
|--------|----------|------|----------|
| GET | `/tokens/balance` | 토큰 잔고 조회 | 🔥 최우선 |
| POST | `/tokens/charge` | 토큰 충전 (외부 결제) | 🔥 최우선 |
| GET | `/tokens/history` | 토큰 사용 내역 | ⚡ 우선 |

### 🎮 **게임 시스템**
| Method | Endpoint | 설명 | 우선순위 |
|--------|----------|------|----------|
| POST | `/games/slot-machine/spin` | 슬롯머신 게임 플레이 | 🔥 최우선 |
| POST | `/games/roulette/bet` | 룰렛 베팅 | ⚡ 우선 |
| POST | `/games/gacha/draw` | 가챠 뽑기 | ⚡ 우선 |
| POST | `/games/rock-paper-scissors/play` | 가위바위보 | ⚡ 우선 |
| GET | `/games/history` | 게임 기록 | 📈 나중에 |

### 🤖 **CJ AI 시스템**
| Method | Endpoint | 설명 | 우선순위 |
|--------|----------|------|----------|
| POST | `/ai/chat` | CJ AI 채팅 | 🔥 최우선 |
| POST | `/ai/emotion-feedback` | 감정 분석 피드백 | ⚡ 우선 |
| GET | `/ai/character-settings` | AI 캐릭터 설정 | 📈 나중에 |

### 🔞 **성인 콘텐츠**
| Method | Endpoint | 설명 | 우선순위 |
|--------|----------|------|----------|
| GET | `/content/preview` | 콘텐츠 미리보기 목록 | ⚡ 우선 |
| POST | `/content/unlock` | 콘텐츠 언락 (토큰 소비) | ⚡ 우선 |
| GET | `/content/{id}` | 언락된 콘텐츠 조회 | ⚡ 우선 |
| POST | `/content/rating` | 만족도 평가 | 📈 나중에 |

### 🏆 **리워드/미션**
| Method | Endpoint | 설명 | 우선순위 |
|--------|----------|------|----------|
| GET | `/missions/daily` | 데일리 미션 목록 | ⚡ 우선 |
| POST | `/missions/complete` | 미션 완료 처리 | ⚡ 우선 |
| GET | `/rewards/available` | 받을 수 있는 보상 | ⚡ 우선 |
| POST | `/rewards/claim` | 보상 받기 | ⚡ 우선 |

### 👤 **사용자 프로필**
| Method | Endpoint | 설명 | 우선순위 |
|--------|----------|------|----------|
| GET | `/user/profile` | 프로필 정보 | 📈 나중에 |
| PUT | `/user/profile` | 프로필 수정 | 📈 나중에 |
| GET | `/user/statistics` | 게임 통계 | 📈 나중에 |

---

## 🔥 **최우선 API 상세 명세 (MVP용)**

### 1. 초대코드 검증
```http
POST /auth/invite-code
Content-Type: application/json

{
  "invite_code": "VIP2025ABCD"
}
```

**응답 성공 (200)**:
```json
{
  "success": true,
  "message": "초대코드가 유효합니다",
  "data": {
    "code_valid": true,
    "remaining_uses": 5
  }
}
```

**응답 실패 (400)**:
```json
{
  "success": false,
  "message": "유효하지 않은 초대코드입니다",
  "error_code": "INVALID_INVITE_CODE"
}
```

### 2. 회원가입
```http
POST /auth/register
Content-Type: application/json

{
  "invite_code": "VIP2025ABCD",
  "nickname": "게이머123",
  "password": "securepass123"
}
```

**응답 성공 (201)**:
```json
{
  "success": true,
  "message": "회원가입이 완료되었습니다",
  "data": {
    "user_id": 1234,
    "nickname": "게이머123",
    "welcome_tokens": 200,
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

### 3. 로그인
```http
POST /auth/login
Content-Type: application/json

{
  "nickname": "게이머123",
  "password": "securepass123"
}
```

**응답 성공 (200)**:
```json
{
  "success": true,
  "message": "로그인 성공",
  "data": {
    "user_id": 1234,
    "nickname": "게이머123",
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
  }
}
```

### 4. 토큰 잔고 조회
```http
GET /tokens/balance
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**응답 성공 (200)**:
```json
{
  "success": true,
  "data": {
    "balance": 1250,
    "currency": "💎",
    "last_updated": "2025-06-18T10:30:00Z"
  }
}
```

### 5. 슬롯머신 게임 플레이
```http
POST /games/slot-machine/spin
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "bet_amount": 20
}
```

**응답 성공 (200)**:
```json
{
  "success": true,
  "message": "스핀 완료!",
  "data": {
    "game_id": "slot_12345",
    "bet_amount": 20,
    "result": {
      "reels": ["🍒", "🍒", "🍒"],
      "is_win": true,
      "payout": 100,
      "win_type": "cherry_triple"
    },
    "new_balance": 1330,
    "emotion_feedback": {
      "emotion": "excitement",
      "message": "대박! 세 개가 모두 맞았네요! 🎉"
    }
  }
}
```

### 6. CJ AI 채팅
```http
POST /ai/chat
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "message": "안녕 CJ!",
  "context": {
    "current_activity": "slot_machine",
    "recent_emotion": "excitement"
  }
}
```

**응답 성공 (200)**:
```json
{
  "success": true,
  "data": {
    "response": "안녕하세요! 슬롯머신에서 대박 나셨군요! 😍 다음엔 룰렛도 한번 도전해보시는 건 어떠세요?",
    "emotion_detected": "happy",
    "suggestions": [
      "룰렛 게임 해보기",
      "데일리 미션 확인하기"
    ]
  }
}
```

---

## 🚨 **에러 응답 표준 포맷**

**인증 오류 (401)**:
```json
{
  "success": false,
  "message": "인증이 필요합니다",
  "error_code": "UNAUTHORIZED",
  "details": "토큰이 만료되었거나 유효하지 않습니다"
}
```

**토큰 부족 (400)**:
```json
{
  "success": false,
  "message": "토큰이 부족합니다",
  "error_code": "INSUFFICIENT_TOKENS",
  "details": {
    "required": 20,
    "current": 15,
    "shortage": 5
  }
}
```

**서버 오류 (500)**:
```json
{
  "success": false,
  "message": "서버 오류가 발생했습니다",
  "error_code": "INTERNAL_SERVER_ERROR",
  "request_id": "req_12345"
}
```

---

## 🔧 **프론트엔드 API 호출 가이드**

### **API 클라이언트 설정**
```javascript
// utils/apiClient.js
import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 토큰 자동 추가
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 에러 응답 처리
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 시 로그인 페이지로 이동
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### **사용 예시**
```javascript
// 슬롯머신 스핀
const spinSlotMachine = async (betAmount) => {
  try {
    const response = await apiClient.post('/games/slot-machine/spin', {
      bet_amount: betAmount
    });
    
    return response.data;
  } catch (error) {
    if (error.response?.data?.error_code === 'INSUFFICIENT_TOKENS') {
      // 토큰 부족 처리
      showTokenChargeModal();
    }
    throw error;
  }
};
```

---

이제 **실제 구현 가능한 API 명세서**가 완성되었습니다! 

**다음 단계**: 이 명세서를 기반으로 어떤 컴포넌트부터 구현하시겠습니까?
1. 토큰 헤더 컴포넌트
2. 로그인/회원가입 페이지  
3. 슬롯머신 토큰 연동
