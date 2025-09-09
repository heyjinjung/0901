3.1. Purpose & Overview
Goal:

사용자 행동을 기반으로 감정 상태(도파민 분비 경로)를 감지하고,

즉각적이고 심리적으로 자극적인 피드백(애니메이션, 사운드, 사이버 토큰 보상)을 제공하여

“행위중독 트리거(Variable‐Ratio Reward + Social Feedback)”와 “도파민 루프”를 극대화

궁극적으로 본사 사이트에서 획득한 사이버 토큰을 앱 내 소비로 연결하고, 앱에서 부족 시 다시 본사로 유도하며 리텐션을 강화함.

핵심 포인트
즉각 피드백(Immediate Feedback):

게임 결과 직후 애니메이션 + 사운드 + 토큰 보상 패키지

재미 요소(시각·청각)와 **사이버 토큰 즉시 획득(또는 감소)**를 결합하여 사용자의 도파민 분비를 유발

행위중독 트리거(Behavioral Addiction Triggers):

Variable‐Ratio Reward Schedule: 슬롯, 룰렛, 가챠 등에서 “언제 당첨될지 모름” 긴장감

Social Proof / Leaderboard: 실시간 랭킹 → 경쟁심 자극

Limited-Time Offer / Flash Event: “본사 사이트 로그인이 2시간 후에 종료됩니다 → 100토큰 보너스”

사이버 토큰 연계:

본사 사이트 이용 시 획득 → Redis에 user:{id}:cyber_token_balance 저장

앱 내 게임·언락 시 사용 → 토큰 잔고 감소

잔고 부족 시 본사 사이트로 즉시 유도 (리디렉션 / 푸시 알림)

3.2. Emotion Matrix & Feedback Triggers
Action Type	Emotion Trigger	Reward Behavior	Feedback Message & Asset
GAME_WIN	Dopamine Surge	+10~50 사이버 토큰(랜덤) + 화려한 애니메이션	“🎉 대박! {earned_tokens} 토큰 획득! 고스피드 플레이 계속!”
(Confetti 애니메이션 + Victory 사운드)
GAME_FAIL	Frustration Loop	–2 사이버 토큰(작은 패널티) + 격려 애니메이션	“😓 아쉽네요… 하지만 곧 보상을 다시 받을 수 있어요!”
(Sad Shake 애니메이션 + Encourage 사운드)
GAME_RETRY	Determination Boost	–1 사이버 토큰(재도전 비용) + 짧은 “다시 도전” 애니메이션	“🔥 한 번 더? 이번엔 확률이 15% 상승했어요!”
(Flash 애니메이션 + Beat 사운드)
DAILY_INACTIVE (>12h)	Concern	푸시 알림 → 본사 사이트에서 +100 토큰 보상 제안	“⌛ 오랜만이네요! 본사 사이트 로그인만 해도 100토큰 드려요!”
(Ring 톤 + 토큰 이미지 애니메이션)
REWARD_CLAIM	Satisfaction	+ 일정량 사이버 토큰(콘텐츠 언락 보너스)	“👏 보상 획득! {item_name} 언락 완료. 다음 보상까지 {next_threshold}토큰 남음”
(Unlock 애니메이션 + Cheer 사운드)
QUIZ_COMPLETE	Curiosity/Engagement	+200 토큰(본사 사이트 퀴즈) + 리스크 프로필 반영	“🧠 퀴즈 완료! 당신은 {risk_profile}형 플레이어군요. 맞춤 리워드를 추천해드릴게요!”

Note: 각 상황별로 “애니메이션+사운드+토큰 증감” 패키지가 한 세트로 묶여, 유저의 감정 상태(도파민 분비)와 직결되도록 설계.

3.3. FastAPI Endpoint Integration

#### 3.3.1. Enhanced Emotion Feedback Endpoints

