# 🔍 데이터 분석 및 개인화 시스템 문서

## 2.1. 데이터 수집 개요 📊

### 사용자 데이터 소스

#### 1. 미니게임 이벤트 🎲
- 슬롯, 가위바위보, 룰렛 등에서 발생한 플레이 기록
- 결과(승리/패배), 사용한 코인/사이버 토큰, 반복 횟수 등

#### 2. 성인 콘텐츠 언락 기록 🔓
- 단계별 언락 시점(stage, timestamp)
- 언락 트리거로 사용된 사이버 토큰 사용량

#### 3. 사용자 액션 로그 📝
- 모든 인터랙션: CLAIM_REWARD, VIEW_CONTENT, FAIL_GAME, BUY_ITEM 등
- 특히 "사이버 토큰 획득" 항목이 중요

#### 4. 심리 퀴즈 및 미니 설문 🧠
- 리스크 성향, 선호도, 보상 반응도 등을 측정하기 위한 짧은 설문

#### 5. 기업 업체 사용 내역 💻
- A 업체 방문 횟수, 체류 시간, 수행된 액션
- 보상으로 지급된 사이버 토큰 양

#### 6. 코호트 지표 📈
- DAU, MAU, Churn Rate, 코호트별 생존율 (D1/D7/D14/D30)

## 2.2. RFM + Cyber Token 기반 사용자 세분화
### 2.2.1. Recency-Frequency-Monetary (RFM) 계산
#### Recency (R):
- 마지막 액션(게임 플레이, 콘텐츠 언락, A 토큰 획득 등) 이후 경과 일수
- SQL 예시:
```sql
SELECT DATEDIFF(day, MAX(action_timestamp), CURRENT_DATE) 
FROM user_actions 
WHERE user_id = X;
```

#### Frequency (F):
- 지난 30일 내 전체 액션 수 (특히 “게임 플레이” + “사이버 토큰 사용” + “A 업체 방문”)
- SQL 예시:
```sql
SELECT COUNT(*) 
FROM user_actions 
WHERE user_id = X 
  AND action_timestamp >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY);
```

#### Monetary (M):
- 지난 30일 내 실제 과금 금액(현금 구매로 전환된 사이버 토큰 사용 총액)
- 또는 “A 업체를 통해 획득한 사이버 토큰” 총량
- SQL 예시:
```sql
-- 현금 결제 기반 토큰 사용량
SELECT SUM(metadata->>'spent_tokens')::INTEGER 
FROM user_actions 
WHERE user_id = X 
  AND action_type = 'SPEND_CYBER_TOKENS'
  AND action_timestamp >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY);

-- A 업체에서 획득한 토큰 누적량
SELECT SUM(metadata->>'earned_tokens')::INTEGER 
FROM user_actions 
WHERE user_id = X 
  AND action_type = 'EARN_CYBER_TOKENS'
  AND action_timestamp >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY);
```

### 2.2.2. 세그먼트 정의 (Cyber Token 중심)
#### Whale (Top Spenders)
- R ≤ 2일, F ≥ 30회 (주로 게임/미션 플레이),
- M ≥ 10,000 사이버 토큰(현금 결제 포함)
- “사이버 토큰 잔액” ≥ 1,000 이상

#### High Engaged (일반 과금 유저)
- R ≤ 5일, F ≥ 15회,
- M ≥ 2,000 사이버 토큰
- “A 업체 방문” ≥ 5회/월

#### Medium (적극 이용 유저)
- R 6∼15일, F 5∼14회,
- M 100∼1,999 사이버 토큰
- “A 업체 방문” 2∼4회/월

#### Low / At-risk (관심 필요)
- R > 15일 또는 F < 5회,
- M < 100 사이버 토큰
- “A 업체 방문” 0∼1회/월

> 참고: “A 업체 방문”과 “사이버 토큰 획득”은 동일하게 취급 가능
> 단, A 업체에서 획득한 토큰을 통한 “게임 내 소비”가 얼마나 이루어졌는지도 추적 필요

### 2.2.3. 구현 및 스케줄링
#### 배치 작업 (Nightly / 일 1회)
- user_actions → 지난 30일 데이터를 조회하여 RFM 계산
- “A 업체에서 획득한 토큰 수량”을 별도 집계
- user_segments 테이블 업데이트:
```sql
UPDATE user_segments
SET rfm_group = CASE
  WHEN r <= 2 AND f >= 30 AND m >= 10000 THEN 'Whale'
  WHEN r <= 5 AND f >= 15 AND m >= 2000 THEN 'High Engaged'
  WHEN r <= 15 AND f BETWEEN 5 AND 14 AND m BETWEEN 100 AND 1999 THEN 'Medium'
  ELSE 'Low'
END
WHERE user_id = X;
```

