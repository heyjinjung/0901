# 🌈 User Journey: From Entry to Engagement

## 6.1. Entry Point (유입 경로) 🚪

### 초대코드 기반 즉시 가입 시스템
- **초대코드 + 닉네임만으로 즉시 가입**
- 가입 즉시 모든 서비스 이용 가능
- 복잡한 인증 절차 완전 제거

### 로그인 방식
- **초대코드 기반 가입**: 6자리 코드 + 닉네임 
- **로컬스토리지 기반 인증**: JWT/세션 관리 제거
- **랭크 기반 권한**: VIP/PREMIUM/STANDARD 3단계

### 유입 경로 🔍

#### 1. 소셜 미디어 광고
- 타겟: MZ세대 고액 사용자
- 엄격한 초대 코드 기반 접근

#### 2. 친구 초대 링크
- 기존 코드회원이 발급한 초대 코드
- 제한적이고 통제된 확산

### 진입 흐름도
```
[Landing Page] → [초대 코드 입력] → [닉네임/비밀번호 등록] → [앱 진입 (메인 대시보드)]
```

## 6.2. Journey Phases 🚀

### 1. Anticipation (기대) 🌟

#### 진입 흐름
- **사용자:** 초대 링크 클릭
- **앱:** 초대코드 입력 화면 노출
  - "VIP 멤버십을 위한 초대코드를 입력하세요"
- **사용자:** 유효한 초대코드 + 닉네임 입력
- **시스템:** 즉시 가입 완료 → 모든 서비스 접근 가능

#### 데모용 초대코드 안내
- **VIP2024**: VIP 등급 (모든 서비스 접근)
- **DEMO99**: PREMIUM 등급 (프리미엄 콘텐츠)
- **TEST01**: STANDARD 등급 (기본 서비스)

#### CJ AI 웰컴 메시지
- "어서 오세요, {닉네임}님! 오늘의 사이버 토큰은 {초기 토큰}개 입니다."

#### 주요 감정 기대치
- 소속감 (초대 코드 → VIP 전용)
- 기대감 ("토큰으로 어떤 재미를 경험할까?")

### 2. Challenge (도전) 🎲

#### 미니게임 단계
- Slot Machine (3릴, Spin 버튼)
- Roulette (스핀 애니메이션)
- RPS (Rock-Paper-Scissors)

#### 감정 피드백 (도파민 루프)
- CJ AI 실시간 반응
  - GAME_WIN: "축하합니다, {nickname}님! {earned_tokens} 토큰이 적립되었어요! 🎉"
  - GAME_FAIL: "괜찮아요! 다음은 꼭 성공할 거예요. 스트릭이 {streak+1}이 되면 확률이 커집니다!"

#### 사이버 토큰 사용
- 1회 플레이당 소모 토큰 자동 차감
  - 슬롯: 10토큰
  - 룰렛: 20토큰
- 실패 시 일부 토큰 환급 이벤트

### 3. Achievement (성취) 🏆

#### 단계별 콘텐츠 언락
- **Stage 1 (200토큰):** 블러리 티저
  - CJ AI: "Stage 1 언락 성공! 다음은 Stage 2를 노려보세요."

- **Stage 2 (500토큰):** 부분 노출
  - CJ AI: "와우, {nickname}님! 깜짝 놀랄 준비 되셨나요? 🔥"

- **Stage 3 (1,000토큰):** 전체 공개
  - CJ AI: "축하합니다! 최종 언락 완료! VIP 한정 콘텐츠를 즐기세요. 🎬"

#### 소셜/경쟁 트리거
- 리더보드: "현재 {nickname}님의 순위: TOP {rank} (Whale 그룹)"
- CJ AI: "상위 1% 달성자에게는 별도 보너스 +150토큰 지급!"

### 4. Retention & Loop (리텐션 & 반복) 🔁

#### 일일 체크인
- CJ AI: "오늘의 사이버 토큰 50개가 준비되어 있습니다! 지금 바로 스핀하세요!"
- 앱 푸시: "당신의 매일 보너스가 만료됩니다! 12시까지 접속하고 수령하세요."

#### 한정 이벤트
- 본사 사이트 연동 이벤트
  - "본사 사이트 로그인만 해도 추가 200토큰!"
- CJ AI: "지금 본사 사이트에 방문하여 토큰을 충전해보세요. 한정 2시간 이벤트! ⏰"

