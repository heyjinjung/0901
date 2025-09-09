# 🔞 Adult Content & Token-Driven Reward System

## 4.1. 개요 🎯

04_adult_rewards_en.md
🔞 Adult Content & Token-Driven Reward System
4.1. Overview
Use adult content unlock as a psychological reward (dopamine loop).

Cyber tokens are F2P-only currency, obtainable exclusively from the corporate site.

Unlock adult content by spending cyber tokens via in-app games (slots/roulette/gacha).

If tokens run out, users are directed to the corporate site, strengthening retention loops.

Key Elements
Unlock Stages:

Stage 1 (Teaser): Blurred image (200 tokens)

Stage 2 (Partial Reveal): Upper body partial nudity (500 tokens)

Stage 3 (Full Reveal): Full adult content (1,000 tokens)

Variable-Ratio Reward:

Gacha pull yields "content unlock ticket" at low probability (0.5–2%)

Limited-Time Offers:

Example: Weekend 24h event → Stage 1 unlock costs 150 tokens

4.2. Data Model & DB Table
adult_content (PostgreSQL)

Column	Type	Description
id	SERIAL (PK)	Unique ID
stage	INTEGER	Stage number (1,2,3)
name	VARCHAR	Ex: "Stage 1: Teaser"
description	VARCHAR	Stage description
thumbnail_url	VARCHAR	Blurred thumbnail URL
media_url	VARCHAR	Full image/video URL
required_segment_level	INTEGER	User segment level (Whale=3, etc.)
base_token_cost	INTEGER	Tokens to unlock (200/500/1000)
flash_offer_cost	INTEGER	Discounted token amount (for events)

user_rewards

Column	Type	Description
id	SERIAL (PK)	Unique ID
user_id	INTEGER	FK: users.id
reward_type	VARCHAR(50)	Ex: "CONTENT_UNLOCK", "TOKEN_TICKET"
reward_value	VARCHAR(255)	Ex: "Stage1", "TicketStage2"
awarded_at	TIMESTAMP	When awarded
trigger_action_id	INTEGER	FK: user_actions.id (optional)

4.3. Unlock Logic (FastAPI)
Endpoint: POST /api/unlock

Parameters: user_id, desired_stage

Flow:

Check user and segment level.

Check token balance (deduct on unlock).

If not enough tokens, HTTP 402.

Record unlock in user_rewards.

Return: Unlocked media URL, tokens left, success message.

4.4. Gacha / Ticket System
Endpoint: POST /api/gacha

Spend 50 tokens for a random chance at ticket or coins.

"CONTENT_TICKET" for Stage 1/2/3 possible at different weights.

4.5. Flash Offer API
Endpoint: GET /api/flash_offer

Returns: Discounted unlock cost, time remaining

4.6. Token Conversion & Corporate Integration
Earn tokens from the corporate site (quizzes, events, purchases)

Spend tokens in the app for unlocks or gacha

Insufficient tokens → direct user to main site for more



### 목표

성인 콘텐츠 언락을 심리적 보상으로 사용하여 도파민 분비를 자극

사이버 토큰을 "본사 사이트에서만 획득 가능"한 F2P 재화로 설정

앱 내 게임(슬롯/룰렛/가챠)에서 사이버 토큰을 소모하여 성인 콘텐츠를 Unlock

부족 시 본사 사이트 유도 → "본사 ↔ 앱" 간 리텐션 고리 강화

### 핵심 요소 🌟

#### Stages (단계별 언락)

- **Stage 1 (Teaser):** 
  - 블러 처리된 이미지
  - 사이버 토큰 200개 소모

- **Stage 2 (Partial Reveal):** 
  - 상의 벗고 부분 노출
  - 사이버 토큰 500개 소모

- **Stage 3 (Full Reveal):** 
  - 전체 성인 콘텐츠 언락
  - 사이버 토큰 1,000개 소모

#### Variable-Ratio Reward

- 가챠 Pull에서 "성인 콘텐츠 언락 티켓" 낮은 확률로 획득 (0.5%–2%)
- 티켓 획득 시 특정 단계 언락 시도 (Stage 1~3 확률 다르게 적용)

#### Limited-Time Offers

- 주말 이벤트: "이번 주말 24시간 한정 → Stage 1 언락 비용 150토큰"
- 긴박감(Scarcity) 유발

#### Integration Flow

```
사용자(앱) ──> 슬롯/룰렛/가챠 ─(토큰 소모)─> 언락 시도 ─> 성공 시 Reward
                                                │
                                                └─ 실패 시 "다시 도전" → 소량 토큰 소모
```

## 4.2. Data Model & DB 테이블