- 사이버 토큰 잔고 (Redis) 업데이트
```
user:{id}:cyber_token_balance =
이전 잔고 + 이번 배치에서 A 통해 획득한 토큰량 – 이번 배치에서 사용된 토큰량
```

#### 이벤트 트리거 (실시간)
- A 업체에서 토큰을 획득할 때마다 바로 user_actions에 EARN_CYBER_TOKENS 기록
- Redis 키(user:{id}:cyber_token_balance) 즉시 증액
- 즉시 푸시 알림:
```json
{
  "type": "NEW_TOKEN_ARRIVAL",
  "user_id": 123,
  "earned_tokens": 500,
  "message": "A 업체에서 500 사이버 토큰을 획득했습니다! 바로 게임에서 사용해보세요."
}
```

- 그 후 앞서 안내된 RFM 작업을 통해 세그먼트 변화 시 “등급 업그레이드 보상” 지급

## 2.3. Cyber-Token 기반 Personalized Recommendation Engine
### 2.3.1. 목표
- 개인화를 통해 유저가 보유 중인 “사이버 토큰”을 최대한 소비하도록 유도
- A 업체 → 앱 유입을 늘리기 위해,
- “A에서 토큰을 획득할 추가 미션”을 추천하거나 보유 토큰 사용 기회를 제공
- 도파민 경로를 강화: 즉시 보상 + 점진적 업그레이드 플랜 제공

### 2.3.2. 입력값
- user_segments 테이블 (rfm_group, risk_profile)
- Redis:
  - user:{id}:streak_count (연속 플레이 횟수)
  - user:{id}:cyber_token_balance (현재 사이버 토큰 잔고)
- A 업체 이용 기록:
  - 최신 A 방문 시점 & 이벤트 참여 기록
  - “이번 달 A 토큰 획득 횟수”

### 2.3.3. 출력값
- 추천 보상 제안 (Recommended Reward Proposal)
  - “지금 가지고 있는 토큰으로 슬롯에서 빅윈 확률 20%↑”
  - “룰렛 한 판 더 돌리면 Stage 2 Adult Content 언락”
  - “A 업체에서 300 토큰만 더 모으면 VIP 뱃지 획득”
- 추천 미션 제안
  - “오늘 A 업체에서 로그인만 하면 100 토큰 추가 지급”
  - “퀴즈 참여 시 200 토큰 보상 + 심층 프로필 업데이트”
- 추천 사용 창 시점
  - 유저의 플레이 패턴과 가장 최근 A 방문 시점을 분석하여
  → 유저가 “앱에 접속할 최적 시간대” 표시 (예: 20:00~21:00)

