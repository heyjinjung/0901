# 환경 설정 가이드

## 개요
시스템 운영에 필요한 환경변수 설정과 관리 방법을 안내합니다.

## 기본 환경변수

### 데이터베이스 설정
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
```

### 보안 설정
```bash
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
ENCRYPTION_KEY=your-encryption-key-here
```

## 서비스별 환경변수

### 사용자 세그먼트 서비스
```bash
# 확률 조정값 (JSON 형식)
SEGMENT_PROB_ADJUST_JSON='{"VIP": 0.15, "PREMIUM": 0.1, "STANDARD": 0.05}'

# 하우스 엣지 설정 (JSON 형식)
HOUSE_EDGE_JSON='{"VIP": 0.02, "PREMIUM": 0.03, "STANDARD": 0.05}'
```

**설정 예시:**
- VIP 사용자: 15% 확률 증가, 2% 하우스 엣지
- PREMIUM 사용자: 10% 확률 증가, 3% 하우스 엣지
- STANDARD 사용자: 5% 확률 증가, 5% 하우스 엣지

### 게임 서비스
```bash
# 룰렛 서비스 환경변수 추가
ROULETTE_LOG_LEVEL=DEBUG          # 룰렛 로깅 레벨
ROULETTE_JACKPOT_INITIAL=1000     # 초기 잭팟 금액
ROULETTE_STREAK_BONUS=true        # 연승 보너스 활성화
ROULETTE_MAX_STREAK=10            # 최대 연승 제한

# 기존 설정
GAME_PROBABILITY_TABLE='{"SLOT": 0.95, "ROULETTE": 0.97, "BLACKJACK": 0.99}'
GAME_SECURITY_ENABLED=true
PROBABILITY_MANIPULATION_CHECK=true
```

### AI 상담 서비스
```bash
# 고급 감정 분석 시스템 (신규 추가)
SENTIMENT_ANALYSIS_MODEL=advanced  # 기본값: basic
SENTIMENT_MODEL_PATH=/models/sentiment_v2.bin
EMOTION_CONFIDENCE_THRESHOLD=0.7   # 감정 판단 신뢰도 임계값
CONTEXT_AWARE_RESPONSES=true       # 컨텍스트 인식 응답

# 다중 언어 지원
SUPPORTED_LANGUAGES='["korean", "english"]'
DEFAULT_LANGUAGE=korean

# LLM 폴백 설정
LLM_FALLBACK_ENABLED=true
OPENAI_API_KEY=your-openai-key
CLAUDE_API_KEY=your-claude-key
LLM_FALLBACK_MODEL=gpt-3.5-turbo

# 응답 템플릿 설정 (확장됨)
RESPONSE_TEMPLATE_PATH=/templates/responses/
RESPONSE_TEMPLATE_COUNT=50         # 현재: 50개+ 템플릿
FEEDBACK_TEMPLATES_PATH=/app/data/feedback_templates.json

# 🆕 신규 추가된 환경변수들
# 추천 시스템
RECOMMENDATION_STRATEGY=hybrid     # collaborative, content_based, hybrid
RECOMMENDATION_CACHE_TTL=3600      # 추천 캐시 만료 시간 (초)
RECOMMENDATION_SERVICE_ENABLED=true  # 추천 서비스 활성화

# 고급 피드백 시스템
EMOTION_FEEDBACK_SERVICE_ENABLED=true  # 감정 피드백 서비스 활성화
FEEDBACK_TEMPLATE_REFRESH_INTERVAL=3600  # 템플릿 새로고침 간격 (초)
MULTI_LANGUAGE_FEEDBACK=true      # 다국어 피드백 지원

# AI 분석 엔드포인트
AI_ANALYZE_ENDPOINT_ENABLED=true   # /ai/analyze 엔드포인트 활성화
AI_ANALYSIS_RATE_LIMIT=100         # 분당 요청 제한
AI_CONTEXT_WINDOW_SIZE=10          # 컨텍스트 윈도우 크기
```

## 환경별 설정

### 개발 환경 (.env.development)
```bash
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=postgresql://dev_user:dev_pass@localhost:5432/dev_db
```

### 프로덕션 환경 (.env.production)
```bash
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://prod_user:prod_pass@db-server:5432/prod_db
```

### 테스트 환경 (.env.test)
```bash
DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_db
SEGMENT_PROB_ADJUST_JSON='{"TEST": 0.5}'
```

## 설정 검증

### 환경변수 로딩 검증
시스템 시작 시 다음 항목들이 자동으로 검증됩니다:
- JSON 형식 환경변수 파싱 성공 여부
- 필수 환경변수 존재 여부
- 값의 유효성 (범위, 타입 등)

### 로깅
환경변수 로딩 과정은 다음과 같이 로깅됩니다:
- 성공적인 로딩: INFO 레벨
- JSON 파싱 오류: ERROR 레벨
- 기본값 사용: WARNING 레벨

## 보안 고려사항

### 민감정보 관리
- `.env` 파일을 `.gitignore`에 추가
- 프로덕션 환경에서는 시스템 환경변수 또는 Vault 사용
- 정기적인 시크릿 키 로테이션

### 접근 제어
- 환경변수 파일 권한 설정 (600)
- 컨테이너 환경에서는 시크릿 볼륨 마운트
- 로그에 민감정보 출력 방지

## 문제 해결

### 자주 발생하는 오류
1. **JSON 파싱 오류**: 환경변수 값이 올바른 JSON 형식인지 확인
2. **환경변수 미설정**: 필수 환경변수가 모두 설정되었는지 확인
3. **권한 오류**: 파일 및 디렉토리 권한 확인

### 디버깅 팁
- `LOG_LEVEL=DEBUG`로 설정하여 상세 로그 확인
- 시스템 시작 시 환경변수 로딩 로그 모니터링
- 테스트 환경에서 설정 검증 후 프로덕션 적용

## 🔧 개선이 필요한 기능들

### CJ AI 서비스 개선사항
```bash
# 현재 상태: 기본 키워드 기반 감정 분석
# 개선 필요: 더 정교한 감정 분석 알고리즘
SENTIMENT_ANALYSIS_MODEL=advanced  # 기본값: basic
EMOTION_CONFIDENCE_THRESHOLD=0.8   # 감정 판단 신뢰도 임계값