### 4.2.1. adult_content 테이블 (PostgreSQL)

| Column                   | Type            | Description                                       |
|--------------------------|-----------------|---------------------------------------------------|
| id                       | SERIAL (PK)     | 고유 ID                                           |
| stage                     | INTEGER         | 단계 번호 (1, 2, 3)                              |
| name                     | VARCHAR(100)    | 예: "Stage 1: Teaser"                            |
| description              | VARCHAR(255)    | 단계별 설명                                      |
| thumbnail_url            | VARCHAR(255)    | 블러 처리된 썸네일 URL                          |
| media_url                | VARCHAR(255)    | 풀 해상도 이미지/동영상 URL                     |
| required_segment_level   | INTEGER         | 필요한 최소 세그먼트 레벨 (Whale=3, High Engaged=2, Medium=1) |
| base_token_cost         | INTEGER         | 기본 소모 토큰 수 (Stage 1=200, Stage 2=500, Stage 3=1000) |
| flash_offer_cost         | INTEGER         | 한정 이벤트 시 소모 토큰 수(옵션)               |

### 4.2.2. user_rewards 테이블

| Column             | Type            | Description                                       |
|--------------------|-----------------|---------------------------------------------------|
| id                 | SERIAL (PK)     | 고유 ID                                           |
| user_id            | INTEGER         | FK: users.id                                     |
| reward_type        | VARCHAR(50)     | "CONTENT_UNLOCK", "TOKEN_TICKET", "COIN", "BADGE" 등 |
| reward_value       | VARCHAR(255)    | 예: "Stage1", "TicketStage2", "50_COIN"         |
| awarded_at         | TIMESTAMP       | 지급 시각                                        |
| trigger_action_id  | INTEGER (Nullable) | 언락 시도와 연결된 user_actions.id (선택적)    |

## 4.3. Unlock Logic (FastAPI)

### 4.3.1. 기본 언락 엔드포인트

```python
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db, get_redis
from .models import User, AdultContent, UserReward
from datetime import datetime

app = FastAPI()

@app.post("/api/unlock", response_model=dict)
def unlock_adult_content(user_id: int, desired_stage: int, db=Depends(get_db), redis=Depends(get_redis)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. 요구되는 세그먼트 레벨 확인
    content = db.query(AdultContent).filter(AdultContent.stage == desired_stage).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content stage not found")

    user_segment = user.segment.rfm_group
    seg_level_map = {"Low":1, "Medium":2, "High Engaged":2, "Whale":3}
    user_level = seg_level_map.get(user_segment, 0)
    if user_level < content.required_segment_level:
        raise HTTPException(status_code=403, detail="Segment level too low")

    # 2. 토큰 잔고 확인
    token_balance = int(redis.get(f"user:{user_id}:cyber_token_balance") or 0)
    cost = content.base_token_cost
    # Flash Offer 적용 여부(파라미터 추가 가능)
    # cost = content.flash_offer_cost if is_flash_offer_active(desired_stage) else cost

    if token_balance < cost:
        raise HTTPException(status_code=402, detail="Insufficient cyber tokens")

    # 3. 토큰 차감
    redis.decrby(f"user:{user_id}:cyber_token_balance", cost)

    # 4. 언락 Reward 기록
    new_reward = UserReward(
      user_id=user_id,
      reward_type="CONTENT_UNLOCK",
      reward_value=f"Stage{desired_stage}",
      awarded_at=datetime.utcnow(),
      trigger_action_id=None
    )
    db.add(new_reward)
    db.commit()

    # 5. 응답
    return {
      "stage": desired_stage,
      "media_url": content.media_url,
      "remaining_tokens": int(redis.get(f"user:{user_id}:cyber_token_balance")),
      "message": f"Stage {desired_stage} 언락 성공! 남은 토큰: {int(redis.get(f'user:{user_id}:cyber_token_balance'))}"
    }
```

핵심 변경점:

- desired_stage 파라미터로 클라이언트가 언락을 요청할 단계 지정 (1, 2, 3)
- 세그먼트 레벨 체크
- 사이버 토큰 잔고 확인 후 차감
- 토큰 부족 시 HTTP 402 에러 반환 (앱 내 결제 또는 본사 사이트 유도)

## 4.4. Gacha / Ticket 시스템

### 4.4.1. Gacha Pull 로직 (/api/gacha)