### 2.3.4. 알고리즘 Sketch (Pseudocode)
```python
def generate_recommendation(user_id):
    # 1. 사용자 세그먼트 조회
    segment = db.query("SELECT rfm_group, risk_profile FROM user_segments WHERE user_id = %s", (user_id,))
    # 2. Redis에서 핫 메트릭 조회
    streak = redis.get(f"user:{user_id}:streak_count") or 0
    token_balance = redis.get(f"user:{user_id}:cyber_token_balance") or 0
    last_corporate_visit = db.query_last_corporate_visit(user_id)
    corporate_token_count = db.query_monthly_earned_tokens(user_id)
    
    # 3. 보상 확률 / 추천 전략 기본 설정
    if segment.rfm_group == "Whale":
        base_reward_level = 3  # 최고급 보상 추천
        recommended_game = "Roulette"  # 높은 배당 게임 추천
    elif segment.rfm_group == "High Engaged":
        base_reward_level = 2
        recommended_game = "SlotMachine"
    elif segment.rfm_group == "Medium":
        base_reward_level = 1
        recommended_game = "RPSGame"
    else:  # 'Low' or At-risk
        base_reward_level = 0
        recommended_game = "Quiz"  # 재참여 유도용 퀴즈/미션

    # 4. 토큰 잔고 기반 보상 제안
    proposals = []
    if token_balance >= 500:
        proposals.append({
            "type": "HIGH_STAKE",
            "message": f"현재 {token_balance} 토큰 보유 중! 룰렛 한 판에 걸어보세요 → 빅윈 확률 UP",
            "game": "Roulette"
        })
    elif token_balance >= 200:
        proposals.append({
            "type": "MID_STAKE",
            "message": f"토큰이 {token_balance}개 있어요! 슬롯머신으로 안정적인 보상을 노려보세요",
            "game": "SlotMachine"
        })
    else:
        # 토큰 잔고 부족 시 A 업체 유도
        proposals.append({
            "type": "EARN_MORE",
            "message": f"토큰 잔고가 {token_balance}개입니다. A 업체에서 300토큰만 더 모아보세요!",
            "action": "VISIT_CORPORATE_SITE"
        })

    # 5. 리스크 프로필 기반 보상 조정
    if segment.risk_profile == "High-Risk":
        # 큰 베팅 권장
        proposals.append({
            "type": "RISKY_PLAY",
            "message": "위험을 즐기시는군요! 프리미엄 룰렛으로 한 방 노려보세요 → 빅윈 확률 15% UP",
            "game": "Roulette"
        })
    elif segment.risk_profile == "Low-Risk":
        # 소량 베팅 + 안정적 보상
        proposals.append({
            "type": "SAFE_PLAY",
            "message": "안정적인 플레이를 원한다면 슬롯머신 소액 베팅으로 꾸준히 리워드를 쌓아보세요",
            "game": "SlotMachine"
        })

    # 6. A 업체 미션 제안
    if time_since(last_corporate_visit) > timedelta(days=7):
        proposals.append({
            "type": "CORPORATE_ENGAGE",
            "message": "마지막 A 방문이 일주일 전이네요! 지금 로그인만 해도 100토큰 보상",
            "action": "VISIT_CORPORATE_SITE"
        })
    elif corporate_token_count < 500:
        proposals.append({
            "type": "CORPORATE_MISSION",
            "message": "이번 달 토큰 획득이 {corporate_token_count}개예요. A 업체에서 퀴즈 풀고 200토큰 받으세요!",
            "action": "COMPLETE_CORPORATE_QUIZ"
        })

    # 7. 최종 추천 객체 반환
    return {
        "recommended_game": recommended_game,
        "proposals": proposals
    }
```

#### 결과 예시 (JSON):
```json
{
  "recommended_game": "SlotMachine",
  "proposals": [
    {
      "type": "MID_STAKE",
      "message": "토큰이 250개 있어요! 슬롯머신으로 안정적인 보상을 노려보세요",
      "game": "SlotMachine"
    },
    {
      "type": "SAFE_PLAY",
      "message": "안정적인 플레이를 원한다면 슬롯머신 소액 베팅으로 꾸준히 리워드를 쌓아보세요",
      "game": "SlotMachine"
    },
    {
      "type": "CORPORATE_MISSION",
      "message": "이번 달 토큰 획득이 150개예요. A 업체에서 퀴즈 풀고 200토큰 받으세요!",
      "action": "COMPLETE_CORPORATE_QUIZ"
    }
  ]
}
```

> Note: 프론트엔드에서는 이 추천 결과를 받아
> - 메인 대시보드 “오늘의 제안” 카드로 표시
> - “게임 바로가기” 버튼 및 “A 업체로 이동” 버튼 노출

## 2.4. Psychometric Quiz & Micro Survey (F2P 심리학적 활용)
### 2.4.1. 목적
- 유저 성향(Risk-Taker vs. Risk-Averse) 파악
- 개인화된 “토큰 사용 / 보상 선호” 전략 수립
- 도파민 민감도(Dopamine Sensitivity) 지표 획득

### 2.4.2. 구현 세부사항
#### 프론트엔드:
- React Multi-Step Form (2~3문항씩 단계적으로)
- 질문 예시:
  - “높은 배당을 위해 큰 금액을 베팅하는 편인가요?” (1~5)
  - “잃었을 때 다시 도전하는 편인가요?” (Yes/No)
- 완료 시 /api/quiz/submit 호출

