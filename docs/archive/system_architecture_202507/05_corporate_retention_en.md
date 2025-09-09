# 🤝 Corporate Site Retention & Cross-Platform Reward System

## 5.1. 목표 🎯

05_corporate_retention_en.md
🤝 Corporate Site Retention & Cross-Platform Reward System
5.1. Objective
Build a strong retention loop between the app and the corporate site

Use "cyber tokens" as the main cross-platform reward

Maximize cross-participation, cross-revenue, and dopamine triggers at each transition

5.2. Integrated Workflow
App → Corporate Site

Trigger: Low in-app tokens, flash offer ending, etc.

Show deep link: https://corporate-site.com/login?userId={user_id}&source=app_shortage

On landing: Quizzes/events grant 100–500 tokens; instant reward for login

Corporate Site → App

After reward on site (event, purchase): “Go to app for 300 tokens/free gacha.”

On app entry: Show animation, bonus gacha, push notification

5.3. Reward/Token Flow
Corporate site visits = 100–500 tokens instantly (updated in Redis, app push)

Purchases on site grant more tokens + app coupons

All tracked via site_visits, site_rewards, user_rewards

5.4. Analytics & Triggers
Scheduled batch jobs for reminder, token updates, etc.

Track inflow/outflow rates, retention loops

5.5. Dopamine Triggers Table
Trigger	Detail	Effect
Variable-Ratio Reward	Slot/gacha/roulette uncertainty	↑ Dopamine/repeat
Limited-Time Offer	Site events with countdown	Scarcity/Immediate Act
Social Proof	Leaderboard in app	Competition/Spending
Free Gacha Ticket	Free in-app gacha for site activity	App return





### 주요 목적

본사 사이트(Corporate Site)와 앱 간의 강력한 리텐션 사이클을 구축

- "사이버 토큰"을 본사 사이트 이용 보상으로 제공하여,
- 유저가 본사 사이트에 재방문하도록 유도
- 본사 사이트 활동을 통해 토큰을 획득하고 다시 앱 내 소비

### 핵심 전략 🌐

- 본사 사이트와 앱 간의 **교차 참여율** 및 **교차 매출** 극대화
- "행위중독 트리거"를 본사 사이트 ↔ 앱 전환 시점마다 적용하여 도파민 루프 강화

## 5.2. 통합 워크플로우 🔄

### 5.2.1. 앱 → 본사 사이트 (App to Corporate Site)

#### 트리거 사례:

- 앱 내 토큰 잔고 부족 알림 
  - "본사 사이트에서 100토큰만 더 모아오세요"

- Flash Offer 종료 임박 알림 
  - "본사 사이트 이벤트 30분 후 종료 → 지금 방문하면 추가 보너스"

#### Deep Link 메커니즘:

```
https://corporate-site.com/login?userId={user_id}&source=app_shortage
```

#### 본사 사이트 랜딩 페이지 (토큰 미션):

- "앱에서 부족한 토큰을 채워보세요!"
- 퀴즈 / 설문 / 이벤트 참여로 사이버 토큰 즉시 획득 (예: 100~500 토큰)

#### 자동 보상 메커니즘:
- 본사 사이트 로그인만으로 100토큰 보상
- Redis 즉시 토큰 잔고 증가
- 앱 푸시 알림: "본사 사이트에서 100토큰 획득! 지금 앱으로 돌아가서 사용하세요 🚀"

### 5.2.2. 본사 사이트 → 앱 (Corporate Site to App)

#### 트리거 사례:

- 본사 사이트 Flash Event 참여 후
  - "축하합니다! 300토큰 획득 → 앱에서 사용하세요"

- 본사 사이트에서 Purchase/Subscription 완료 시
  - "스페셜 쿠폰: 앱 내 가챠 1회 무료 제공"

#### 도파민 루프 강화:
- 본사에서 보상을 받은 직후 앱 진입 시
  - 화려한 애니메이션 + 사운드 + 무료 가챠 기회 제공