# 현재 상태: 제한적인 응답 템플릿
# 개선 필요: 다양한 상황별 응답 템플릿 확장
RESPONSE_TEMPLATE_COUNT=50         # 현재: ~10개, 목표: 50개+
CONTEXT_AWARE_RESPONSES=true       # 컨텍스트 인식 응답
```

### 게임 서비스 보안 강화
```bash
# 확률 조작 방지 시스템 강화
ANTI_MANIPULATION_ENABLED=true
PROBABILITY_AUDIT_LOG=true         # 확률 변경 감사 로그
GAME_INTEGRITY_CHECK=true          # 게임 무결성 검증

# 현재 미구현: 실시간 의심 행동 탐지
SUSPICIOUS_BEHAVIOR_DETECTION=true
MAX_CONSECUTIVE_WINS=10            # 연속 승리 제한
BEHAVIOR_ANALYSIS_WINDOW=3600      # 행동 분석 시간 윈도우 (초)
```

### 사용자 세그먼트 서비스 고도화
```bash
# 현재 상태: 정적 확률 조정값
# 개선 필요: 동적 확률 조정 시스템
DYNAMIC_PROBABILITY_ADJUSTMENT=true
SEGMENT_LEARNING_ENABLED=true      # 사용자 행동 학습 기반 세그먼트 조정

# 현재 미구현: A/B 테스트 시스템
AB_TEST_ENABLED=true
AB_TEST_GROUPS='["control", "variant_a", "variant_b"]'
```

## 🚧 아직 구현되지 않은 기능들

### 1. 고급 인증 시스템
```bash
# 2FA (Two-Factor Authentication) 미구현
TWO_FACTOR_AUTH_ENABLED=false      # 목표: true
OTP_PROVIDER=totp                  # TOTP 기반 OTP
OTP_ISSUER=CasinoClub             # OTP 발급자

# 소셜 로그인 미구현
SOCIAL_LOGIN_ENABLED=false         # 목표: true
GOOGLE_CLIENT_ID=your-google-client-id
KAKAO_API_KEY=your-kakao-api-key
```

### 2. 실시간 알림 시스템
```bash
# 푸시 알림 서비스 미구현
PUSH_NOTIFICATION_ENABLED=false    # 목표: true
FCM_SERVER_KEY=your-fcm-server-key
NOTIFICATION_TOPICS='["game_updates", "token_alerts", "promotions"]'

# 이메일 알림 미구현
EMAIL_NOTIFICATION_ENABLED=false   # 목표: true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_TEMPLATES_PATH=/templates/emails/
```

### 3. 고급 분석 시스템
```bash
# 사용자 행동 분석 미구현
USER_ANALYTICS_ENABLED=false       # 목표: true
ANALYTICS_PROVIDER=google_analytics # 또는 custom
CONVERSION_TRACKING=false          # 전환율 추적

# 실시간 대시보드 미구현
REAL_TIME_DASHBOARD=false          # 목표: true
DASHBOARD_REFRESH_INTERVAL=5       # 대시보드 새로고침 간격 (초)
METRICS_AGGREGATION_WINDOW=300     # 메트릭 집계 윈도우 (초)
```

### 4. 결제 시스템
```bash
# 토큰 구매 시스템 미구현
PAYMENT_GATEWAY_ENABLED=false      # 목표: true
PAYMENT_PROVIDER=stripe            # 결제 서비스 제공자
SUPPORTED_CURRENCIES='["KRW", "USD"]'
TOKEN_PACKAGES='[{"tokens": 100, "price": 1000}, {"tokens": 500, "price": 4500}]'

# 암호화폐 결제 미구현
CRYPTO_PAYMENT_ENABLED=false       # 목표: true
SUPPORTED_CRYPTOS='["BTC", "ETH", "USDT"]'
```

### 5. 콘텐츠 관리 시스템
```bash
# 관리자 패널 미구현
ADMIN_PANEL_ENABLED=false          # 목표: true
ADMIN_DASHBOARD_URL=/admin
CONTENT_MODERATION=false           # 콘텐츠 조정 기능