```python
from fastapi import APIRouter, Depends, HTTPException
from .database import get_db, get_redis
from .models import User, UserReward
import random
from datetime import datetime

router = APIRouter()

# 가챠 확률 테이블 (예시)
gacha_table = [
    {"weight": 5,  "result": {"type":"CONTENT_TICKET","stage":3}},
    {"weight": 20, "result": {"type":"CONTENT_TICKET","stage":2}},
    {"weight": 50, "result": {"type":"CONTENT_TICKET","stage":1}},
    {"weight": 25, "result": {"type":"COIN","amount":100}}
]

@router.post("/api/gacha", response_model=dict)
def spin_gacha(user_id: int, db=Depends(get_db), redis=Depends(get_redis)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. 토큰 차감(예: 가챠 50토큰)
    token_balance = int(redis.get(f"user:{user_id}:cyber_token_balance") or 0)
    if token_balance < 50:
        raise HTTPException(status_code=402, detail="Insufficient cyber tokens for gacha")

    redis.decrby(f"user:{user_id}:cyber_token_balance", 50)

    # 2. 가챠 확률 랜덤 선택
    total_weight = sum(entry["weight"] for entry in gacha_table)
    rand = random.uniform(0, total_weight)
    for entry in gacha_table:
        if rand < entry["weight"]:
            result = entry["result"]
            break
        rand -= entry["weight"]

    # 3. 결과 처리
    if result["type"] == "CONTENT_TICKET":
        # 티켓 보상 기록 (stage 별 티켓)
        new_reward = UserReward(
            user_id=user_id,
            reward_type="CONTENT_TICKET",
            reward_value=f"TicketStage{result['stage']}",
            awarded_at=datetime.utcnow(),
            trigger_action_id=None
        )
        db.add(new_reward)
        db.commit()
        return {
            "result": "ticket",
            "stage": result["stage"],
            "message": f"Stage {result['stage']} 티켓 획득! 토큰 남음: {int(redis.get(f'user:{user_id}:cyber_token_balance'))}"
        }
    else:
        # 코인 보상 기록
        amount = result["amount"]
        new_reward = UserReward(
            user_id=user_id,
            reward_type="COIN",
            reward_value=str(amount),
            awarded_at=datetime.utcnow(),
            trigger_action_id=None
        )
        db.add(new_reward)
        db.commit()
        # 토큰 대신 코인(게임 내 메인 화폐) 지급 로직
        return {
            "result": "coin",
            "amount": amount,
            "message": f"{amount} 코인 획득! 토큰 남음: {int(redis.get(f'user:{user_id}:cyber_token_balance'))}"
        }
```

주요 특징:

- 50 토큰 소모 후 잔고 차감
- 저확률(5%)로 Stage 3 티켓, 중확률(20%)로 Stage 2 티켓 등 Variable‐Ratio Reward 적용
- 티켓 획득 시 /api/unlock 호출 없이, "티켓 → 추후 직접 언락" 플로우 (UX 상에서 "티켓 사용" 버튼 노출)

## 4.5. Flash Offer / Limited-Time Event

Flash Offer 예시 엔드포인트 (/api/flash_offer)

```python
from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from .models import AdultContent

router = APIRouter()

@router.get("/api/flash_offer", response_model=dict)
def get_flash_offer():
    now = datetime.utcnow()
    # 주말(토요일 00:00 UTC ~ 일요일 23:59 UTC) 여부 체크
    if now.weekday() in [5, 6]:
        # Stage1 비용 200 → 150으로 할인
        content = db.query(AdultContent).filter(AdultContent.stage == 1).first()
        return {
            "stage": 1,
            "discounted_cost": 150,
            "expires_at": (datetime(now.year, now.month, now.day, 23, 59, 59) + timedelta(days=(6 - now.weekday() if now.weekday()<=6 else 0))).isoformat(),
            "message": "주말 한정! Stage 1 언락 비용 150토큰으로 할인 중!"
        }
    else:
        return {"flash_active": False}
```

Front-End UX:

- 대시보드 상단 Flash Offer 배너 노출
- "지금 언락" 버튼 클릭 → /api/unlock?desired_stage=1&cost=150 호출

## 4.6. Token Conversion & Corporate Site 연동

사이버 토큰 획득 경로:

- 본사 사이트 활동:
  - 로그인, 퀴즈, 이벤트 참여 시 EARN_CYBER_TOKENS 액션 기록
  - Redis에 즉시 반영 → "앱 내 토큰 잔고" 증가 → 푸시 알림 "본사에서 500토큰 획득"

- 앱 내 게임 플레이:
  - 게임 승리 시 /api/feedback → token_delta
  - 가챠/스핀 시 /api/gacha 로 코인 or 티켓 획득 → 토큰 차감

- 현금 결제로 토큰 구매:
  - "충전" 버튼 클릭 → In-App Purchase 또는 PG 연동 → /api/purchase →
  SPEND_CASH_FOR_TOKENS 액션 실행 → Redis 토큰 잔고 증액