```python
# Original emotion feedback endpoint
@app.post("/api/feedback", response_model=FeedbackResponse)
def get_feedback(req: FeedbackRequest, db=Depends(get_db), redis=Depends(get_redis)):
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    entry = emotion_matrix.get(req.action_type)
    if not entry:
        # 기본 피드백
        return {"emotion": "neutral", "message": "계속 진행해보세요!", "animation": None, "sound": None, "token_delta": 0}
    
    # 토큰 증감 계산
    if callable(entry["token_delta"]):
        # 연승/연패 등 streak를 고려
        streak = int(redis.get(f"user:{req.user_id}:streak_count") or 0)
        token_change = entry["token_delta"](streak)
    else:
        token_change = entry["token_delta"]
    
    # 토큰 잔고 업데이트
    if token_change != 0:
        redis.incrby(f"user:{req.user_id}:cyber_token_balance", token_change)
    
    # 메시지 포맷팅
    formatted_message = entry["message"].format(
        earned_tokens=token_change if token_change > 0 else 0,
        item_name=req.metadata.get("item_name", ""),
        next_threshold=req.metadata.get("next_threshold", "")
    )
    
    # 마지막 액션 시각 업데이트
    redis.set(f"user:{req.user_id}:last_action_ts", int(datetime.utcnow().timestamp()))
    
    return {
        "emotion": entry["emotion"],
        "message": formatted_message,
        "animation": entry["animation"],
        "sound": entry["sound"],
        "token_delta": token_change
    }
# 🆕 Advanced AI Analysis Endpoint
@app.post("/ai/analyze", response_model=EmotionAnalysisResponse)
def analyze_emotion(req: AnalyzeRequest, db=Depends(get_db)):
    """Advanced emotion analysis with context awareness"""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze(req.text)
    
    return {
        "emotion": result.emotion,
        "score": result.score,
        "confidence": result.confidence,
        "language": result.language,
        "context_aware": bool(req.context)
    }

# 🆕 Personalized Feedback Generation
@app.post("/feedback/generate", response_model=PersonalizedFeedbackResponse)
def generate_feedback(req: FeedbackGenerationRequest, db=Depends(get_db)):
    """Generate emotion-based personalized feedback"""
    service = EmotionFeedbackService()
    feedback = service.generate_feedback(
        emotion=req.emotion,
        segment=req.segment,
        context=req.context
    )
    
    return {
        "success": True,
        "data": {
            "feedback": feedback["message"],
            "template_id": feedback["template_id"],
            "animation_meta": feedback["animation_meta"]
        }
    }

# 🆕 Personalized Recommendations
@app.get("/recommend/personalized", response_model=RecommendationResponse)
def get_personalized_recommendations(
    user_id: int = Query(...),
    emotion: Optional[str] = Query(None),
    segment: Optional[str] = Query(None)
):
    """Get AI-powered personalized game recommendations"""
    service = RecommendationService()
    recommendations = service.get_personalized_recommendations(
        user_id=user_id,
        emotion=emotion,
        segment=segment
    )
    
    return {
        "success": True,
        "data": {
            "recommendations": [
                {
                    "game_type": rec.game_type,
                    "confidence": rec.confidence,
                    "reason": rec.reason,
                    "metadata": rec.metadata
                }
                for rec in recommendations
            ]
        }
    }
```

#### 3.3.2. Enhanced Frontend Integration

```jsx
// Enhanced SlotMachine component with new endpoints
const spin = async () => {
    // 1) Game logic
    const isWin = Math.random() < (0.10 + Math.min(streakCount * 0.01, 0.30));
    
    // 2) Advanced emotion analysis
    const emotionData = await fetch('/ai/analyze', {
        method: 'POST',
        body: JSON.stringify({
            user_id: userId,
            text: isWin ? "슬롯에서 이겼어요!" : "아쉽게 졌네요...",
            context: { game_type: "slot", result: isWin ? "win" : "loss" }
        })
    }).then(r => r.json());
    
    // 3) Get personalized feedback
    const feedbackData = await fetch('/feedback/generate', {
        method: 'POST',
        body: JSON.stringify({
            user_id: userId,
            emotion: emotionData.data.emotion,
            segment: userSegment,
            context: { game_type: "slot", result: isWin ? "win" : "loss" }
        })
    }).then(r => r.json());
    
    // 4) Apply feedback (animation + sound + UI update)
    applyEmotionFeedback(feedbackData.data);
    
    // 5) Get next game recommendation
    const recommendations = await fetch(`/recommend/personalized?user_id=${userId}&emotion=${emotionData.data.emotion}&segment=${userSegment}`)
        .then(r => r.json());
    
    // 6) Show recommendation UI
    showGameRecommendations(recommendations.data.recommendations);
};
```

3.4. Frontend Integration (React 예시)
3.4.1. useEmotionFeedback Hook
jsx
복사
편집
import axios from "axios";

export async function fetchEmotionFeedback(userId, actionType, metadata = {}) {
  const response = await axios.post("/api/feedback", {
    user_id: userId,
    action_type: actionType,
    metadata: metadata
  });
  return response.data; // { emotion, message, animation, sound, token_delta }
}
3.4.2. SlotMachine 컴포넌트 수정 예시
jsx
복사
편집
import React, { useState, useEffect } from "react";
import { fetchEmotionFeedback } from "../hooks/useEmotionFeedback";
import useSound from "use-sound";
import Confetti from "react-confetti"; // 예시로 사용할 수 있는 라이브러리
import { useSelector, useDispatch } from "react-redux";

