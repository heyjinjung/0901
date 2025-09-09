# 🎰 Casino-Club F2P: 시스템 아키텍처 및 데이터 흐름

이 문서는 Casino-Club F2P 프로젝트의 전체 아키텍처와 주요 기능의 데이터 흐름을 설명합니다.

## 1. 고수준 아키텍처 (High-Level Architecture)

본 프로젝트는 다음과 같은 모듈식 아키텍처를 따릅니다.

-   **Frontend (Next.js):** 사용자가 직접 상호작용하는 UI 계층입니다. React 컴포넌트로 구성되며, 모든 데이터는 백엔드 API를 통해 비동기적으로 요청합니다.
-   **Backend (FastAPI):** 핵심 비즈니스 로직을 처리하는 API 서버입니다. 라우터(Router)와 서비스(Service) 계층으로 명확히 분리되어 있습니다.
    -   **Router:** HTTP 요청을 받아 유효성을 검증하고, 적절한 서비스에 작업을 위임합니다.
    -   **Service:** 실제 비즈니스 로직(게임 규칙, 토큰 계산 등)을 수행하고, 데이터베이스와 상호작용합니다.
-   **Database (PostgreSQL):** 모든 영구 데이터를 저장하는 주 데이터베이스입니다. `users`, `games`, `missions` 등 모든 핵심 정보가 이곳에 저장됩니다.
-   **Cache (Redis):** 자주 변경되거나 빠른 조회가 필요한 데이터(예: 연승 기록)를 임시 저장하여 시스템 성능을 향상시킵니다.
-   **Task Scheduler (APScheduler):** 매일 밤 RFM 스코어를 계산하는 등 주기적인 백그라운드 작업을 실행합니다.

## 2. 핵심 데이터 흐름 예시: 가위바위보(RPS) 게임

사용자가 가위바위보 게임을 한 판 플레이하는 경우의 데이터 흐름은 다음과 같습니다.

1.  **[Frontend] 사용자 입력:**
    *   사용자가 `RPSGame.tsx` 컴포넌트에서 '가위' 버튼을 클릭합니다.
    *   컴포넌트의 `handlePlayerChoice('rock')` 함수가 호출됩니다.

2.  **[Frontend] API 클라이언트 호출:**
    *   `handlePlayerChoice` 함수는 `ApiClient.playRPS('rock', 5000)` 메소드를 호출합니다.

3.  **[API] 백엔드 요청:**
    *   `ApiClient`는 백엔드로 `POST /api/games/rps/play` HTTP 요청을 보냅니다. 요청 본문(body)에는 `{"user_choice": "rock", "bet_amount": 5000}` 데이터가 포함됩니다.

4.  **[Backend] 라우터 수신:**
    *   `rps.py` 라우터의 `@router.post("/play")` 엔드포인트가 요청을 받습니다.
    *   FastAPI가 요청 본문의 유효성을 검증하고, `RPSService`를 `Depends`를 통해 주입받습니다.

5.  **[Backend] 서비스 로직 실행:**
    *   라우터는 주입받은 `rps_service.play()` 메소드를 호출하며, 사용자 ID, 선택, 베팅액을 전달합니다.
    *   `RPSService`는 다음 로직을 순서대로 실행합니다.
        a.  일일 플레이 횟수 제한을 검사합니다 (`GameRepository` -> `user_actions` 테이블 조회).
        b.  사용자의 토큰이 베팅액보다 충분한지 확인합니다 (`TokenService` -> `users` 테이블 조회).
        c.  토큰을 차감합니다 (`TokenService` -> `users` 테이블 `UPDATE`).
        d.  게임의 승/패/무 결과를 결정합니다.
        e.  승리 또는 무승부 시, 보상 토큰을 지급합니다 (`TokenService` -> `users` 테이블 `UPDATE`).
        f.  게임 결과를 `games` 테이블에, 플레이 활동을 `user_actions` 테이블에 `INSERT`합니다 (`GameRepository`).

6.  **[Database] 데이터 변경:**
    *   `users` 테이블의 `cyber_token_balance` 컬럼이 업데이트됩니다.
    *   `games` 테이블과 `user_actions` 테이블에 새로운 레코드가 추가됩니다. 이 모든 과정은 단일 트랜잭션으로 처리되어 데이터 정합성을 보장합니다.

7.  **[Response] 결과 반환:**
    *   `RPSService`는 게임 결과(사용자 선택, 컴퓨터 선택, 승패 여부, 토큰 변화량, 최종 잔액 등)를 담은 `RPSResult` 객체를 라우터에 반환합니다.
    *   라우터는 이 객체를 JSON 형태로 변환하여 프론트엔드에 HTTP 응답으로 보냅니다.

8.  **[Frontend] UI 업데이트:**
    *   `ApiClient`는 응답받은 JSON 데이터를 `useRPSGame` 훅에 전달합니다.
    *   훅은 `setGameState`를 호출하여 컴포넌트의 상태를 업데이트합니다.
    *   React는 변경된 상태에 따라 UI를 다시 렌더링하여, 사용자에게 컴퓨터의 선택과 게임 결과를 보여주고 변경된 토큰 잔액을 표시합니다.

이러한 유기적인 구조를 통해 각 계층은 자신의 역할에만 집중할 수 있으며, 전체 시스템은 안정적이고 확장 가능하게 됩니다.