#### 백엔드 엔드포인트:
```python
@app.post("/api/quiz/submit")
def submit_quiz(response: QuizResponse, db: Session = Depends(get_db)):
    # QuizResponse: { user_id: int, answers: { q1: int, q2: int, q3: int } }
    # 점수 가중치: Risk-Taker 문항 +1, Risk-Averse 문항 -1
    score = compute_risk_score(response.answers)
    risk_profile = "High-Risk" if score >= 2 else "Low-Risk" if score <= -2 else "Moderate-Risk"
    db.execute(
        "UPDATE user_segments SET risk_profile = %s WHERE user_id = %s",
        (risk_profile, response.user_id)
    )
    db.commit()
    return {"status": "ok", "risk_profile": risk_profile}
```

#### 결과 활용:
- 리스크 프로필에 따라 토큰 사용 제안 / 베팅 권장 전략이 달라짐
- 예:
  - High-Risk: “사이버 토큰 500개로 룰렛 하이 스테이크 도전”
  - Low-Risk: “슬롯머신으로 100개 토큰 소액 베팅하여 꾸준히 모으기”

## 2.5. Analytics & Continuous Personalization
### 2.5.1. 실시간 대시보드 (Monitoring)
#### 역할:
- 관리자용 대시보드에서 주요 KPI 실시간 모니터링
- 일별/월별 토큰 획득량 (A vs. 앱 내)
- 과금 유저 비율 (Whale %), Churn Rate
- 피크 플레이 시간대, 사용자 분포 (RFM 그룹별 비율)

#### 기술 스택:
- ClickHouse / Druid: OLAP 집계
- Grafana / Metabase: 시각화
- Prometheus + Alertmanager: 인프라 성능 및 에러 모니터링

### 2.5.2. 주기적 추천 업데이트
#### 스케줄링:
- Nightly Batch → RFM 업데이트 → 추천 가중치 재계산
- 실시간 Trigger → A 업체에서 토큰 획득 시 즉시 Redis 갱신 → 해당 유저에게 푸시 알림 + “지금 사용하세요” 제안

#### Adaptive Learning Loop:
- 유저가 제안을 클릭하고 “실제 행동”으로 이어지는 비율 추적
- 클릭률, 전환율(토큰 사용 → 빅윈/언락 성공) 기반으로 추천 알고리즘 파라미터 조정

### 2.5.3. 예측 모델 (추가 옵션)
#### Churn Prediction
- 최근 7일간 A 업체 방문 횟수, 앱 내 플레이 빈도, 토큰 잔고, RFM 그룹을 입력으로
- XGBoost/LightGBM 모델로 “7일 내 이탈 가능성” 예측
- 높은 이탈 확률 유저에게 “특별 초대” (A 업체 이벤트) 푸시

#### LTV Prediction
- 과거 30일간 과금 패턴, 플레이 행동, 성인 콘텐츠 언락 이력 등을 기반으로
- 머신러닝 모델(XGBoost) 사용
- LTV가 높은 예측 사용자(Whale Candidate) 에게는 VIP 전용 보상 제공

## 2.6. 주요 테이블 및 필드 요약
| 테이블 | 필드 (Key) | 설명 |
| --- | --- | --- |
| user_actions | id, user_id, action_type, metadata, action_timestamp | 모든 액션 로그 (게임, 이벤트, 토큰 획득/사용 등) |
| user_segments | user_id, rfm_group, risk_profile, streak_count, last_updated | RFM, 심리 프로필, 연속 플레이, 마지막 업데이트 시점 |
| user_rewards | id, user_id, reward_type, reward_value, awarded_at, trigger_action_id | 코인/토큰/성인 콘텐츠 언락 등 모든 보상 내역 |
| adult_content | id, stage, name, description, thumbnail_url, media_url, required_segment_level | 성인 콘텐츠 단계별 메타데이터 |
| notifications | id, user_id, message, is_sent, created_at, sent_at | 푸시/이메일 등 알림 기록 |
| Redis Keys | user:{id}:streak_count<br>user:{id}:last_action_ts<br>user:{id}:cyber_token_balance | 실시간 캐싱 메트릭 (연승, 마지막 액션, 토큰 잔고) |
| site_visits | id, user_id, source, visit_timestamp | A 업체 방문 이력 (source에 “corporate_site” 사용) |
| site_rewards | id, user_id, reward_type, reward_value, issued_at | A 업체에서 지급된 토큰 기록(“EARN_CYBER_TOKENS” 기록과 연동) |

## 2.7. 요약 및 기대 효과
- A 업체 리텐션 ↑
  - “A에서만 얻을 수 있는 사이버 토큰” 구조로, A 업체 방문뿐 아니라 “토큰으로 앱 내 고가치 보상”을 받도록 설계
  - 즉, “앱 → A → 앱”으로 이어지는 순환 루프 형성