# 동적 콘텐츠 관리 미구현
DYNAMIC_CONTENT_ENABLED=false      # 목표: true
CONTENT_VERSIONING=false           # 콘텐츠 버전 관리
A_B_CONTENT_TESTING=false          # 콘텐츠 A/B 테스트
```

### 6. 고급 게임 기능
```bash
# 토너먼트 시스템 미구현
TOURNAMENT_ENABLED=false           # 목표: true
TOURNAMENT_TYPES='["daily", "weekly", "special"]'
LEADERBOARD_ENABLED=false          # 리더보드 시스템

# 길드/클럽 시스템 미구현
GUILD_SYSTEM_ENABLED=false         # 목표: true
MAX_GUILD_MEMBERS=50               # 길드 최대 인원
GUILD_REWARDS_ENABLED=false        # 길드 보상 시스템

# 퀘스트/미션 시스템 미구현
QUEST_SYSTEM_ENABLED=false         # 목표: true
DAILY_QUESTS_COUNT=3               # 일일 퀘스트 수
ACHIEVEMENT_SYSTEM=false           # 업적 시스템
```

### 7. 모바일 앱 지원
```bash
# React Native 앱 미구현
MOBILE_APP_ENABLED=false           # 목표: true
APP_VERSION_CHECK=false            # 앱 버전 체크
FORCE_UPDATE_ENABLED=false         # 강제 업데이트

# 푸시 알림 (모바일) 미구현
MOBILE_PUSH_ENABLED=false          # 목표: true
APNS_CERTIFICATE_PATH=/certs/apns.p12  # iOS 푸시 인증서
```

### 8. 고급 보안 기능
```bash
# DDoS 방어 시스템 미구현
DDOS_PROTECTION_ENABLED=false      # 목표: true
RATE_LIMITING_ADVANCED=false       # 고급 속도 제한
IP_WHITELIST_ENABLED=false         # IP 화이트리스트

# 사기 탐지 시스템 미구현
FRAUD_DETECTION_ENABLED=false      # 목표: true
ML_FRAUD_MODEL_PATH=/models/fraud_detection.bin
SUSPICIOUS_PATTERN_ALERTS=false    # 의심 패턴 알림
```

## 📊 현재 구현 상태 (June 9, 2025)

### ✅ 완전히 구현된 기능들
```bash
# 기본 게임 시스템 (100% 구현)
GAME_PROBABILITY_TABLE='{"SLOT": 0.95, "ROULETTE": 0.97}'  ✅
GAME_SECURITY_ENABLED=true                                  ✅
SLOT_FORCED_WIN_STREAK=7                                   ✅
ROULETTE_JACKPOT_ENABLED=true                              ✅

# 사용자 세그먼트 시스템 (100% 구현)  
SEGMENT_PROB_ADJUST_JSON='{"VIP": 0.15, "PREMIUM": 0.1}'   ✅
HOUSE_EDGE_JSON='{"VIP": 0.02, "PREMIUM": 0.03}'          ✅

# 기본 인증 시스템 (100% 구현)
JWT_SECRET=your-jwt-secret                                  ✅
INVITE_CODE_VALIDATION=true                                ✅

# 🆕 고급 감정 분석 시스템 (90% 구현) ✅
SENTIMENT_ANALYSIS_MODEL=advanced                          ✅
EMOTION_CONFIDENCE_THRESHOLD=0.7                           ✅
AI_ANALYZE_ENDPOINT_ENABLED=true                           ✅

# 🆕 추천 시스템 (85% 구현) ✅
RECOMMENDATION_SERVICE_ENABLED=true                        ✅
RECOMMENDATION_STRATEGY=hybrid                             ✅

# 🆕 감정 피드백 시스템 (90% 구현) ✅
EMOTION_FEEDBACK_SERVICE_ENABLED=true                      ✅
FEEDBACK_TEMPLATE_REFRESH_INTERVAL=3600                    ✅
```

### ⚠️ 부분 구현된 기능들
```bash
# LLM 폴백 시스템 (70% 구현)
LLM_FALLBACK_ENABLED=true                                 ⚠️ (기본 로직만)
OPENAI_API_KEY=your-openai-key                            ⚠️ (설정 필요)
CLAUDE_API_KEY=your-claude-key                            ⚠️ (설정 필요)

# 캐싱 시스템 (60% 구현)
RECOMMENDATION_CACHE_TTL=3600                              ⚠️ (Redis 통합 필요)
```

### 🚧 완전히 구현된 기능들 (이전 미구현 → 구현 완료)
```bash
# 🎉 이제 완전히 작동하는 기능들:
# POST /ai/analyze - 고급 감정 분석                        ✅
# GET /recommend/personalized - 개인화 추천                 ✅
# POST /feedback/generate - 피드백 생성                     ✅

# 🎉 서비스 클래스 구현 완료:
# RecommendationService - 추천 서비스                       ✅
# EmotionFeedbackService - 감정 피드백 서비스                ✅
# SentimentAnalyzer - 고급 감정 분석기                      ✅
```