function SlotMachine({ userId }) {
  const [reels, setReels] = useState([0, 0, 0]);
  const [streakCount, setStreakCount] = useState(0);
  const [feedback, setFeedback] = useState(null);
  const [tokenBalance, setTokenBalance] = useState(0);

  // Redux 또는 Context로부터 사이버 토큰 잔고 구독
  const balance = useSelector(state => state.user.cyberTokenBalance);
  const dispatch = useDispatch();

  // 사운드 준비
  const [playVictory] = useSound("/sounds/victory.mp3");
  const [playEncourage] = useSound("/sounds/encourage.mp3");

  useEffect(() => {
    // 초기 토큰 잔고 로드
    setTokenBalance(balance);
  }, [balance]);

  const spin = async () => {
    // 1) 실제 승리 판정 로직 (variable-ratio 기반)
    const isWin = Math.random() < (0.10 + Math.min(streakCount * 0.01, 0.30));
    const actionType = isWin ? "GAME_WIN" : "GAME_FAIL";
    const metadata = {}; // 추후 필요한 메타데이터 추가

    // 2) emotion feedback 요청
    const data = await fetchEmotionFeedback(userId, actionType, metadata);
    setFeedback(data);

    // 3) 애니메이션 & 사운드
    if (data.animation === "confetti") {
      // Confetti 애니메이션 노출
      // 예: <Confetti numberOfPieces={200} />
      playVictory();
    } else if (data.animation === "shake_sad") {
      playEncourage();
      // 화면 흔들기 등의 추가 이펙트 처리
    }

    // 4) 레일즈(리덕스) 토큰 잔고 업데이트
    if (data.token_delta !== 0) {
      dispatch({ type: "UPDATE_TOKEN_BALANCE", payload: data.token_delta });
    }

    // 5) 스트릭(streak) 관리
    if (isWin) {
      setStreakCount(prev => prev + 1);
      dispatch({ type: "UPDATE_STREAK", payload: streakCount + 1 });
    } else {
      setStreakCount(0);
      dispatch({ type: "UPDATE_STREAK", payload: 0 });
    }

    // 6) 리콤보 신호: 다음 액션 예고 (ex: GAME_RETRY 권장)
    if (!isWin && streakCount >= 2) {
      const retryFeedback = await fetchEmotionFeedback(userId, "GAME_RETRY", {});
      // 화면에 “한 번 더” 토스트 노출
      setFeedback(retryFeedback);
      playEncourage();
      dispatch({ type: "UPDATE_TOKEN_BALANCE", payload: retryFeedback.token_delta });
    }

    // 7) 릴 출력 (0~9 랜덤)
    setReels([
      Math.floor(Math.random() * 10),
      Math.floor(Math.random() * 10),
      Math.floor(Math.random() * 10),
    ]);
  };

  return (
    <div>
      <h2>Slot Machine</h2>
      <div className="reels">
        {reels.map((num, idx) => (
          <div key={idx} className="reel">{num}</div>
        ))}
      </div>
      <button onClick={spin}>Spin</button>
      {feedback && (
        <div className={`feedback ${feedback.emotion}`}>
          {feedback.message}
        </div>
      )}
      <div>Streak: {streakCount}</div>
      <div>Cyber Token Balance: {tokenBalance}</div>
    </div>
  );
}

export default SlotMachine;
주요 특징:

GAME_WIN 시 “도파민 서지” 트리거 → 화려한 콘페티 + 토큰 보상

GAME_FAIL 시 “좌절 → 재도전” 루프 활성화 → 소량 토큰 차감 후 “한 번 더” 유도

리덕스/컨텍스트를 이용해 사이버 토큰 잔고와 스트릭 카운트를 전역 관리

3.5. Psychometric/Survey 피드백 연동
퀴즈 완료(Quiz Complete) 시 /api/feedback 호출 → QUIZ_COMPLETE

리스크 프로필을 기반으로 한 피드백 메시지 + +200 토큰 보상

도파민 피드백: 애니메이션 “quiz_success” + (think.mp3) 사운드

이후 개인화 추천 (02 문서의 Recommendation Engine)에서 risk_profile 활용

3.6. 요약
유저 행동 → FastAPI /api/feedback 호출 →

도파민 루프(애니메이션 + 사운드 + 토큰 증감) 활성화 →

사이버 토큰 잔고가 변동되면 즉시 Redux/Redis → UI 업데이트 →

잔고 부족 시 본사 사이트 리디렉션 → 리텐션 고리 완성

<!-- English translation below -->

# Emotion Feedback (English Translation)

3.1. Purpose & Overview
Goal:

To detect emotional states (dopamine secretion pathways) based on user behavior, and

To provide immediate and psychologically stimulating feedback (animations, sounds, cyber token rewards) to maximize

"Behavioral Addiction Triggers (Variable-Ratio Reward + Social Feedback)" and "Dopamine Loops"

Ultimately, to connect the cyber tokens acquired on the headquarters site to consumption within the app, and to redirect to the headquarters when lacking in the app, thereby strengthening retention.

Key Points
Immediate Feedback:

Animation + Sound + Token Reward Package immediately after game results

Combining fun elements (visual and auditory) with **immediate acquisition (or reduction) of cyber tokens** to induce dopamine secretion in users

Behavioral Addiction Triggers:

Variable-Ratio Reward Schedule: Uncertainty of "when will I win" in slots, roulette, gacha, etc.

Social Proof / Leaderboard: Real-time rankings → Stimulate competitiveness

Limited-Time Offer / Flash Event: "Headquarters site login ends in 2 hours → 100 token bonus"

Linkage with Cyber Tokens:

Acquired when using the headquarters site → Stored in Redis as user:{id}:cyber_token_balance

Used in-app games/unlocks → Decrease in token balance

Immediate guidance to the headquarters site when the balance is insufficient (redirection/push notification)