- 앱 내 과금 전환율 ↑
  - 사이버 토큰 잔고가 부족하면 A 업체로 유도
  - 토큰 소진 시 “현금 결제”를 통한 충전 유도 (원패스 게임 내 결제 연동)
- 데이터 드리븐 개인화 강화
  - RFM + 토큰 사용 패턴 + 심리 프로필 정보를 결합한 맞춤형 제안
  - 유저의 행동을 지속적으로 학습하여 추천 전략 자동 고도화
- 도파민 루프 최적화
  - Variable-Ratio 보상(가챠, 룰렛) + 즉시 피드백 애니메이션/사운드를 통해 중독성 극대화
  - “한 단계만 더” 심리 자극: “50토큰 남았어요 → 한 번 더 돌리면 확률 UP” 시각화

이로써 “사이버 토큰 = A 업체 이용 보상” 을 핵심 축으로,
“모바일게임식 과금 구조 + 데이터 기반 개인화 + 도파민 루프 강화”가 통합된 F2P 시스템을 완성할 수 있습니다.
## 2.8. Refactoring Guideline Integration
- User segment creation and retrieval logic has been centralized in `UserService`.
- Routers must call `UserService.get_or_create_segment` instead of direct DB access.

<!-- English translation below -->

# Data Personalization (English Translation)

## 2.1. Data Collection Overview 📊

### User Data Sources

#### 1. Mini-game Events 🎲
- Play records from slots, rock-paper-scissors, roulette, etc.
- Results (win/loss), coins/cyber tokens used, number of repetitions, etc.

#### 2. Adult Content Unlock Records 🔓
- Stage-wise unlock timestamps (stage, timestamp)
- Amount of cyber tokens used as unlock triggers

#### 3. User Action Logs 📝
- All interactions: CLAIM_REWARD, VIEW_CONTENT, FAIL_GAME, BUY_ITEM, etc.
- Especially important is the "Cyber Token Acquisition" item

#### 4. Psychological Quizzes and Mini Surveys 🧠
- Short surveys to measure risk propensity, preferences, reward responsiveness, etc.

#### 5. Corporate Usage History 💻
- Number of visits to Company A, dwell time, actions performed
- Amount of cyber tokens rewarded

#### 6. Cohort Metrics 📈
- DAU, MAU, Churn Rate, Cohort-specific survival rates (D1/D7/D14/D30)

## 2.2. RFM + Cyber Token Based User Segmentation
### 2.2.1. Recency-Frequency-Monetary (RFM) Calculation
#### Recency (R):
- Days elapsed since the last action (game play, content unlock, A token acquisition, etc.)
- SQL Example:
```sql
SELECT DATEDIFF(day, MAX(action_timestamp), CURRENT_DATE) 
FROM user_actions 
WHERE user_id = X;
```

#### Frequency (F):
- Total number of actions in the last 30 days (especially "game plays" + "cyber token uses" + "visits to Company A")
- SQL Example:
```sql
SELECT COUNT(*) 
FROM user_actions 
WHERE user_id = X 
  AND action_timestamp >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY);
```

#### Monetary (M):
- Actual amount spent in the last 30 days (total amount of cyber tokens used converted from cash purchases)
- Or total amount of "cyber tokens acquired through Company A"
- SQL Example:
```sql
-- Token usage based on cash payment
SELECT SUM(metadata->>'spent_tokens')::INTEGER 
FROM user_actions 
WHERE user_id = X 
  AND action_type = 'SPEND_CYBER_TOKENS'
  AND action_timestamp >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY);

-- Cumulative amount of tokens acquired from Company A
SELECT SUM(metadata->>'earned_tokens')::INTEGER 
FROM user_actions 
WHERE user_id = X 
  AND action_type = 'EARN_CYBER_TOKENS'
  AND action_timestamp >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY);
```

### 2.2.2. Segment Definitions (Cyber Token Focused)
#### Whale (Top Spenders)
- R ≤ 2 days, F ≥ 30 times (mainly game/mission plays),
- M ≥ 10,000 cyber tokens (including cash payments)
- "Cyber Token Balance" ≥ 1,000 or more

#### High Engaged (Regular Payers)
- R ≤ 5 days, F ≥ 15 times,
- M ≥ 2,000 cyber tokens
- "Visits to Company A" ≥ 5 times/month