- 즉시 가챠 결과가 성공(티켓 획득) 시 Stage 2 언락까지 이어지는 몰입 루프

## 5.3. 보상 메커니즘 & 사이버 토큰 흐름 💰

### 5.3.1. 방문 보상
- 본사 사이트 방문으로 100~500 사이버 토큰 지급
- "앱 내에서 사용 가능한 토큰" 획득
- Redis 즉시 갱신 → 앱 푸시 알림

### 5.3.2. 사이트 활동 보상
- 본사 사이트 결제(현금) 완료 시
  - 300 사이버 토큰 지급 + "앱 내 Stage 2 언락 쿠폰"

- 본사 사이트 퀴즈/이벤트 참여 시
  - 참여 유형에 따라 100~200 사이버 토큰
  - "이번 달 참여 횟수"에 따라 추가 보너스 토큰

## 5.4. 분석 및 리텐션 추적 📊

### 5.4.1. 주요 테이블
| 테이블 | 설명 |
|--------|------|
| site_visits | 본사 사이트 방문 이력 |
| site_rewards | 본사 사이트에서 지급된 보상(토큰/쿠폰) 기록 |
| user_actions | 앱 내 모든 액션 기록 |
| user_rewards | 앱 내 보상 (콘텐츠 언락, 무료 가챠, 코인 등) |

### 5.4.2. 예약된 작업
- **일간 배치 (02시 UTC):**
  - RFM + 사이버 토큰 잔고 업데이트
  - 본사 사이트 방문자 중 "토큰 미사용" 사용자 대상 리마인더 발송

- **주간 분석 (일요일 자정):**
  - "본사 → 앱 유입률" 및 "앱 → 본사 재방문률" 지표 계산

## 5.5. 도파민 루프 및 중독 트리거 🧠

| 트리거 유형 | 상세 내용 | 기대 효과 |
|-------------|-----------|-----------|
| Variable-Ratio Reward | 슬롯/룰렛/가챠에서 "언제 당첨될지 모름" 긴장감 | 도파민 분비 ↑, 사용자 반복 플레이 유도 |
| Limited-Time Offer | 본사 사이트 주말 할인 이벤트 | 희소성 자극, 즉시 행동 유도 |
| Social Proof | 앱 내 리더보드 노출 | 경쟁심 자극, 과금 욕구 상승 |
| Free Gacha Ticket | 본사 사이트 이벤트 참여 시 앱 내 가챠 1회 무료 | 즉각적 보상 제공, 앱 복귀 유도 |

## 5.6. 요약 및 기대 효과 🚀

### 주요 성과
- **본사 사이트 리텐션 ↑**
  - "앱 내 토큰 부족" → "본사 사이트 방문" → "토큰 획득" → "앱 복귀" 순환 고리 완성

- **앱 내 과금 전환율 ↑**
  - 본사 사이트 획득 토큰으로 언락/가챠 시도 → 추가 토큰 부족 시 현금 결제 유도

- **지속적 개인화**
  - RFM + 심리 프로필 기반 추천 엔진으로 유입율 극대화

### 최종 목표
앱과 본사 사이트 간의 시너지를 통해 양쪽 플랫폼 모두 사용자 체류 시간 및 매출 증대

---

# 🤝 Corporate Site Retention & Cross-Platform Reward System (English Translation)

## 5.1. Objective 🎯

### Main Purpose

Build a strong retention cycle between the corporate site and the app.

- Provide "cyber tokens" as a reward for using the corporate site,
- Encourage users to revisit the corporate site
- Users earn tokens through corporate site activities and spend them again in the app

### Key Strategies 🌐

- Maximize **cross-participation** and **cross-revenue** between the corporate site and the app
- Apply "behavioral addiction triggers" at every transition between the corporate site and the app to reinforce the dopamine loop

## 5.2. Integrated Workflow 🔄