3.2. Emotion Matrix & Feedback Triggers
Action Type	Emotion Trigger	Reward Behavior	Feedback Message & Asset
GAME_WIN	Dopamine Surge	+10~50 사이버 토큰(랜덤) + 화려한 애니메이션	“🎉 대박! {earned_tokens} 토큰 획득! 고스피드 플레이 계속!”
(Confetti 애니메이션 + Victory 사운드)
GAME_FAIL	Frustration Loop	–2 사이버 토큰(작은 패널티) + 격려 애니메이션	“😓 아쉽네요… 하지만 곧 보상을 다시 받을 수 있어요!”
(Sad Shake 애니메이션 + Encourage 사운드)
GAME_RETRY	Determination Boost	–1 사이버 토큰(재도전 비용) + 짧은 “다시 도전” 애니메이션	“🔥 한 번 더? 이번엔 확률이 15% 상승했어요!”
(Flash 애니메이션 + Beat 사운드)
DAILY_INACTIVE (>12h)	Concern	푸시 알림 → 본사 사이트에서 +100 토큰 보상 제안	“⌛ 오랜만이네요! 본사 사이트 로그인만 해도 100토큰 드려요!”
(Ring 톤 + 토큰 이미지 애니메이션)
REWARD_CLAIM	Satisfaction	+ 일정량 사이버 토큰(콘텐츠 언락 보너스)	“👏 보상 획득! {item_name} 언락 완료. 다음 보상까지 {next_threshold}토큰 남음”
(Unlock 애니메이션 + Cheer 사운드)
QUIZ_COMPLETE	Curiosity/Engagement	+200 토큰(본사 사이트 퀴즈) + 리스크 프로필 반영	“🧠 퀴즈 완료! 당신은 {risk_profile}형 플레이어군요. 맞춤 리워드를 추천해드릴게요!”

Note: Each situation is designed as a set of "Animation + Sound + Token Change" packages, directly linked to the user's emotional state (dopamine secretion).

3.3. FastAPI Endpoint Integration

#### 3.3.1. Enhanced Emotion Feedback Endpoints

```python
# Original emotion feedback endpoint
@app.post("/api/feedback", response_model=FeedbackResponse)
def get_feedback(req: FeedbackRequest, db=Depends(get_db), redis=Depends(get_redis)):
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    entry = emotion_matrix.get(req.action_type)
    if not entry:
        # Default feedback
        return {"emotion": "neutral", "message": "계속 진행해보세요!", "animation": None, "sound": None, "token_delta": 0}
    
    # Calculate token change
    if callable(entry["token_delta"]):
        # Considering streaks like winning/losing streaks
        streak = int(redis.get(f"user:{req.user_id}:streak_count") or 0)
        token_change = entry["token_delta"](streak)
    else:
        token_change = entry["token_delta"]
    
    # Update token balance
    if token_change != 0:
        redis.incrby(f"user:{req.user_id}:cyber_token_balance", token_change)
    
    # Format message
    formatted_message = entry["message"].format(
        earned_tokens=token_change if token_change > 0 else 0,
        item_name=req.metadata.get("item_name", ""),
        next_threshold=req.metadata.get("next_threshold", "")
    )
    
    # Update last action timestamp
    redis.set(f"user:{req.user_id}:last_action_ts", int(datetime.utcnow().timestamp()))
    
    return {
        "emotion": entry["emotion"],
        "message": formatted_message,
        "animation": entry["animation"],
        "sound": entry["sound"],
        "token_delta": token_change
    }
# 🆕 Advanced AI Analysis Endpoint
@app.post("/ai/analyze", response_model=EmotionAnalysisResponse)
def analyze_emotion(req: AnalyzeRequest, db=Depends(get_db)):
    """Advanced emotion analysis with context awareness"""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze(req.text)
    
    return {
        "emotion": result.emotion,
        "score": result.score,
        "confidence": result.confidence,
        "language": result.language,
        "context_aware": bool(req.context)
    }

# 🆕 Personalized Feedback Generation
@app.post("/feedback/generate", response_model=PersonalizedFeedbackResponse)
def generate_feedback(req: FeedbackGenerationRequest, db=Depends(get_db)):
    """Generate emotion-based personalized feedback"""
    service = EmotionFeedbackService()
    feedback = service.generate_feedback(
        emotion=req.emotion,
        segment=req.segment,
        context=req.context
    )
    
    return {
        "success": True,
        "data": {
            "feedback": feedback["message"],
            "template_id": feedback["template_id"],
            "animation_meta": feedback["animation_meta"]
        }
    }

# 🆕 Personalized Recommendations
@app.get("/recommend/personalized", response_model=RecommendationResponse)
def get_personalized_recommendations(
    user_id: int = Query(...),
    emotion: Optional[str] = Query(None),
    segment: Optional[str] = Query(None)
):
    """Get AI-powered personalized game recommendations"""
    service = RecommendationService()
    recommendations = service.get_personalized_recommendations(
        user_id=user_id,
        emotion=emotion,
        segment=segment
    )
    
    return {
        "success": True,
        "data": {
            "recommendations": [
                {
                    "game_type": rec.game_type,
                    "confidence": rec.confidence,
                    "reason": rec.reason,
                    "metadata": rec.metadata
                }
                for rec in recommendations
            ]
        }
    }
```