#### Medium (Active Users)
- R 6∼15 days, F 5∼14 times,
- M 100∼1,999 cyber tokens
- "Visits to Company A" 2∼4 times/month

#### Low / At-risk (Needs Attention)
- R > 15 days or F < 5 times,
- M < 100 cyber tokens
- "Visits to Company A" 0∼1 time/month

> Note: "Visits to Company A" and "Cyber Token Acquisition" can be treated identically
> However, it is also necessary to track how much "in-game consumption" was made through the tokens acquired from Company A.

### 2.2.3. Implementation and Scheduling
#### Batch Job (Nightly / Once a day)
- user_actions → Retrieve data from the last 30 days to calculate RFM
- Separately aggregate the "number of tokens acquired from Company A"
- Update the user_segments table:
```sql
UPDATE user_segments
SET rfm_group = CASE
  WHEN r <= 2 AND f >= 30 AND m >= 10000 THEN 'Whale'
  WHEN r <= 5 AND f >= 15 AND m >= 2000 THEN 'High Engaged'
  WHEN r <= 15 AND f BETWEEN 5 AND 14 AND m BETWEEN 100 AND 1999 THEN 'Medium'
  ELSE 'Low'
END
WHERE user_id = X;
```

- Update cyber token balance (Redis)
```
user:{id}:cyber_token_balance =
Previous balance + Number of tokens acquired through A in this batch - Number of tokens used in this batch
```

#### Event Trigger (Real-time)
- Every time tokens are acquired from Company A, immediately record EARN_CYBER_TOKENS in user_actions
- Immediately increase Redis key (user:{id}:cyber_token_balance)
- Instant push notification:
```json
{
  "type": "NEW_TOKEN_ARRIVAL",
  "user_id": 123,
  "earned_tokens": 500,
  "message": "You have acquired 500 cyber tokens from Company A! Use them in the game now."
}
```

- Then, when the segment changes through the previously guided RFM work, "grade upgrade rewards" are paid.

## 2.3. Cyber-Token Based Personalized Recommendation Engine
### 2.3.1. Objective
- To induce users to consume as much as possible of the "cyber tokens" they hold through personalization
- To increase app inflow from Company A,
- Recommend "additional missions to acquire tokens from A" or provide opportunities to use the tokens held
- Strengthen the dopamine pathway: provide instant rewards + gradual upgrade plans

### 2.3.2. Input Values
- user_segments table (rfm_group, risk_profile)
- Redis:
  - user:{id}:streak_count (consecutive play count)
  - user:{id}:cyber_token_balance (current cyber token balance)
- Records of using Company A:
  - Latest visit timestamp & event participation record
  - "Number of A token acquisitions this month"

### 2.3.3. Output Values
- Recommended Reward Proposal
  - "Increase the probability of big win on slots with the tokens you have now by 20%"
  - "Unlock Stage 2 Adult Content by spinning the roulette one more time"
  - "Acquire VIP badge by collecting just 300 more tokens at Company A"
- Recommended Mission Proposal
  - "Receive an additional 100 tokens just by logging in to Company A today"
  - "Get 200 token reward + in-depth profile update by participating in the quiz"
- Recommended Usage Window
  - By analyzing the user's play pattern and the most recent visit to A,
  → Indicate the "optimal time zone for the user to access the app" (e.g., 20:00~21:00)