### 5.2.1. App → Corporate Site

#### Trigger Examples:

- In-app token shortage notification
  - "Collect 100 more tokens at the corporate site"
- Flash Offer ending soon notification
  - "Corporate site event ends in 30 minutes → Visit now for an extra bonus"

#### Deep Link Mechanism:

```
https://corporate-site.com/login?userId={user_id}&source=app_shortage
```

#### Corporate Site Landing Page (Token Mission):

- "Fill up your missing tokens from the app!"
- Instantly earn cyber tokens by participating in quizzes/surveys/events (e.g., 100~500 tokens)

#### Automatic Reward Mechanism:
- 100 tokens rewarded just for logging in to the corporate site
- Redis token balance updated instantly
- App push notification: "You earned 100 tokens at the corporate site! Return to the app and use them now 🚀"

### 5.2.2. Corporate Site → App

#### Trigger Examples:

- After participating in a corporate site flash event
  - "Congratulations! You earned 300 tokens → Use them in the app"
- After completing a purchase/subscription on the corporate site
  - "Special coupon: 1 free gacha in the app"

#### Dopamine Loop Reinforcement:
- When entering the app right after receiving a reward from the corporate site
  - Show flashy animation + sound + free gacha opportunity
- If the gacha result is a success (ticket obtained), the immersion loop continues up to Stage 2 unlock

## 5.3. Reward Mechanism & Cyber Token Flow 💰

### 5.3.1. Visit Rewards
- 100~500 cyber tokens given for visiting the corporate site
- "Tokens usable in the app" are obtained
- Redis updated instantly → app push notification

### 5.3.2. Site Activity Rewards
- After completing a purchase (cash) on the corporate site
  - 300 cyber tokens + "Stage 2 unlock coupon in the app"
- After participating in quizzes/events on the corporate site
  - 100~200 cyber tokens depending on activity type
  - Additional bonus tokens based on "number of participations this month"

## 5.4. Analytics & Retention Tracking 📊

### 5.4.1. Key Tables
| Table         | Description                                 |
|--------------|---------------------------------------------|
| site_visits  | Corporate site visit history                |
| site_rewards | Rewards (tokens/coupons) given on the site  |
| user_actions | All actions in the app                      |
| user_rewards | In-app rewards (content unlock, free gacha, coins, etc.) |

### 5.4.2. Scheduled Tasks
- **Daily batch (02:00 UTC):**
  - RFM + cyber token balance update
  - Send reminders to users who visited the corporate site but haven't used their tokens
- **Weekly analysis (Sunday midnight):**
  - Calculate "corporate site → app inflow rate" and "app → corporate site revisit rate"

## 5.5. Dopamine Loop & Addiction Triggers 🧠

| Trigger Type           | Details                                              | Expected Effect                                 |
|-----------------------|------------------------------------------------------|-------------------------------------------------|
| Variable-Ratio Reward | Tension of "not knowing when you'll win" in slots/roulette/gacha | ↑ Dopamine, encourages repeated play           |
| Limited-Time Offer    | Corporate site weekend discount event                | Stimulates scarcity, prompts immediate action   |
| Social Proof          | Leaderboard exposure in the app                      | Stimulates competition, increases spending urge |
| Free Gacha Ticket     | 1 free gacha in the app for participating in site events | Provides instant reward, encourages app return  |

## 5.6. Summary & Expected Effects 🚀

### Key Outcomes
- **Increased corporate site retention**
  - "In-app token shortage" → "Visit corporate site" → "Earn tokens" → "Return to app" cycle completed
- **Increased in-app monetization conversion**
  - Attempt unlock/gacha with tokens earned from the corporate site → If more tokens are needed, induce cash purchase
- **Continuous personalization**
  - Maximize inflow rate with RFM + psychological profile-based recommendation engine

### Final Goal
Increase user dwell time and revenue on both platforms through synergy between the app and the corporate site.