#### 3.3.2. Enhanced Frontend Integration

```jsx
// Enhanced SlotMachine component with new endpoints
const spin = async () => {
    // 1) Game logic
    const isWin = Math.random() < (0.10 + Math.min(streakCount * 0.01, 0.30));
    
    // 2) Advanced emotion analysis
    const emotionData = await fetch('/ai/analyze', {
        method: 'POST',
        body: JSON.stringify({
            user_id: userId,
            text: isWin ? "슬롯에서 이겼어요!" : "아쉽게 졌네요...",
            context: { game_type: "slot", result: isWin ? "win" : "loss" }
        })
    }).then(r => r.json());
    
    // 3) Get personalized feedback
    const feedbackData = await fetch('/feedback/generate', {
        method: 'POST',
        body: JSON.stringify({
            user_id: userId,
            emotion: emotionData.data.emotion,
            segment: userSegment,
            context: { game_type: "slot", result: isWin ? "win" : "loss" }
        })
    }).then(r => r.json());
    
    // 4) Apply feedback (animation + sound + UI update)
    applyEmotionFeedback(feedbackData.data);
    
    // 5) Get next game recommendation
    const recommendations = await fetch(`/recommend/personalized?user_id=${userId}&emotion=${emotionData.data.emotion}&segment=${userSegment}`)
        .then(r => r.json());
    
    // 6) Show recommendation UI
    showGameRecommendations(recommendations.data.recommendations);
};
```

3.4. Frontend Integration (React 예시)
3.4.1. useEmotionFeedback Hook
jsx
복사
편집
import axios from "axios";

export async function fetchEmotionFeedback(userId, actionType, metadata = {}) {
  const response = await axios.post("/api/feedback", {
    user_id: userId,
    action_type: actionType,
    metadata: metadata
  });
  return response.data; // { emotion, message, animation, sound, token_delta }
}
3.4.2. SlotMachine 컴포넌트 수정 예시
jsx
복사
편집
import React, { useState, useEffect } from "react";
import { fetchEmotionFeedback } from "../hooks/useEmotionFeedback";
import useSound from "use-sound";
import Confetti from "react-confetti"; // 예시로 사용할 수 있는 라이브러리
import { useSelector, useDispatch } from "react-redux";

function SlotMachine({ userId }) {
  const [reels, setReels] = useState([0, 0, 0]);
  const [streakCount, setStreakCount] = useState(0);
  const [feedback, setFeedback] = useState(null);
  const [tokenBalance, setTokenBalance] = useState(0);

  // Redux 또는 Context로부터 사이버 토큰 잔고 구독
  const balance = useSelector(state => state.user.cyberTokenBalance);
  const dispatch = useDispatch();

  // 사운드 준비
  const [playVictory] = useSound("/sounds/victory.mp3");
  const [playEncourage] = useSound("/sounds/encourage.mp3");

  useEffect(() => {
    // 초기 토큰 잔고 로드
    setTokenBalance(balance);
  }, [balance]);

  const spin = async () => {
    // 1) 실제 승리 판정 로직 (variable-ratio 기반)
    const isWin = Math.random() < (0.10 + Math.min(streakCount * 0.01, 0.30));
    const actionType = isWin ? "GAME_WIN" : "GAME_FAIL";
    const metadata = {}; // 추후 필요한 메타데이터 추가

    // 2) emotion feedback 요청
    const data = await fetchEmotionFeedback(userId, actionType, metadata);
    setFeedback(data);

    // 3) 애니메이션 & 사운드
    if (data.animation === "confetti") {
      // Confetti 애니메이션 노출
      // 예: <Confetti numberOfPieces={200} />
      playVictory();
    } else if (data.animation === "shake_sad") {
      playEncourage();
      // 화면 흔들기 등의 추가 이펙트 처리
    }

    // 4) 레일즈(리덕스) 토큰 잔고 업데이트
    if (data.token_delta !== 0) {
      dispatch({ type: "UPDATE_TOKEN_BALANCE", payload: data.token_delta });
    }

    // 5) 스트릭(streak) 관리
    if (isWin) {
      setStreakCount(prev => prev + 1);
      dispatch({ type: "UPDATE_STREAK", payload: streakCount + 1 });
    } else {
      setStreakCount(0);
      dispatch({ type: "UPDATE_STREAK", payload: 0 });
    }

    // 6) 리콤보 신호: 다음 액션 예고 (ex: GAME_RETRY 권장)
    if (!isWin && streakCount >= 2) {
      const retryFeedback = await fetchEmotionFeedback(userId, "GAME_RETRY", {});
      // 화면에 “한 번 더” 토스트 노출
      setFeedback(retryFeedback);
      playEncourage();
      dispatch({ type: "UPDATE_TOKEN_BALANCE", payload: retryFeedback.token_delta });
    }

    // 7) 릴 출력 (0~9 랜덤)
    setReels([
      Math.floor(Math.random() * 10),
      Math.floor(Math.random() * 10),
      Math.floor(Math.random() * 10),
    ]);
  };

  return (
    <div>
      <h2>Slot Machine</h2>
      <div className="reels">
        {reels.map((num, idx) => (
          <div key={idx} className="reel">{num}</div>
        ))}
      </div>
      <button onClick={spin}>Spin</button>
      {feedback && (
        <div className={`feedback ${feedback.emotion}`}>
          {feedback.message}
        </div>
      )}
      <div>Streak: {streakCount}</div>
      <div>Cyber Token Balance: {tokenBalance}</div>
    </div>
  );
}

