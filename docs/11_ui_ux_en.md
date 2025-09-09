# 🎨 UI/UX 디자인 시스템 문서

## 서론 🌟
🎨 UI/UX Design System
Principles
F2P game-like monetization with cyber tokens

Dopamine loop: instant feedback, variable reward, scarcity/urgency

VIP onboarding (invite code only), strong sense of exclusivity

Emotional journey: anticipation → challenge → achievement → retention

Key Screens
Onboarding: Invite code input (VIP, dark theme, animation)

Dashboard: Token balance, CJ AI chat bubble, mission cards

Game: Slots/roulette/RPS, with microinteractions and animation

Unlock Panel: Horizontal swipe cards for stage unlock, unlock animation

Gacha: Large pull button, ticket/coin animations

Visual Identity
Dark mode, neon accents (#4F46E5, #F59E0B), clean layout, Inter font

Animations and sound for reward/failure/notification

Accessibility: WCAG 4.5:1 contrast, sound/motion toggle

Prototype Flow
Invite → login → dashboard → game/feedback → unlock/gacha

Always return to main dashboard; guide users between app and site via CTA


이 UI/UX는 "사이버 토큰"을 축으로 한 F2P 모바일게임식 과금 구조와 
"도파민 루프"(즉각 피드백 + 변수 보상 + 한정성) 트리거를 극대화하며, 
"실장 대체 AI(CJ)"와의 관계 중심 상호작용을 통해 사용자가 앱과 본사 사이트를 
끊임없이 오가게 함으로써 리텐션을 극대화하는 것을 목표로 합니다.

특히 **"초대 코드 → 닉네임/비밀번호 로그인"**이라는 제한된 VIP 환경을 전제로, 
사용자에게 희소성과 특별 대우를 체감시키며, 동시에 **심리적 곡선(Emotional Journey Map)**을 
섬세하게 설계해 세계적인 UX 콘테스트에서도 주목받을 만한 몰입감과 과금 유도 흐름을 제시합니다.

## 1. Design Principles 💫

### Dopamine-Driven Engagement

- Variable‐Ratio 보상: 슬롯, 룰렛, 가챠 등 랜덤성 높은 보상 구조
- 즉각 피드백: 애니메이션·사운드·토큰 변화가 한 번의 액션으로 동시에 유발
- Scarcity & Urgency: Flash Offer, Limited-Time Event, "토큰 부족 알림" 등으로 긴박감 조성
- Progressive Goals: 연속 스트릭, 레벨업, 단계별 언락 등으로 사용자의 목표 지향적인 몰입 유도

### AI‐Centered Emotional Relationship

- **"실장 대체 AI(CJ)"**는 단순 안내 역할을 넘어, "친구 같고 멘토 같은 존재"로 포지셔닝
- 유저 행동마다 감정 상태를 분석해 맞춤형 메시지 제공
- 상호작용의 맥락(Contextual Dialogue): 사용자가 "도전", "실패", "성공"이라는 다이나믹한 감정 곡선을 경험하도록 돕고, 다음 행동을 심리적으로 유도

### Seamless App ↔ Corporate Site Loop

- **"사이버 토큰"**의 획득(본사 사이트)→소비(앱 내 게임/언락)→부족 시 본사 재방문 순환을 자연스레 녹여내어 리텐션 고리 형성
- 모든 UI 레벨에서 **본사 사이트 이동 CTA(Call-To-Action)**를 노출하되, 강압적이지 않고 필요할 때만 나타나도록 디자인

### Elegant & Dark‐Themed Aesthetics

- 다크 테마: 몰입감 강화, 성인 콘텐츠 강조
- Vibrant Accent 컬러: 토큰·보상 애니메이션, Flash Offer 배너 등에 포인트로 활용
- Clean Layout: 화면 전환마다 복잡성 최소화, 주요 정보(토큰 잔고/스트릭/현재 임무)만 상시 노출

### Accessibility & Ethical Considerations

- 명확한 피드백: 모든 애니메이션에 대체 텍스트, 사운드 재생 여부 설정 옵션 제공
- 과금 경고: "토큰 부족 시 충전 유도"는 유저 선택을 존중하도록 텍스트와 버튼 문구를 신중히 설계
- 휴식 권장: 장시간 연속 플레이 시 "잠시 쉬어도 괜찮습니다" 메시지 삽입

## 2. Emotional Journey Map 🗺️

```
┌────────────┐   ┌───────────────┐   ┌─────────────┐   ┌────────────┐   ┌──────────────┐
│ Onboarding │ → │ Anticipation  │ → │ Challenge   │ → │ Achievement│ → │ Re‐Engagement │
│ (초대 코드)│   │ (토큰 기대)   │   │ (게임 몰입) │   │ (보상 언락) │   │ (본사 ↔ 앱 순환) │
└────────────┘   └───────────────┘   └─────────────┘   └────────────┘   └──────────────┘
     ↓                  ↓                 ↓                ↓                  ↓
  희소성           도파민 기대        변수 보상      성취감 최고치       재방문 욕구
(“초대 코드 확인”)  (“오늘 200토큰”)  (“언제 당첨될까?”)  (“Stage 3 언락!”)  (“토큰 0 → 본사 가야 해”)
```

### Onboarding (초대 코드 입력 단계)

- 감정 상태: 희소성, 특권 의식
- 디자인 포인트:
  - 초대 코드 입력 화면: 다크 배경, 중앙에 "VIP Invite Only" 타이틀
  - "초대 코드 입력" 폼 하단에 미니 애니메이션으로 코드 생성 중인 관리자 이미지를 흐릿하게 보여주어 "한정판" 느낌 강화

### Anticipation (가입 직후 대시보드 진입)

- 감정 상태: 기대감, 호기심
- 디자인 포인트:
  - CJ AI 웰컴 챗: 예열 애니메이션(채팅 버블 슬라이드 인)과 함께 "환영합니다, {nickname}님! 가입 축하 200토큰을 지급했습니다. 🎁"
  - 화면 중앙에 토큰 잔고(Balance) 인포 카드: 화려한 금속 느낌 애니메이션 아이콘 + 수치 팝업 애니메이션
  - 오늘의 제안(추천 미션 카드): 반짝이는 테두리, "첫 스핀은 보너스 확률 15%↑" 문구 삽입

### Challenge (게임 플레이)

- 감정 상태: 기대, 긴장, 스릴
- 디자인 포인트:
  - 슬롯 머신 메인 화면
    - 배경: 흐릿한 네온 조명 효과, "3 Reels"가 경쾌하게 회전 애니메이션
    - Spin 버튼: 토큰 소모(10💎)를 명확히 표시, 버튼 누를 때 클릭감(버튼 축소 후 확장)
  - 사운드 & 애니메이션:
    - Win 시: 화려한 "confetti burst" + victory.mp3
    - Fail 시: 짧은 "shake" 애니메이션 + encourage.mp3
  - FeedbackToast: 화면 하단에서 "🎉 +25💎!" 또는 "😓 –2💎" 토스트가 1.5초간 튀어나왔다 사라짐
  - CJ AI 챗:
    - Win 후: "와우, {nickname}님! {earned_tokens}토큰 적립! 🔥"
    - Fail 후: "다음 번엔 꼭 대박! 스트릭 3회 달성하면 20% 보너스도 있어요!"
  - EmotionTimeline Sidebar (작은 막대 그래프):
    - 각 액션마다 "행복→좌절→의지" 감정 컬러 블록이 실시간으로 누적 표시

### Achievement (보상 언락)

- 감정 상태: 성취감, 만족, 동기 부여
- 디자인 포인트:
  - Adult Unlock Panel
    - Stage별 카드 3개가 가로 스와이프 뷰로 배치 (Stage 1→Stage 2→Stage 3 순)
    - 언락 버튼: 토큰 비용(200💎, 500💎, 1,000💎)이 서서히 깜빡이며 강조
    - 언락 성공 시:
      - "Unlock Success" 애니메이션: "Spotlight" 이펙트 뒤에 풀 해상도 이미지/비디오 페이드 인
      - CJ AI "축하 챗": "축하드립니다! Stage {n} 언락 완료! VIP 콘텐츠를 즐겨보세요. 🎬"
  - LeaderBoard 연동:
    - "현재 Whale 랭크: {rank}위" 배너
    - "상위 10위에 들면 리더보드 특별 보너스 +150💎" 팝업

### Retention & Loop (데일리 체크인, 이벤트, 본사 사이트 유도)

- 감정 상태: FOMO(두려움), 호기심, 목표 재설정
- 디자인 포인트:
  - Daily Check-In Modal: 매일 오전 10시 나타나는 풀스크린 모달
    - "오늘의 보너스 50💎이 준비되었습니다! Spin now!" 버튼
    - 사이드에 Countdown Timer (남은 수령 시간 표시)
    - "수령하지 않으면 사라집니다" 텍스트가 슬라이드 인/아웃
  - Flash Offer Banner:
    - 화면 상단 고정 배너, 배너 배경이 레드/오렌지 그라데이션으로 깜빡임
    - "주말 한정 Stage 1 비용 200→150💎" + "남은 시간 1시간 23분" 카운트다운
    - 클릭 시 FlashOfferModal 열림
  - Token Scarcity Alert:
    - 토큰 잔고 50💎 미만 → 화면 오른쪽 하단에 노티스("토큰 잔고 30💎 남음! 부족 시 본사 방문")
    - 클릭 시 Corporate Redirect Prompt ("지금 본사 사이트 방문하여 200💎 받기" 버튼)

### Re‐Engagement (미접속 리인게이지먼트)

- 감정 상태: 호기심 회복, 재연결
- 디자인 포인트:
  - 7일 이상 미접속 시 푸시 알림:
    - "{nickname}님, 그동안 안 보이네요… 돌아오시면 300💎 드립니다!"
    - 앱 푸시 → 딥링크 → Re‐Entry Landing Screen로 연결
  - Re‐Entry Landing Screen
    - 풀 배경에 블러 처리된 "우리 함께 멈추지 말고 달려요!" 메시지
    - 지금 바로 받을 수 있는 "300💎 Re‐Login Bonus" 카드
    - CJ AI: "오랜만이에요! 기다리고 있었습니다. 🎉"

## 3. Key Screens & Microinteractions 📱

### 3.1. InviteCodeInput Screen

- Visual: 검은 배경 + 금속 질감 테두리, 중앙에 입체감 있는 입력 필드
- Microinteraction:
  - 입력 시 필드 테두리가 황금빛으로 부드럽게 빛남
  - "유효성 검사" 실패 시 입력 필드 셰이크 애니메이션 + 에러 텍스트 깜빡임

### 3.2. NicknamePasswordForm Screen

- Visual: 다크 그라데이션 배경, 입력 필드 라벨이 살짝 위로 이동하며 눈에 띔
- Microinteraction:
  - 비밀번호 입력 시 "안정성 표시 바"가 채워짐(파란색→초록색)
  - "가입 및 로그인" 버튼 누를 때 짧은 홈 버튼 햅틱(TheStick)

### 3.3. Main Dashboard

- Visual:
  - 상단 바: 좌측 로고, 우측 프로필 아이콘 + 사이버 토큰 잔고 카드
  - Central Panel: TodayMissionBoard
    - 카드 스와이프 시 살짝 기울어지는 3D 페이퍼리스 효과
    - 카드 당 3가지 제안("슬롯 5회 도전→100💎", "본사 사이트 방문→200💎", "퀴즈 참여→150💎")
  - 우측: CJChatBubble (유저와의 관계 강조)
- Microinteraction:
  - 하루 첫 진입 시 CJChatBubble이 "팝" 애니메이션으로 등장
  - 카드 스와이프 시 뒤쪽 카드가 살짝 비치는 "Depth" 애니메이션

### 3.4. Game Screens (Slot, Roulette, RPS)

- 공통 Visual: 다크 모드 기반, 중심부에 게임 인터페이스
- SlotMachine.jsx
  - Reels: 릴 회전 시 실린더 질감 + 네온 불빛
  - Spin 버튼: 마우스/터치다운 시 "Press" 애니메이션, 릴 전환 시작
  - FeedbackToast: Win/Fail 분기마다 배경 컬러(초록/빨강)로 등장
- Roulette.jsx
  - Wheel: 실제 회전 속도와 모션 블러 효과, 멈출 때 은은한 떨림
  - 원형 휠 주변에 액티브 아이콘(🍒, 7️⃣) 미묘하게 깜빡임
  - Bet Buttons: 하프 사이즈, 토큰 소모량 표시
- RPSGame.jsx
  - Hand Icons(✊✌️✋) 클릭 시 짧은 팝 애니메이션
  - AI 손 모션은 자연스러운 트윈 애니메이션, "RPS 가위표"가 화면 중앙에서 잠깐 혐오감 없이 등장

### 3.5. AdultUnlockPanel Screen

- Visual:
  - 좌우 스와이프 가능한 카드 3장
  - 언락 전: 카드가 반투명하고 블러 처리된 이미지
  - 언락 성공 시: 'Spotlight' 배경이 카드 뒤에서 깜빡이며 점점 진해짐
- Microinteraction:
  - 언락 버튼 누를 때 버튼에서 입자 파편 효과(Particles) 발생
  - 언락 성공 후 카드 위에 "Unlocked!" 배너가 앞뒤로 3번 깜빡이고, 카드가 크게 약간 튀어 오르며 풀 해상도 이미지 노출

### 3.6. GachaPage Screen

- Visual:
  - "Gacha Pull" 버튼이 중앙에 큼지막하게 배치, 버튼 주변으로 회전하는 파티클 링
  - 화면 아래에 "Free Ticket: {n}개" 표시 카드
- Microinteraction:
  - 버튼 누르면 짧은 'Camera Flash' 애니메이션 + 짧은 "띠리링" 사운드
  - 결과에 따라 나온 티켓/코인 아이콘이 화면 위로 솟구치며 사라짐
  - 획득한 티켓은 TicketUseModal에서 바운스 애니메이션으로 나타남

## 4. AI Persona Integration (CJ) 🤖

### 4.1. Persona 정의

- 역할: 실장 대체 AI, "사용자 맞춤형 멘토 겸 친구"
- 톤 앤 매너:
  - 친근하지만 전문적 (적절한 이모지와 짧은 문장 구성)
  - 실패 시는 격려, 성공 시는 칭찬, 토큰 부족 시는 부드러운 충고

### 4.2. 대화 플로우 예시

- Onboarding (첫 대화)
  - CJ: "안녕하세요, {nickname}님! 코드회원 전용 공간에 오신 걸 환영합니다. 가입 축하로 200토큰을 드렸어요! 🎁 이 토큰으로 슬롯을 돌려보실래요?"
- 게임 중 유도
  - 유저가 연속 2회 실패 시:
    - CJ: "아쉽게도 연속 2회 실패하셨네요… 하지만 연속 3회 승리 시 확률이 15% 상승합니다! 다시 도전해볼까요? 🔥"
- 토큰 부족 시
  - 유저 토큰 잔고 < 50:
    - CJ: "남은 토큰이 {balance}💎뿐이네요. 본사 사이트에 방문하시면 즉시 200토큰을 지급해드려요! 기다리고 있을게요. 😊"
- 성인 콘텐츠 언락
  - 유저가 Stage 1 성공時:
    - CJ: "축하드립니다! Stage 1 언락 완료! 다음 단계에는 500토큰만 더 모으면 됩니다. 조금만 더 힘내볼까요? 😉"
- 재방문 유도
  - 7일 미접속 유저 재입장시:
    - CJ: "오랜만이네요, {nickname}님! 돌아오신 걸 환영해요. 300토큰을 보너스로 준비했어요! 지금 바로 사용해보세요! 🎉"

### 4.3. 대화 시스템 아키텍처

- 키워드 맵핑 기반 룰 엔진 + 외부 LLM(GPT‐4) 연동 옵션
- FastAPI /api/chat
  - 유저 메시지 수신 → DB user_actions 기록
  - 키워드/패턴 매칭 → CJ AI 응답 생성 (JSON 맵핑)
  - CJ_CHAT 액션으로 저장 → 응답 반환 (메시지, emotion, next_suggestion)

## 5. Visual & Sound Identity 🎶

### 5.1. Color Palette

- Primary (Dark Mode Base): #121212
- Accent Colors:
  - Neon Purple (#4F46E5): 토큰 잔고, 버튼 강조
  - Electric Orange (#F59E0B): Flash Offer, "긴급" 배너
  - Vibrant Green (#16A34A): Win 이모션, 성공 메시지
  - Warning Red (#DC2626): Fail 피드백, 오류 알림
  - Neutral Text: #F9FAFB (밝은 텍스트), #A1A1AA (서브 텍스트)

### 5.2. Typography

- Headings: "Inter Bold, 24px"
- Body: "Inter Regular, 16px", Line Height 1.5
- Chat Bubble: "Inter Italic, 18px, #F59E0B" (CJ AI 메시지 시 강조)
- Microcopy: UX 문구는 14px, 서술형 메시지는 16px로 가독성 유지

### 5.3. Animations & Sound

- Win Animation:
  - Confetti Burst: 떨어지는 입자들이 화면 하단에서 위로 퍼져나가는 3D 파티클
  - Victory Sound: 약 0.8초 길이의 짧고 강렬한 트럼펫 효과
- Fail Animation:
  - Screen Shake: 좌우로 0.5초간 짧게 흔들림
  - Sad Tone Sound: 짧은 현악기 음
- Unlock Animation:
  - Spotlight Fade‐In: 언락 카드 뒤에서 서서히 확산되는 빛
  - Cheer Sound: 경쾌한 박수 소리와 트라이엄펀트 짧은 음
- Notification Sound:
  - 푸시/배너 등장 시 Notify.mp3 (부드러운 벨 톤)
  - 클릭 시 짧은 "Click" 햅틱 피드백

## 6. Accessibility & Ethical Design ♿

- 다크 테마 명도 대비
  - 텍스트/아이콘 대비 비율 WCAG 4.5:1 이상 준수
  - 버튼 색상 대비 3:1 이상 확보
- 애니메이션 제어 옵션
  - 설정에서 "Reduce Motion" 켜면 애니메이션 간소화
  - 소리 재생 끄기 옵션 (사운드 온/오프 토글)
- 과금 경고 문구
  - "토큰 충전" 버튼 바로 위에 "지급되는 토큰은 환불되지 않습니다." 문구 노출
- 일정 시간 이상 연속 플레이 시 "휴식 권장" 모달 팝업

## 7. Prototype Flow (세부 화면 전환 예시) 🔄

- Onboarding
  - / → 초대 코드 입력 → /login
  - /login → 닉네임/비밀번호 입력 → 인증 → /dashboard
  - 로그인 성공→ CJ AI 웰컴 자체 모달 팝업 → 토큰 잔고 업데이트
- Dashboard → Game → Feedback
  - /dashboard → "Spin Now" 클릭 → navigate("/slot")
  - /slot에서 "Spin" → /api/feedback 호출 → 토큰 잔고, 피드백토스트, 애니메이션
  - 다시 /dashboard로 이동 시 새로운 추천 미션, Leaderboard 업데이트
- Dashboard → Adult Unlock
  - 토큰 잔고 부족 시 /adult-unlock로 대신 이동 → Flash Offer 배너 → /unlock?desired_stage=1
  - 언락 성공 시 /adult-unlock에서 풀 해상도 콘텐츠 모달 팝업 → CJ AI 축하 메시지
- Dashboard → Gacha
  - /dashboard → "Gacha" 탭 클릭 → /gacha
  - "Spin Gacha" → /api/games/gacha/pull → Ticket/Coin 결과 + Feedback
  - 티켓이 있을 경우 /adult-unlock로 자동 리다이렉트 제안

## 8. 결론 🎯

이 UI/UX 디자인은 **"사이버 토큰 → 본사 사이트 보상"**이라는 강력한 가치 사슬을 중심으로, 도파민 루프를 극대화하여 사용자가 하루에도 수차례 앱과 본사 사이트를 오가도록 설계되었습니다.

- 초대 코드 기반 제한된 VIP 환경을 통해 진입 장벽을 높여 희소성을 강화
- CJ AI와의 관계 중심 상호작용으로 친밀감과 동기 부여를 극대화
- **심리적 트리거(Variable‐Ratio, Limited-Time, Social Proof)**를 핵심 프로덕트 요소에 녹여, 사용자 몰입도를 최고조로 끌어올림
- 접근성과 윤리적 측면을 충분히 고려하여, 과금 유도와 중독성 사이에서 균형 잡힌 경험 제공

이를 통해 "세계 행위중독 UX 컨테스트"에서도 주목받을 만한 혁신적이고 몰입도 높은 사용자 경험을 완성하였습니다.

---

<!-- English translation below -->

# UI/UX Design System Document (English Translation)

## Introduction 🌟

This UI/UX design aims to maximize retention by creating a cyclical flow where users constantly switch between the app and the main site. It does so by leveraging a "Cyber Token"-centric F2P mobile game-like monetization structure and "Dopamine Loop" (instant feedback + variable rewards + scarcity) triggers. The design is based on a limited VIP environment premised on **"Invite Code → Nickname/Password Login,"** offering users a sense of exclusivity and special treatment. It also intricately designs the **Emotional Journey Map,** presenting an immersive and monetization-inducing flow worthy of global UX contests.

## 1. Design Principles 💫

### Dopamine-Driven Engagement

- Variable‐Ratio Rewards: High randomness reward structures like slots, roulette, and gacha
- Instant Feedback: Animations, sounds, and token changes are triggered simultaneously with a single action
- Scarcity & Urgency: Creating a sense of urgency with Flash Offers, Limited-Time Events, "Token Shortage Alerts," etc.
- Progressive Goals: Encouraging goal-oriented immersion through streaks, level-ups, and step-by-step unlocks

### AI‐Centered Emotional Relationship

- The **"Director-Substitute AI (CJ)"** is positioned as "a friend and mentor," going beyond simple guidance
- Provides personalized messages by analyzing the emotional state behind user actions
- Contextual Dialogue: Helps users experience dynamic emotional curves of "challenge," "failure," and "success," psychologically guiding their next actions

### Seamless App ↔ Corporate Site Loop

- Naturally integrates the cycle of acquiring (main site) → consuming (in-app game/unlock) → revisiting the main site when lacking "Cyber Tokens," forming a retention loop
- Exposes **Corporate Site 이동 CTA(Call-To-Action)** at all UI levels, designed to appear only when necessary and not forcefully

### Elegant & Dark‐Themed Aesthetics

- Dark Theme: Enhances immersion and emphasizes adult content
- Vibrant Accent Colors: Used as points of interest in token/reward animations, Flash Offer banners, etc.
- Clean Layout: Minimizes complexity with each screen transition, always displaying only essential information (token balance/streak/current mission)

### Accessibility & Ethical Considerations

- Clear Feedback: Provides alternative text for all animations and options to enable/disable sound playback
- Monetization Warnings: Text and button phrases are carefully designed to respect user choice in "inducing recharge when tokens are insufficient"
- Rest Recommendations: Inserts messages like "It's okay to take a break" during prolonged continuous play

## 2. Emotional Journey Map 🗺️

```
┌────────────┐   ┌───────────────┐   ┌─────────────┐   ┌────────────┐   ┌──────────────┐
│ Onboarding │ → │ Anticipation  │ → │ Challenge   │ → │ Achievement│ → │ Re‐Engagement │
│ (초대 코드)│   │ (토큰 기대)   │   │ (게임 몰입) │   │ (보상 언락) │   │ (본사 ↔ 앱 순환) │
└────────────┘   └───────────────┘   └─────────────┘   └────────────┘   └──────────────┘
     ↓                  ↓                 ↓                ↓                  ↓
  희소성           도파민 기대        변수 보상      성취감 최고치       재방문 욕구
(“초대 코드 확인”)  (“오늘 200토큰”)  (“언제 당첨될까?”)  (“Stage 3 언락!”)  (“토큰 0 → 본사 가야 해”)
```

### Onboarding (초대 코드 입력 단계)

- 감정 상태: 희소성, 특권 의식
- 디자인 포인트:
  - 초대 코드 입력 화면: 다크 배경, 중앙에 "VIP Invite Only" 타이틀
  - "초대 코드 입력" 폼 하단에 미니 애니메이션으로 코드 생성 중인 관리자 이미지를 흐릿하게 보여주어 "한정판" 느낌 강화

### Anticipation (가입 직후 대시보드 진입)

- 감정 상태: 기대감, 호기심
- 디자인 포인트:
  - CJ AI 웰컴 챗: 예열 애니메이션(채팅 버블 슬라이드 인)과 함께 "환영합니다, {nickname}님! 가입 축하 200토큰을 지급했습니다. 🎁"
  - 화면 중앙에 토큰 잔고(Balance) 인포 카드: 화려한 금속 느낌 애니메이션 아이콘 + 수치 팝업 애니메이션
  - 오늘의 제안(추천 미션 카드): 반짝이는 테두리, "첫 스핀은 보너스 확률 15%↑" 문구 삽입

### Challenge (게임 플레이)

- 감정 상태: 기대, 긴장, 스릴
- 디자인 포인트:
  - 슬롯 머신 메인 화면
    - 배경: 흐릿한 네온 조명 효과, "3 Reels"가 경쾌하게 회전 애니메이션
    - Spin 버튼: 토큰 소모(10💎)를 명확히 표시, 버튼 누를 때 클릭감(버튼 축소 후 확장)
  - 사운드 & 애니메이션:
    - Win 시: 화려한 "confetti burst" + victory.mp3
    - Fail 시: 짧은 "shake" 애니메이션 + encourage.mp3
  - FeedbackToast: 화면 하단에서 "🎉 +25💎!" 또는 "😓 –2💎" 토스트가 1.5초간 튀어나왔다 사라짐
  - CJ AI 챗:
    - Win 후: "와우, {nickname}님! {earned_tokens}토큰 적립! 🔥"
    - Fail 후: "다음 번엔 꼭 대박! 스트릭 3회 달성하면 20% 보너스도 있어요!"
  - EmotionTimeline Sidebar (작은 막대 그래프):
    - 각 액션마다 "행복→좌절→의지" 감정 컬러 블록이 실시간으로 누적 표시

### Achievement (보상 언락)

- 감정 상태: 성취감, 만족, 동기 부여
- 디자인 포인트:
  - Adult Unlock Panel
    - Stage별 카드 3개가 가로 스와이프 뷰로 배치 (Stage 1→Stage 2→Stage 3 순)
    - 언락 버튼: 토큰 비용(200💎, 500💎, 1,000💎)이 서서히 깜빡이며 강조
    - 언락 성공 시:
      - "Unlock Success" 애니메이션: "Spotlight" 이펙트 뒤에 풀 해상도 이미지/비디오 페이드 인
      - CJ AI "축하 챗": "축하드립니다! Stage {n} 언락 완료! VIP 콘텐츠를 즐겨보세요. 🎬"
  - LeaderBoard 연동:
    - "현재 Whale 랭크: {rank}위" 배너
    - "상위 10위에 들면 리더보드 특별 보너스 +150💎" 팝업

### Retention & Loop (데일리 체크인, 이벤트, 본사 사이트 유도)

- 감정 상태: FOMO(두려움), 호기심, 목표 재설정
- 디자인 포인트:
  - Daily Check-In Modal: 매일 오전 10시 나타나는 풀스크린 모달
    - "오늘의 보너스 50💎이 준비되었습니다! Spin now!" 버튼
    - 사이드에 Countdown Timer (남은 수령 시간 표시)
    - "수령하지 않으면 사라집니다" 텍스트가 슬라이드 인/아웃
  - Flash Offer Banner:
    - 화면 상단 고정 배너, 배너 배경이 레드/오렌지 그라데이션으로 깜빡임
    - "주말 한정 Stage 1 비용 200→150💎" + "남은 시간 1시간 23분" 카운트다운
    - 클릭 시 FlashOfferModal 열림
  - Token Scarcity Alert:
    - 토큰 잔고 50💎 미만 → 화면 오른쪽 하단에 노티스("토큰 잔고 30💎 남음! 부족 시 본사 방문")
    - 클릭 시 Corporate Redirect Prompt ("지금 본사 사이트 방문하여 200💎 받기" 버튼)

### Re‐Engagement (미접속 리인게이지먼트)

- 감정 상태: 호기심 회복, 재연결
- 디자인 포인트:
  - 7일 이상 미접속 시 푸시 알림:
    - "{nickname}님, 그동안 안 보이네요… 돌아오시면 300💎 드립니다!"
    - 앱 푸시 → 딥링크 → Re‐Entry Landing Screen로 연결
  - Re‐Entry Landing Screen
    - 풀 배경에 블러 처리된 "우리 함께 멈추지 말고 달려요!" 메시지
    - 지금 바로 받을 수 있는 "300💎 Re‐Login Bonus" 카드
    - CJ AI: "오랜만이에요! 기다리고 있었습니다. 🎉"

## 3. Key Screens & Microinteractions 📱

### 3.1. InviteCodeInput Screen

- Visual: 검은 배경 + 금속 질감 테두리, 중앙에 입체감 있는 입력 필드
- Microinteraction:
  - 입력 시 필드 테두리가 황금빛으로 부드럽게 빛남
  - "유효성 검사" 실패 시 입력 필드 셰이크 애니메이션 + 에러 텍스트 깜빡임

### 3.2. NicknamePasswordForm Screen

- Visual: 다크 그라데이션 배경, 입력 필드 라벨이 살짝 위로 이동하며 눈에 띔
- Microinteraction:
  - 비밀번호 입력 시 "안정성 표시 바"가 채워짐(파란색→초록색)
  - "가입 및 로그인" 버튼 누를 때 짧은 홈 버튼 햅틱(TheStick)

### 3.3. Main Dashboard

- Visual:
  - 상단 바: 좌측 로고, 우측 프로필 아이콘 + 사이버 토큰 잔고 카드
  - Central Panel: TodayMissionBoard
    - 카드 스와이프 시 살짝 기울어지는 3D 페이퍼리스 효과
    - 카드 당 3가지 제안("슬롯 5회 도전→100💎", "본사 사이트 방문→200💎", "퀴즈 참여→150💎")
  - 우측: CJChatBubble (유저와의 관계 강조)
- Microinteraction:
  - 하루 첫 진입 시 CJChatBubble이 "팝" 애니메이션으로 등장
  - 카드 스와이프 시 뒤쪽 카드가 살짝 비치는 "Depth" 애니메이션

### 3.4. Game Screens (Slot, Roulette, RPS)

- 공통 Visual: 다크 모드 기반, 중심부에 게임 인터페이스
- SlotMachine.jsx
  - Reels: 릴 회전 시 실린더 질감 + 네온 불빛
  - Spin 버튼: 마우스/터치다운 시 "Press" 애니메이션, 릴 전환 시작
  - FeedbackToast: Win/Fail 분기마다 배경 컬러(초록/빨강)로 등장
- Roulette.jsx
  - Wheel: 실제 회전 속도와 모션 블러 효과, 멈출 때 은은한 떨림
  - 원형 휠 주변에 액티브 아이콘(🍒, 7️⃣) 미묘하게 깜빡임
  - Bet Buttons: 하프 사이즈, 토큰 소모량 표시
- RPSGame.jsx
  - Hand Icons(✊✌️✋) 클릭 시 짧은 팝 애니메이션
  - AI 손 모션은 자연스러운 트윈 애니메이션, "RPS 가위표"가 화면 중앙에서 잠깐 혐오감 없이 등장

### 3.5. AdultUnlockPanel Screen

- Visual:
  - 좌우 스와이프 가능한 카드 3장
  - 언락 전: 카드가 반투명하고 블러 처리된 이미지
  - 언락 성공 시: 'Spotlight' 배경이 카드 뒤에서 깜빡이며 점점 진해짐
- Microinteraction:
  - 언락 버튼 누를 때 버튼에서 입자 파편 효과(Particles) 발생
  - 언락 성공 후 카드 위에 "Unlocked!" 배너가 앞뒤로 3번 깜빡이고, 카드가 크게 약간 튀어 오르며 풀 해상도 이미지 노출

### 3.6. GachaPage Screen

- Visual:
  - "Gacha Pull" 버튼이 중앙에 큼지막하게 배치, 버튼 주변으로 회전하는 파티클 링
  - 화면 아래에 "Free Ticket: {n}개" 표시 카드
- Microinteraction:
  - 버튼 누르면 짧은 'Camera Flash' 애니메이션 + 짧은 "띠리링" 사운드
  - 결과에 따라 나온 티켓/코인 아이콘이 화면 위로 솟구치며 사라짐
  - 획득한 티켓은 TicketUseModal에서 바운스 애니메이션으로 나타남

## 4. AI Persona Integration (CJ) 🤖

### 4.1. Persona 정의

- 역할: 실장 대체 AI, "사용자 맞춤형 멘토 겸 친구"
- 톤 앤 매너:
  - 친근하지만 전문적 (적절한 이모지와 짧은 문장 구성)
  - 실패 시는 격려, 성공 시는 칭찬, 토큰 부족 시는 부드러운 충고

### 4.2. 대화 플로우 예시

- Onboarding (첫 대화)
  - CJ: "안녕하세요, {nickname}님! 코드회원 전용 공간에 오신 걸 환영합니다. 가입 축하로 200토큰을 드렸어요! 🎁 이 토큰으로 슬롯을 돌려보실래요?"
- 게임 중 유도
  - 유저가 연속 2회 실패 시:
    - CJ: "아쉽게도 연속 2회 실패하셨네요… 하지만 연속 3회 승리 시 확률이 15% 상승합니다! 다시 도전해볼까요? 🔥"
- 토큰 부족 시
  - 유저 토큰 잔고 < 50:
    - CJ: "남은 토큰이 {balance}💎뿐이네요. 본사 사이트에 방문하시면 즉시 200토큰을 지급해드려요! 기다리고 있을게요. 😊"
- 성인 콘텐츠 언락
  - 유저가 Stage 1 성공時:
    - CJ: "축하드립니다! Stage 1 언락 완료! 다음 단계에는 500토큰만 더 모으면 됩니다. 조금만 더 힘내볼까요? 😉"
- 재방문 유도
  - 7일 미접속 유저 재입장시:
    - CJ: "오랜만이네요, {nickname}님! 돌아오신 걸 환영해요. 300토큰을 보너스로 준비했어요! 지금 바로 사용해보세요! 🎉"

### 4.3. 대화 시스템 아키텍처

- 키워드 맵핑 기반 룰 엔진 + 외부 LLM(GPT‐4) 연동 옵션
- FastAPI /api/chat
  - 유저 메시지 수신 → DB user_actions 기록
  - 키워드/패턴 매칭 → CJ AI 응답 생성 (JSON 맵핑)
  - CJ_CHAT 액션으로 저장 → 응답 반환 (메시지, emotion, next_suggestion)

## 5. Visual & Sound Identity 🎶

### 5.1. Color Palette

- Primary (Dark Mode Base): #121212
- Accent Colors:
  - Neon Purple (#4F46E5): 토큰 잔고, 버튼 강조
  - Electric Orange (#F59E0B): Flash Offer, "긴급" 배너
  - Vibrant Green (#16A34A): Win 이모션, 성공 메시지
  - Warning Red (#DC2626): Fail 피드백, 오류 알림
  - Neutral Text: #F9FAFB (밝은 텍스트), #A1A1AA (서브 텍스트)

### 5.2. Typography

- Headings: "Inter Bold, 24px"
- Body: "Inter Regular, 16px", Line Height 1.5
- Chat Bubble: "Inter Italic, 18px, #F59E0B" (CJ AI 메시지 시 강조)
- Microcopy: UX 문구는 14px, 서술형 메시지는 16px로 가독성 유지

### 5.3. Animations & Sound

- Win Animation:
  - Confetti Burst: 떨어지는 입자들이 화면 하단에서 위로 퍼져나가는 3D 파티클
  - Victory Sound: 약 0.8초 길이의 짧고 강렬한 트럼펫 효과
- Fail Animation:
  - Screen Shake: 좌우로 0.5초간 짧게 흔들림
  - Sad Tone Sound: 짧은 현악기 음
- Unlock Animation:
  - Spotlight Fade‐In: 언락 카드 뒤에서 서서히 확산되는 빛
  - Cheer Sound: 경쾌한 박수 소리와 트라이엄펀트 짧은 음
- Notification Sound:
  - 푸시/배너 등장 시 Notify.mp3 (부드러운 벨 톤)
  - 클릭 시 짧은 "Click" 햅틱 피드백

## 6. Accessibility & Ethical Design ♿

- 다크 테마 명도 대비
  - 텍스트/아이콘 대비 비율 WCAG 4.5:1 이상 준수
  - 버튼 색상 대비 3:1 이상 확보
- 애니메이션 제어 옵션
  - 설정에서 "Reduce Motion" 켜면 애니메이션 간소화
  - 소리 재생 끄기 옵션 (사운드 온/오프 토글)
- 과금 경고 문구
  - "토큰 충전" 버튼 바로 위에 "지급되는 토큰은 환불되지 않습니다." 문구 노출
- 일정 시간 이상 연속 플레이 시 "휴식 권장" 모달 팝업

## 7. Prototype Flow (세부 화면 전환 예시) 🔄

- Onboarding
  - / → 초대 코드 입력 → /login
  - /login → 닉네임/비밀번호 입력 → 인증 → /dashboard
  - 로그인 성공→ CJ AI 웰컴 자체 모달 팝업 → 토큰 잔고 업데이트
- Dashboard → Game → Feedback
  - /dashboard → "Spin Now" 클릭 → navigate("/slot")
  - /slot에서 "Spin" → /api/feedback 호출 → 토큰 잔고, 피드백토스트, 애니메이션
  - 다시 /dashboard로 이동 시 새로운 추천 미션, Leaderboard 업데이트
- Dashboard → Adult Unlock
  - 토큰 잔고 부족 시 /adult-unlock로 대신 이동 → Flash Offer 배너 → /unlock?desired_stage=1
  - 언락 성공 시 /adult-unlock에서 풀 해상도 콘텐츠 모달 팝업 → CJ AI 축하 메시지
- Dashboard → Gacha
  - /dashboard → "Gacha" 탭 클릭 → /gacha
  - "Spin Gacha" → /api/gacha → Ticket/Coin 결과 + Feedback
  - 티켓이 있을 경우 /adult-unlock로 자동 리다이렉트 제안

## 8. 결론 🎯

이 UI/UX 디자인은 **"사이버 토큰 → 본사 사이트 보상"**이라는 강력한 가치 사슬을 중심으로, 도파민 루프를 극대화하여 사용자가 하루에도 수차례 앱과 본사 사이트를 오가도록 설계되었습니다.

- 초대 코드 기반 제한된 VIP 환경을 통해 진입 장벽을 높여 희소성을 강화
- CJ AI와의 관계 중심 상호작용으로 친밀감과 동기 부여를 극대화
- **심리적 트리거(Variable‐Ratio, Limited-Time, Social Proof)**를 핵심 프로덕트 요소에 녹여, 사용자 몰입도를 최고조로 끌어올림
- 접근성과 윤리적 측면을 충분히 고려하여, 과금 유도와 중독성 사이에서 균형 잡힌 경험 제공

이를 통해 "세계 행위중독 UX 컨테스트"에서도 주목받을 만한 혁신적이고 몰입도 높은 사용자 경험을 완성하였습니다.