### 2.3.4. Algorithm Sketch (Pseudocode)
```python
def generate_recommendation(user_id):
    # 1. Retrieve user segment
    segment = db.query("SELECT rfm_group, risk_profile FROM user_segments WHERE user_id = %s", (user_id,))
    # 2. Retrieve hot metrics from Redis
    streak = redis.get(f"user:{user_id}:streak_count") or 0
    token_balance = redis.get(f"user:{user_id}:cyber_token_balance") or 0
    last_corporate_visit = db.query_last_corporate_visit(user_id)
    corporate_token_count = db.query_monthly_earned_tokens(user_id)
    
    # 3. Basic settings for reward probability / recommendation strategy
    if segment.rfm_group == "Whale":
        base_reward_level = 3  # Recommend top-level rewards
        recommended_game = "Roulette"  # Recommend high payout game
    elif segment.rfm_group == "High Engaged":
        base_reward_level = 2
        recommended_game = "SlotMachine"
    elif segment.rfm_group == "Medium":
        base_reward_level = 1
        recommended_game = "RPSGame"
    else:  # 'Low' or At-risk
        base_reward_level = 0
        recommended_game = "Quiz"  # Quiz/mission to induce re-participation

    # 4. Reward proposal based on token balance
    proposals = []
    if token_balance >= 500:
        proposals.append({
            "type": "HIGH_STAKE",
            "message": f"You currently have {token_balance} tokens! Bet on the roulette once → Increase the probability of big win",
            "game": "Roulette"
        })
    elif token_balance >= 200:
        proposals.append({
            "type": "MID_STAKE",
            "message": f"You have {token_balance} tokens! Aim for stable rewards on the slot machine",
            "game": "SlotMachine"
        })
    else:
        # Induce to Company A if token balance is insufficient
        proposals.append({
            "type": "EARN_MORE",
            "message": f"Your token balance is {token_balance}. Collect just 300 more tokens at Company A!",
            "action": "VISIT_CORPORATE_SITE"
        })

    # 5. Reward adjustment based on risk profile
    if segment.risk_profile == "High-Risk":
        # Recommend high betting
        proposals.append({
            "type": "RISKY_PLAY",
            "message": "You seem to enjoy risks! Aim for a big win with premium roulette → Increase the probability of big win by 15%",
            "game": "Roulette"
        })
    elif segment.risk_profile == "Low-Risk":
        # Small betting + stable rewards
        proposals.append({
            "type": "SAFE_PLAY",
            "message": "If you want stable play, steadily accumulate rewards with small bets on the slot machine",
            "game": "SlotMachine"
        })

    # 6. Proposal of missions from Company A
    if time_since(last_corporate_visit) > timedelta(days=7):
        proposals.append({
            "type": "CORPORATE_ENGAGE",
            "message": "It's been a week since your last visit to A! Just log in now to receive a reward of 100 tokens",
            "action": "VISIT_CORPORATE_SITE"
        })
    elif corporate_token_count < 500:
        proposals.append({
            "type": "CORPORATE_MISSION",
            "message": "You have acquired {corporate_token_count} tokens this month. Answer the quiz at Company A and receive 200 tokens!",
            "action": "COMPLETE_CORPORATE_QUIZ"
        })

    # 7. Return the final recommendation object
    return {
        "recommended_game": recommended_game,
        "proposals": proposals
    }
```

#### Example Result (JSON):
```json
{
  "recommended_game": "SlotMachine",
  "proposals": [
    {
      "type": "MID_STAKE",
      "message": "You have 250 tokens! Aim for stable rewards on the slot machine",
      "game": "SlotMachine"
    },
    {
      "type": "SAFE_PLAY",
      "message": "If you want stable play, steadily accumulate rewards with small bets on the slot machine",
      "game": "SlotMachine"
    },
    {
      "type": "CORPORATE_MISSION",
      "message": "You have acquired 150 tokens this month. Answer the quiz at Company A and receive 200 tokens!",
      "action": "COMPLETE_CORPORATE_QUIZ"
    }
  ]
}
```

> Note: The front-end will receive this recommendation result to
> - Display it on the main dashboard "Today's Proposal" card
> - Expose "Go to Game" button and "Go to Company A" button

## 2.4. Psychometric Quiz & Micro Survey (F2P Psychological Utilization)
### 2.4.1. Purpose
- Identify user tendencies (Risk-Taker vs. Risk-Averse)
- Establish personalized "token usage/reward preference" strategies
- Obtain dopamine sensitivity indicators

### 2.4.2. Implementation Details
#### Front-end:
- React Multi-Step Form (2-3 questions at a time)
- Example questions:
  - "Do you tend to bet large amounts for high payouts?" (1-5)
  - "Do you try again when you lose?" (Yes/No)
- On completion, call /api/quiz/submit

#### Back-end Endpoint:
```python
@app.post("/api/quiz/submit")
def submit_quiz(response: QuizResponse, db: Session = Depends(get_db)):
    # QuizResponse: { user_id: int, answers: { q1: int, q2: int, q3: int } }
    # Score weights: Risk-Taker questions +1, Risk-Averse questions -1
    score = compute_risk_score(response.answers)
    risk_profile = "High-Risk" if score >= 2 else "Low-Risk" if score <= -2 else "Moderate-Risk"
    db.execute(
        "UPDATE user_segments SET risk_profile = %s WHERE user_id = %s",
        (risk_profile, response.user_id)
    )
    db.commit()
    return {"status": "ok", "risk_profile": risk_profile}
```