export default SlotMachine;
주요 특징:

GAME_WIN 시 “도파민 서지” 트리거 → 화려한 콘페티 + 토큰 보상

GAME_FAIL 시 “좌절 → 재도전” 루프 활성화 → 소량 토큰 차감 후 “한 번 더” 유도

리덕스/컨텍스트를 이용해 사이버 토큰 잔고와 스트릭 카운트를 전역 관리

3.5. Psychometric/Survey 피드백 연동
퀴즈 완료(Quiz Complete) 시 /api/feedback 호출 → QUIZ_COMPLETE

리스크 프로필을 기반으로 한 피드백 메시지 + +200 토큰 보상

도파민 피드백: 애니메이션 “quiz_success” + (think.mp3) 사운드

이후 개인화 추천 (02 문서의 Recommendation Engine)에서 risk_profile 활용

3.6. 요약
유저 행동 → FastAPI /api/feedback 호출 →

도파민 루프(애니메이션 + 사운드 + 토큰 증감) 활성화 →

사이버 토큰 잔고가 변동되면 즉시 Redux/Redis → UI 업데이트 →

잔고 부족 시 본사 사이트 리디렉션 → 리텐션 고리 완성

<!-- English translation below -->

# Emotion Feedback (English Translation)

3.1. Purpose & Overview
Goal:

To detect emotional states (dopamine secretion pathways) based on user behavior, and

To provide immediate and psychologically stimulating feedback (animations, sounds, cyber token rewards) to maximize

"Behavioral Addiction Triggers (Variable-Ratio Reward + Social Feedback)" and "Dopamine Loops"

Ultimately, to connect the cyber tokens acquired on the headquarters site to consumption within the app, and to redirect to the headquarters when lacking in the app, thereby strengthening retention.

Key Points
Immediate Feedback:

Animation + Sound + Token Reward Package immediately after game results

Combining fun elements (visual and auditory) with **immediate acquisition (or reduction) of cyber tokens** to induce dopamine secretion in users

Behavioral Addiction Triggers:

Variable-Ratio Reward Schedule: Uncertainty of "when will I win" in slots, roulette, gacha, etc.

Social Proof / Leaderboard: Real-time rankings → Stimulate competitiveness

Limited-Time Offer / Flash Event: "Headquarters site login ends in 2 hours → 100 token bonus"

Linkage with Cyber Tokens:

Acquired when using the headquarters site → Stored in Redis as user:{id}:cyber_token_balance

Used in-app games/unlocks → Decrease in token balance

Immediate guidance to the headquarters site when the balance is insufficient (redirection/push notification)

3.2. Emotion Matrix & Feedback Triggers
Action Type	Emotion Trigger	Reward Behavior	Feedback Message & Asset
GAME_WIN	Dopamine Surge	+10~50 사이버 토큰(랜덤) + 화려한 애니메이션	“🎉 대박! {earned_tokens} 토큰 획득! 고스피드 플레이 계속!”
(Confetti 애니메이션 + Victory 사운드)
GAME_FAIL	Frustration Loop	–2 사이버 토큰(작은 패널티) + 격려 애니메이션	“😓 아쉽네요… 하지만 곧 보상을 다시 받을 수 있어요!”
(Sad Shake 애니메이션 + Encourage 사운드)
GAME_RETRY	Determination Boost	–1 사이버 토큰(재도전 비용) + 짧은 “다시 도전” 애니메이션	“🔥 한 번 더? 이번엔 확률이 15% 상승했어요!”
(Flash 애니메이션 + Beat 사운드)
DAILY_INACTIVE (>12h)	Concern	푸시 알림 → 본사 사이트에서 +100 토큰 보상 제안	“⌛ 오랜만이네요! 본사 사이트 로그인만 해도 100토큰 드려요!”
(Ring 톤 + 토큰 이미지 애니메이션)
REWARD_CLAIM	Satisfaction	+ 일정량 사이버 토큰(콘텐츠 언락 보너스)	“👏 보상 획득! {item_name} 언락 완료. 다음 보상까지 {next_threshold}토큰 남음”
(Unlock 애니메이션 + Cheer 사운드)
QUIZ_COMPLETE	Curiosity/Engagement	+200 토큰(본사 사이트 퀴즈) + 리스크 프로필 반영	“🧠 퀴즈 완료! 당신은 {risk_profile}형 플레이어군요. 맞춤 리워드를 추천해드릴게요!”