- 본사 사이트 리텐션 강화:
  - 앱에서 토큰 부족 시 UI에 "본사 사이트에서 100토큰만 더 모아오세요" 호출
  - "Visit Corporate Site" 버튼 → https://corporate-site.com?userId={user_id}
  - 리디렉션 시 site_visits 테이블에 기록 + site_rewards 테이블에 이벤트 획득 토큰 기록

## 4.7. 요약

"사이버 토큰 = 본사 사이트 보상" 을 핵심으로,

앱 내 소비(콘텐츠 언락 & 가챠) → 본사 사이트 재방문 → 토큰 획득 → 앱 내 소비 …

이러한 순환 구조를 통해 본사 사이트 리텐션 상승과 앱 내 과금 전환율 극대화를 동시에 달성

# 🔞 Adult Content & Token-Driven Reward System (English Translation)

## 4.1. Overview 🎯

### Objective

Use adult content unlock as a psychological reward to stimulate dopamine release.

Set cyber tokens as F2P currency that can only be obtained on the corporate site.

Unlock adult content by spending cyber tokens in in-app games (slots/roulette/gacha).

If tokens are insufficient, guide users to the corporate site → strengthen the retention loop between "corporate site ↔ app".

### Key Elements 🌟

#### Stages (Stepwise Unlock)

- **Stage 1 (Teaser):**
  - Blurred image
  - Consumes 200 cyber tokens
- **Stage 2 (Partial Reveal):**
  - Partial nudity (upper body)
  - Consumes 500 cyber tokens
- **Stage 3 (Full Reveal):**
  - Full adult content unlock
  - Consumes 1,000 cyber tokens

#### Variable-Ratio Reward

- Low probability (0.5%–2%) to obtain an "adult content unlock ticket" from gacha pulls
- When a ticket is obtained, attempt to unlock a specific stage (different probabilities for Stage 1~3)

#### Limited-Time Offers

- Weekend event: "This weekend, 24-hour limited → Stage 1 unlock costs 150 tokens"
- Induce urgency (Scarcity)

#### Integration Flow

```
User (App) ──> Slot/Roulette/Gacha ─(Token Spend)─> Unlock Attempt ─> Reward on Success
                                               │
                                               └─ On Failure: "Try Again" → Small token spend
```

## 4.2. Data Model & DB Tables

### 4.2.1. adult_content Table (PostgreSQL)

| Column                 | Type          | Description                                                      |
|------------------------|---------------|------------------------------------------------------------------|
| id                     | SERIAL (PK)   | Unique ID                                                        |
| stage                  | INTEGER       | Stage number (1, 2, 3)                                           |
| name                   | VARCHAR(100)  | e.g., "Stage 1: Teaser"                                          |
| description            | VARCHAR(255)  | Description per stage                                            |
| thumbnail_url          | VARCHAR(255)  | Blurred thumbnail URL                                            |
| media_url              | VARCHAR(255)  | Full-resolution image/video URL                                  |
| required_segment_level | INTEGER       | Minimum segment level required (Whale=3, High Engaged=2, Medium=1)|
| base_token_cost        | INTEGER       | Base token cost (Stage 1=200, Stage 2=500, Stage 3=1000)         |
| flash_offer_cost       | INTEGER       | Token cost for limited event (optional)                          |

### 4.2.2. user_rewards Table

| Column            | Type          | Description                                                      |
|-------------------|---------------|------------------------------------------------------------------|
| id                | SERIAL (PK)   | Unique ID                                                        |
| user_id           | INTEGER       | FK: users.id                                                     |
| reward_type       | VARCHAR(50)   | "CONTENT_UNLOCK", "TOKEN_TICKET", "COIN", "BADGE", etc.         |
| reward_value      | VARCHAR(255)  | e.g., "Stage1", "TicketStage2", "50_COIN"                      |
| awarded_at        | TIMESTAMP     | Time awarded                                                     |
| trigger_action_id | INTEGER (Nullable) | Linked user_actions.id for unlock attempt (optional)         |

## 4.3. Unlock Logic (FastAPI)

### 4.3.1. Basic Unlock Endpoint