#### 주간 도전 과제
- "이번 주 미션: 룰렛 5회 플레이 → Stage 2 할인 언락 쿠폰"
- CJ AI: "이 미션을 완료하면 다음 언락 비용이 400토큰으로 감소합니다. 도전해보세요!"

### 5. Re-Engagement (재유입) 🔄

#### 장기 미접속 대응
- 7일 이상 미접속 시
  - CJ AI: "{nickname}님, 그동안 소식이 없으셨네요. 다시 돌아오시면 300토큰 드립니다!"
  - 푸시 알림: "We miss you! Come back now for 300 Cyber Tokens!"

#### 본사 사이트 리마인더
- "앱에서 확인되지 않은 토큰 150개가 본사에 남아있습니다. 지금 확인하세요!"
- CJ AI: "본사 사이트에서 '남은 토큰' 다시 확인하고 앱으로 돌아오세요!"

<!-- English translation below -->

# User Journey: From Entry to Engagement (English Translation)

## 6.1. Entry Point 🚪

### Access Restrictions
- **For pre-authenticated code members only**
- Access granted only to selected users via invitation codes

### Login Method
- Nickname + Password 
- Complete abolition of social login

### Entry Channels 🔍

#### 1. Social Media Ads
- Target: High-income MZ generation
- Strict invitation code-based access

#### 2. Friend Invitation Links
- Invitation codes issued by existing code members
- Limited and controlled dissemination

### Entry Flowchart
```
[Landing Page] → [Enter Invitation Code] → [Register Nickname/Password] → [Enter App (Main Dashboard)]
```

## 6.2. Journey Phases 🚀

### 1. Anticipation 🌟

#### Entry Flow
- **User:** Clicks on the invitation link
- **App:** Displays code entry screen
  - "Invitation code is required"
- **User:** Enters valid code and registers nickname/password

#### CJ AI Welcome Message
- "Welcome, {nickname}! You have {initial_tokens} cyber tokens today."

#### Key Emotional Expectations
- Sense of belonging (Invitation code → VIP exclusive)
- Anticipation ("What fun will the tokens bring?")

### 2. Challenge 🎲

#### Mini-game Stages
- Slot Machine (3 reels, Spin button)
- Roulette (spin animation)
- RPS (Rock-Paper-Scissors)

#### Emotional Feedback (Dopamine Loop)
- CJ AI real-time reactions
  - GAME_WIN: "Congratulations, {nickname}! You've earned {earned_tokens} tokens! 🎉"
  - GAME_FAIL: "Don't worry! You'll succeed next time. The streak will increase the odds!"

#### Cyber Token Usage
- Automatic token deduction per play
  - Slots: 10 tokens
  - Roulette: 20 tokens
- Partial token refund event on failure

### 3. Achievement 🏆

#### Content Unlock by Stage
- **Stage 1 (200 tokens):** Blurry teaser
  - CJ AI: "Stage 1 unlocked! Aim for Stage 2."

- **Stage 2 (500 tokens):** Partial exposure
  - CJ AI: "Wow, {nickname}! Are you ready to be surprised? 🔥"

- **Stage 3 (1,000 tokens):** Full disclosure
  - CJ AI: "Congratulations! Final unlock complete! Enjoy VIP exclusive content. 🎬"

#### Social/Competitive Triggers
- Leaderboard: "Current rank of {nickname}: TOP {rank} (Whale group)"
- CJ AI: "Bonus of +150 tokens for top 1% achievers!"

### 4. Retention & Loop 🔁

#### Daily Check-in
- CJ AI: "You have 50 cyber tokens waiting for you today! Spin now!"
- App push: "Your daily bonus will expire! Log in by 12 o'clock to receive it."

#### Limited Events
- Headquarters site linked events
  - "Additional 200 tokens just for logging into the headquarters site!"
- CJ AI: "Visit the headquarters site now to recharge tokens. Limited 2-hour event! ⏰"

#### Weekly Challenge Missions
- "This week's mission: Play roulette 5 times → Discount unlock coupon for Stage 2"
- CJ AI: "Completing this mission will reduce the next unlock cost to 400 tokens. Give it a try!"

### 5. Re-Engagement 🔄

#### Long-term Inactivity Response
- After 7 days of inactivity
  - CJ AI: "{nickname}, we've missed you. Come back and receive 300 tokens!"
  - Push notification: "We miss you! Come back now for 300 Cyber Tokens!"

#### Headquarters Site Reminder
- "150 tokens remain unverified in the app at the headquarters. Check now!"
- CJ AI: "Check 'remaining tokens' again on the headquarters site and return to the app!"