Note: Each situation is designed as a set of "Animation + Sound + Token Change" packages, directly linked to the user's emotional state (dopamine secretion).

3.3. FastAPI Endpoint Integration

#### 3.3.1. Enhanced Emotion Feedback Endpoints

```python
# Original emotion feedback endpoint
@app.post("/api/feedback", response_model=FeedbackResponse)
def get_feedback(req: FeedbackRequest, db=Depends(get_db), redis=Depends(get_redis)):
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    entry = emotion_matrix.get(req.action_type)
    if not entry:
        # Default feedback
        return {"emotion": "neutral", "message": "계속 진행해보세요!", "animation": None, "sound": None, "token_delta": 0}
    
    # Calculate token change
    if callable(entry["token_delta"]):
        # Considering streaks like winning/losing streaks
        streak = int(redis.get(f"user:{req.user_id}:streak_count") or 0)
        token_change = entry["token_delta"](streak)
    else:
        token_change = entry["token_delta"]
    
    # Update token balance
    if token_change != 0:
        redis.incrby(f"user:{req.user_id}:cyber_token_balance", token_change)
    
    # Format message
    formatted_message = entry["message"].format(
        earned_tokens=token_change if token_change > 0 else 0,
        item_name=req.metadata.get("item_name", ""),
        next_threshold=req.metadata.get("next_threshold", "")
    )
    
    # Update last action timestamp
    redis.set(f"user:{req.user_id}:last_action_ts", int(datetime.utcnow().timestamp()))
    
    return {
        "emotion": entry["emotion"],
        "message": formatted_message,
        "animation": entry["animation"],
        "sound": entry["sound"],
        "token_delta": token_change
    }
# 🆕 Advanced AI Analysis Endpoint
@app.post("/ai/analyze", response_model=EmotionAnalysisResponse)
def analyze_emotion(req: AnalyzeRequest, db=Depends(get_db)):
    """Advanced emotion analysis with context awareness"""
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze(req.text)
    
    return {
        "emotion": result.emotion,
        "score": result.score,
        "confidence": result.confidence,
        "language": result.language,
        "context_aware": bool(req.context)
    }

# 🆕 Personalized Feedback Generation
@app.post("/feedback/generate", response_model=PersonalizedFeedbackResponse)
def generate_feedback(req: FeedbackGenerationRequest, db=Depends(get_db)):
    """Generate emotion-based personalized feedback"""
    service = EmotionFeedbackService()
    feedback = service.generate_feedback(
        emotion=req.emotion,
        segment=req.segment,
        context=req.context
    )
    
    return {
        "success": True,
        "data": {
            "feedback": feedback["message"],
            "template_id": feedback["template_id"],
            "animation_meta": feedback["animation_meta"]
        }
    }

# 🆕 Personalized Recommendations
@app.get("/recommend/personalized", response_model=RecommendationResponse)
def get_personalized_recommendations(
    user_id: int = Query(...),
    emotion: Optional[str] = Query(None),
    segment: Optional[str] = Query(None)
):
    """Get AI-powered personalized game recommendations"""
    service = RecommendationService()
    recommendations = service.get_personalized_recommendations(
        user_id=user_id,
        emotion=emotion,
        segment=segment
    )
    
    return {
        "success": True,
        "data": {
            "recommendations": [
                {
                    "game_type": rec.game_type,
                    "confidence": rec.confidence,
                    "reason": rec.reason,
                    "metadata": rec.metadata
                }
                for rec in recommendations
            ]
        }
    }
```

#### 3.3.2. Enhanced Frontend Integration

```jsx
// Enhanced SlotMachine component with new endpoints
const spin = async () => {
    // 1) Game logic
    const isWin = Math.random() < (0.10 + Math.min(streakCount * 0.01, 0.30));
    
    // 2) Advanced emotion analysis
    const emotionData = await fetch('/ai/analyze', {
        method: 'POST',
        body: JSON.stringify({
            user_id: userId,
            text: isWin ? "슬롯에서 이겼어요!" : "아쉽게 졌네요...",
            context: { game_type: "slot", result: isWin ? "win" : "loss" }
        })
    }).then(r => r.json());
    
    // 3) Get personalized feedback
    const feedbackData = await fetch('/feedback/generate', {
        method: 'POST',
        body: JSON.stringify({
            user_id: userId,
            emotion: emotionData.data.emotion,
            segment: userSegment,
            context: { game_type: "slot", result: isWin ? "win" : "loss" }
        })
    }).then(r => r.json());
    
    // 4) Apply feedback (animation + sound + UI update)
    applyEmotionFeedback(feedbackData.data);
    
    // 5) Get next game recommendation
    const recommendations = await fetch(`/recommend/personalized?user_id=${userId}&emotion=${emotionData.data.emotion}&segment=${userSegment}`)
        .then(r => r.json());
    
    // 6) Show recommendation UI
    showGameRecommendations(recommendations.data.recommendations);
};
```

3.4. Frontend Integration (React 예시)
3.4.1. useEmotionFeedback Hook
jsx
복사
편집
import axios from "axios";