```python
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import get_db, get_redis
from .models import User, AdultContent, UserReward
from datetime import datetime

app = FastAPI()

@app.post("/api/unlock", response_model=dict)
def unlock_adult_content(user_id: int, desired_stage: int, db=Depends(get_db), redis=Depends(get_redis)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. 요구되는 세그먼트 레벨 확인
    content = db.query(AdultContent).filter(AdultContent.stage == desired_stage).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content stage not found")

    user_segment = user.segment.rfm_group
    seg_level_map = {"Low":1, "Medium":2, "High Engaged":2, "Whale":3}
    user_level = seg_level_map.get(user_segment, 0)
    if user_level < content.required_segment_level:
        raise HTTPException(status_code=403, detail="Segment level too low")

    # 2. 토큰 잔고 확인
    token_balance = int(redis.get(f"user:{user_id}:cyber_token_balance") or 0)
    cost = content.base_token_cost
    # Flash Offer 적용 여부(파라미터 추가 가능)
    # cost = content.flash_offer_cost if is_flash_offer_active(desired_stage) else cost

    if token_balance < cost:
        raise HTTPException(status_code=402, detail="Insufficient cyber tokens")

    # 3. 토큰 차감
    redis.decrby(f"user:{user_id}:cyber_token_balance", cost)

    # 4. 언락 Reward 기록
    new_reward = UserReward(
      user_id=user_id,
      reward_type="CONTENT_UNLOCK",
      reward_value=f"Stage{desired_stage}",
      awarded_at=datetime.utcnow(),
      trigger_action_id=None
    )
    db.add(new_reward)
    db.commit()

    # 5. 응답
    return {
      "stage": desired_stage,
      "media_url": content.media_url,
      "remaining_tokens": int(redis.get(f"user:{user_id}:cyber_token_balance")),
      "message": f"Stage {desired_stage} 언락 성공! 남은 토큰: {int(redis.get(f'user:{user_id}:cyber_token_balance'))}"
    }
```

Key changes:

- Client specifies the stage to unlock via the desired_stage parameter (1, 2, 3)
- Check segment level
- Check and deduct cyber token balance
- If tokens are insufficient, return HTTP 402 error (guide to in-app purchase or corporate site)

## 4.4. Gacha / Ticket 시스템

### 4.4.1. Gacha Pull 로직 (/api/gacha)

```python
from fastapi import APIRouter, Depends, HTTPException
from .database import get_db, get_redis
from .models import User, UserReward
import random
from datetime import datetime

router = APIRouter()

# 가챠 확률 테이블 (예시)
gacha_table = [
    {"weight": 5,  "result": {"type":"CONTENT_TICKET","stage":3}},
    {"weight": 20, "result": {"type":"CONTENT_TICKET","stage":2}},
    {"weight": 50, "result": {"type":"CONTENT_TICKET","stage":1}},
    {"weight": 25, "result": {"type":"COIN","amount":100}}
]

@router.post("/api/gacha", response_model=dict)
def spin_gacha(user_id: int, db=Depends(get_db), redis=Depends(get_redis)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 1. 토큰 차감(예: 가챠 50토큰)
    token_balance = int(redis.get(f"user:{user_id}:cyber_token_balance") or 0)
    if token_balance < 50:
        raise HTTPException(status_code=402, detail="Insufficient cyber tokens for gacha")

    redis.decrby(f"user:{user_id}:cyber_token_balance", 50)

    # 2. 가챠 확률 랜덤 선택
    total_weight = sum(entry["weight"] for entry in gacha_table)
    rand = random.uniform(0, total_weight)
    for entry in gacha_table:
        if rand < entry["weight"]:
            result = entry["result"]
            break
        rand -= entry["weight"]

    # 3. 결과 처리
    if result["type"] == "CONTENT_TICKET":
        # 티켓 보상 기록 (stage 별 티켓)
        new_reward = UserReward(
            user_id=user_id,
            reward_type="CONTENT_TICKET",
            reward_value=f"TicketStage{result['stage']}",
            awarded_at=datetime.utcnow(),
            trigger_action_id=None
        )
        db.add(new_reward)
        db.commit()
        return {
            "result": "ticket",
            "stage": result["stage"],
            "message": f"Stage {result['stage']} 티켓 획득! 토큰 남음: {int(redis.get(f'user:{user_id}:cyber_token_balance'))}"
        }
    else:
        # 코인 보상 기록
        amount = result["amount"]
        new_reward = UserReward(
            user_id=user_id,
            reward_type="COIN",
            reward_value=str(amount),
            awarded_at=datetime.utcnow(),
            trigger_action_id=None
        )
        db.add(new_reward)
        db.commit()
        # 토큰 대신 코인(게임 내 메인 화폐) 지급 로직
        return {
            "result": "coin",
            "amount": amount,
            "message": f"{amount} 코인 획득! 토큰 남음: {int(redis.get(f'user:{user_id}:cyber_token_balance'))}"
        }
```

This cyclical structure maximizes both corporate site retention and in-app monetization conversion.