#### Utilization of Results:
- Token usage suggestions/betting recommendations vary based on risk profile
- Example:
  - High-Risk: "Challenge high-stakes roulette with 500 cyber tokens"
  - Low-Risk: "Gradually accumulate by betting small amounts on the slot machine with 100 tokens"

## 2.5. Analytics & Continuous Personalization
### 2.5.1. Real-time Dashboard (Monitoring)
#### Role:
- Real-time monitoring of key KPIs on the admin dashboard
- Daily/Monthly token acquisition amount (A vs. in-app)
- Paying user ratio (Whale %), Churn Rate
- Peak play times, user distribution (by RFM group)

#### Tech Stack:
- ClickHouse / Druid: OLAP aggregation
- Grafana / Metabase: Visualization
- Prometheus + Alertmanager: Infrastructure performance and error monitoring

### 2.5.2. Periodic Recommendation Updates
#### Scheduling:
- Nightly Batch → RFM update → Recalculate recommendation weights
- Real-time Trigger → Immediately update Redis when tokens are acquired from Company A → Push notification to the user + "Use now" suggestion

#### Adaptive Learning Loop:
- Track the ratio of users clicking on suggestions and leading to "actual actions"
- Adjust recommendation algorithm parameters based on click-through rate, conversion rate (token usage → big win/unlock success)

### 2.5.3. Predictive Models (Optional)
#### Churn Prediction
- Based on the number of visits to Company A, app play frequency, token balance, and RFM group in the last 7 days
- Predict "likelihood of churn within 7 days" using XGBoost/LightGBM model
- Push "special invitation" (A company event) to users with high churn probability

#### LTV Prediction
- Based on past 30 days' payment patterns, play behavior, adult content unlock history, etc.
- Using machine learning model (XGBoost)
- Provide VIP exclusive rewards to users predicted to have high LTV (Whale Candidate)

## 2.6. Key Tables and Fields Summary
| Table | Field (Key) | Description |
| --- | --- | --- |
| user_actions | id, user_id, action_type, metadata, action_timestamp | All action logs (games, events, token acquisition/usage, etc.) |
| user_segments | user_id, rfm_group, risk_profile, streak_count, last_updated | RFM, psychological profile, consecutive play, last updated time |
| user_rewards | id, user_id, reward_type, reward_value, awarded_at, trigger_action_id | All reward details such as coins/tokens/adult content unlock |
| adult_content | id, stage, name, description, thumbnail_url, media_url, required_segment_level | Metadata of adult content by stage |
| notifications | id, user_id, message, is_sent, created_at, sent_at | Notification records such as push/email |
| Redis Keys | user:{id}:streak_count<br>user:{id}:last_action_ts<br>user:{id}:cyber_token_balance | Real-time caching metrics (winning streak, last action, token balance) |
| site_visits | id, user_id, source, visit_timestamp | Visit history to Company A (use "corporate_site" in source) |
| site_rewards | id, user_id, reward_type, reward_value, issued_at | Token records issued by Company A (linked with "EARN_CYBER_TOKENS" records) |

## 2.7. Summary and Expected Effects
- Increased retention for Company A ↑
  - Designed with a structure of "cyber tokens obtainable only at A", not only for visiting Company A but also for receiving "high-value rewards in the app with tokens"
  - In other words, forming a循環ループ leading from "app → A → app"
- Increased in-app payment conversion rate ↑
  - Induce visits to Company A if the cyber token balance is insufficient
  - Induce charging through "cash payment" when tokens are exhausted (linked with in-game payment in One-Pass game)
- Strengthened data-driven personalization
  - Customized proposals combining RFM + token usage patterns + psychological profile information
  - Continuously learn user behavior to automatically advanced recommendation strategies
- Optimized dopamine loop
  - Maximizing addiction through Variable-Ratio rewards (gacha, roulette) + instant feedback animations/sounds
  - Psychological stimulation of "just one more step": Visualization of "50 tokens left → If you spin once more, probability UP"

Thus, with "cyber tokens = rewards for using Company A" as the core axis,
We can complete the F2P system integrated with "mobile game-like charging structure + data-based personalization + dopamine loop enhancement".
## 2.8. Refactoring Guideline Integration
- User segment creation and retrieval logic has been centralized in `UserService`.
- Routers must call `UserService.get_or_create_segment` instead of direct DB access.