export async function fetchEmotionFeedback(userId, actionType, metadata = {}) {
  const response = await axios.post("/api/feedback", {
    user_id: userId,
    action_type: actionType,
    metadata: metadata
  });
  return response.data; // { emotion, message, animation, sound, token_delta }
}
3.4.2. SlotMachine 컴포넌트 수정 예시
jsx
복사
편집
import React, { useState, useEffect } from "react";
import { fetchEmotionFeedback } from "../hooks/useEmotionFeedback";
import useSound from "use-sound";
import Confetti from "react-confetti"; // 예시로 사용할 수 있는 라이브러리
import { useSelector, useDispatch } from "react-redux";

function SlotMachine({ userId }) {
  const [reels, setReels] = useState([0, 0, 0]);
  const [streakCount, setStreakCount] = useState(0);
  const [feedback, setFeedback] = useState(null);
  const [tokenBalance, setTokenBalance] = useState(0);

  // Redux 또는 Context로부터 사이버 토큰 잔고 구독
  const balance = useSelector(state => state.user.cyberTokenBalance);
  const dispatch = useDispatch();

  // 사운드 준비
  const [playVictory] = useSound("/sounds/victory.mp3");
  const [playEncourage] = useSound("/sounds/encourage.mp3");

  useEffect(() => {
    // 초기 토큰 잔고 로드
    setTokenBalance(balance);
  }, [balance]);

  const spin = async () => {
    // 1) 실제 승리 판정 로직 (variable-ratio 기반)
    const isWin = Math.random() < (0.10 + Math.min(streakCount * 0.01, 0.30));
    const actionType = isWin ? "GAME_WIN" : "GAME_FAIL";
    const metadata = {}; // 추후 필요한 메타데이터 추가

    // 2) emotion feedback 요청
    const data = await fetchEmotionFeedback(userId, actionType, metadata);
    setFeedback(data);

    // 3) 애니메이션 & 사운드
    if (data.animation === "confetti") {
      // Confetti 애니메이션 노출
      // 예: <Confetti numberOfPieces={200} />
      playVictory();
    } else if (data.animation === "shake_sad") {
      playEncourage();
      // 화면 흔들기 등의 추가 이펙트 처리
    }

    // 4) 레일즈(리덕스) 토큰 잔고 업데이트
    if (data.token_delta !== 0) {
      dispatch({ type: "UPDATE_TOKEN_BALANCE", payload: data.token_delta });
    }

    // 5) 스트릭(streak) 관리
    if (isWin) {
      setStreakCount(prev => prev + 1);
      dispatch({ type: "UPDATE_STREAK", payload: streakCount + 1 });
    } else {
      setStreakCount(0);
      dispatch({ type: "UPDATE_STREAK", payload: 0 });
    }

    // 6) 리콤보 신호: 다음 액션 예고 (ex: GAME_RETRY 권장)
    if (!isWin && streakCount >= 2) {
      const retryFeedback = await fetchEmotionFeedback(userId, "GAME_RETRY", {});
      // 화면에 “한 번 더” 토스트 노출
      setFeedback(retryFeedback);
      playEncourage();
      dispatch({ type: "UPDATE_TOKEN_BALANCE", payload: retryFeedback.token_delta });
    }

    // 7) 릴 출력 (0~9 랜덤)
    setReels([
      Math.floor(Math.random() * 10),
      Math.floor(Math.random() * 10),
      Math.floor(Math.random() * 10),
    ]);
  };

  return (
    <div>
      <h2>Slot Machine</h2>
      <div className="reels">
        {reels.map((num, idx) => (
          <div key={idx} className="reel">{num}</div>
        ))}
      </div>
      <button onClick={spin}>Spin</button>
      {feedback && (
        <div className={`feedback ${feedback.emotion}`}>
          {feedback.message}
        </div>
      )}
      <div>Streak: {streakCount}</div>
      <div>Cyber Token Balance: {tokenBalance}</div>
    </div>
  );
}

export default SlotMachine;
주요 특징:

GAME_WIN 시 “도파민 서지” 트리거 → 화려한 콘페티 + 토큰 보상

GAME_FAIL 시 “좌절 → 재도전” 루프 활성화 → 소량 토큰 차감 후 “한 번 더” 유도

리덕스/컨텍스트를 이용해 사이버 토큰 잔고와 스트릭 카운트를 전역 관리

3.5. Psychometric/Survey 피드백 연동
퀴즈 완료(Quiz Complete) 시 /api/feedback 호출 → QUIZ_COMPLETE

리스크 프로필을 기반으로 한 피드백 메시지 + +200 토큰 보상

도파민 피드백: 애니메이션 “quiz_success” + (think.mp3) 사운드

이후 개인화 추천 (02 문서의 Recommendation Engine)에서 risk_profile 활용

3.6. 요약
유저 행동 → FastAPI /api/feedback 호출 →

도파민 루프(애니메이션 + 사운드 + 토큰 증감) 활성화 →

사이버 토큰 잔고가 변동되면 즉시 Redux/Redis → UI 업데이트 →

잔고 부족 시 본사 사이트 리디렉션 → 리텐션 고리 완성

