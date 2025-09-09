# CC Webapp - Backend

This directory contains the FastAPI backend for the CC Webapp.

## Running the Application

There are two primary ways to run the backend application: using Docker Compose (recommended for a full-stack environment) or running locally using a Python virtual environment (for backend-focused development).

### 1. Running with Docker Compose (Recommended)

This method uses Docker Compose to build and run all services, including the backend, database, Redis, and Kafka, as defined in the main `cc-webapp/docker-compose.yml` file.

1.  **Prerequisites:**
    *   Docker and Docker Compose installed.
2.  **Environment Variables:**
    *   Create a `.env` file in the `cc-webapp` project root (next to `docker-compose.yml`). You can copy `cc-webapp/backend/.env.example` to `cc-webapp/.env` as a starting point, but ensure variable names match those expected by `docker-compose.yml` (e.g., `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `JWT_SECRET`, etc.).
3.  **Build and Start Services:**
    *   Navigate to the main project root directory (`cc-webapp`).
    *   Run the command:
        ```bash
        docker-compose up --build
        ```
    *   This will build the Docker images for the backend and frontend (if not already built) and start all services.
    *   The backend service will be available at `http://localhost:8000` (or the port specified by `BACKEND_PORT` in your `.env` file).
4.  **Database Migrations:**
    *   Database migrations (using Alembic) are automatically run by the `entrypoint.sh` script when the `backend` container starts. You do not need to run `alembic upgrade head` manually when using Docker Compose.

### 2. Local Development (without Docker)

This method is suitable for developing and testing the backend in isolation.

1.  **Prerequisites:**
    *   Python 3.9+ installed.
    *   Access to running instances of PostgreSQL, Redis, and Kafka (their URLs will be needed in the `.env` file).
2.  **Setup:**
    *   Navigate to the `cc-webapp/backend` directory.
    *   Create and activate a Python virtual environment:
        ```bash
        python -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        ```
    *   Install dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    *   Set up environment variables:
        *   Copy `.env.example` to `.env` within the `cc-webapp/backend` directory.
        *   Update variables in this `.env` file to point to your manually managed PostgreSQL, Redis, and Kafka instances.
        *   `SEGMENT_PROB_ADJUST_JSON` 및 `HOUSE_EDGE_JSON` 값을 지정하여 사용자 세그먼트별 확률 조정과 하우스 엣지를 설정할 수 있습니다.
        ```bash
        alembic upgrade head
        ```
3.  **Run the FastAPI Development Server:**
    ```bash
    uvicorn app.main:app --reload --port 8000
    The API will be available at `http://localhost:8000`.

## Monitoring & Health

The backend exposes the following endpoints for monitoring and health checks:

*   **`GET /health`**:
    *   Returns `{"status": "healthy"}`.
    *   This endpoint is used by Docker Compose for the backend service's health check and can be utilized by other monitoring systems to verify application status.
*   **`GET /metrics`**:
    *   Exposes application metrics in Prometheus format. These metrics can be scraped by a Prometheus server for monitoring and alerting.
    *   Includes default metrics provided by `prometheus-fastapi-instrumentator`, such as HTTP request counts, request latencies, and in-progress requests.

## Key Features & Integrations

### 1. Kafka Integration for User Actions
-   All user actions submitted via the `POST /api/actions` endpoint are published as JSON messages to the Kafka topic `topic_user_actions`.
-   The message payload includes `{ user_id, action_type, action_timestamp }`.
-   A consumer script is available at `scripts/kafka_consumer.py` which can be run to observe these messages in real-time:
    ```bash
    python scripts/kafka_consumer.py
    ```
-   This integration requires a Kafka broker running and accessible via the `KAFKA_BROKER` environment variable.

### 2. RFM Batch Job & User Segmentation
-   A daily batch job, `compute_rfm_and_update_segments` (located in `app/utils/segment_utils.py`), calculates Recency, Frequency, and Monetary (RFM) scores for users based on their actions in the last 30 days.
-   This job assigns users to RFM groups (e.g., "Whale", "Medium", "Low") and updates the `rfm_group` and `last_updated` fields in the `user_segments` table.
-   The job is scheduled using APScheduler (`app/apscheduler_jobs.py`) to run:
    -   Daily at 2:00 AM UTC.
    -   Once shortly after application startup for immediate processing in development/testing.
-   The logic for RFM calculation and group assignment should be detailed in the project's technical documentation (`02_data_personalization_en.md`).

### 3. Corporate Site Retention Integration
-   The `POST /api/notify/site_visit` endpoint is used to log instances where a user navigates from the webapp to an external corporate site.
-   It accepts a payload like `{ "user_id": 123, "source": "webapp_button" }`.
-   Logged visits are stored in the `site_visits` table, capturing `user_id`, `source`, and `visit_timestamp`.

### 4. Personalized Recommendation Endpoint
-   The `GET /api/user-segments/{user_id}/recommendation` endpoint provides personalized recommendations for users.
-   It considers the user's:
    -   `rfm_group` (from the `user_segments` table).
    -   `risk_profile` (from the `user_segments` table).
    -   Current `streak_count` (fetched from a Redis key like `user:{user_id}:streak_count`).
-   The endpoint returns a JSON object containing `recommended_reward_probability` and `recommended_time_window`, calculated based on logic outlined in the project's technical documentation (`02_data_personalization_en.md`).
-   Requires Redis to be running and accessible via the `REDIS_URL` environment variable.

## Testing
Unit tests are located in the `tests/` directory and can be run using pytest:
```bash
# Ensure you are in the cc-webapp/backend directory or set PYTHONPATH appropriately
# Example from cc-webapp directory:
# PYTHONPATH=. pytest backend/tests/
# Or from cc-webapp/backend directory:
pytest
```

To run tests via Docker Compose (ensure services are up, e.g., `docker-compose up -d backend db` or the full stack):
```bash
# From the project root (cc-webapp directory)
docker-compose exec backend pytest tests/
```

### Vulnerability Scanning (Backend)

To check for known vulnerabilities in Python dependencies, you can use tools like `pip-audit` or `safety`.

1.  **Using `pip-audit` (Recommended by PyPA):**
    *   Ensure `pip-audit` is installed in your development environment or CI runner:
        ```bash
        pip install pip-audit
        ```
    *   Navigate to the `cc-webapp/backend` directory (where `requirements.txt` is located) and run:
        ```bash
        pip-audit
        ```
    *   To make this a CI check that fails on any vulnerability:
        ```bash
        pip-audit --fail-on-vulnerability
        ```
    *   `pip-audit` uses data from the Python Packaging Advisory Database (PyPI Advisory DB) and others.

2.  **Using `safety` (Alternative):**
    *   Ensure `safety` is installed:
        ```bash
        pip install safety
        ```
    *   Navigate to the `cc-webapp/backend` directory and run:
        ```bash
        safety check -r requirements.txt
        ```
    *   `safety` uses its own vulnerability database (requires a free or commercial license for the latest data, otherwise uses a freely available but potentially delayed database).

Regularly review the output from these tools and update your dependencies in `requirements.txt` as needed, testing thoroughly for compatibility.

---
## 🧩 최근 백엔드 파일 실전 적용/정리 가이드 (누적학습 기준)

### 1. 데이터베이스 초기화/시드/초대코드
- reset_database.py: 전체 테이블 삭제/재생성 + 고정 초대코드(5882, 6969, 6974) 자동 등록. 운영/테스트 환경에서 초기화 필요 시만 사용, 실전 배포 전에는 백업 필수.
- seed_realistic_data.py, seed_and_explain.py: 시드계정만 남기고 가짜 데이터 정리 및 시드계정 상태/쿼리/EXPLAIN 자동화. 운영/테스트 환경에서만 사용, 실전 배포 전에는 백업/정리 권장.

### 2. 토큰/인증 테스트
- token_generator.py, token_test.py, working_token.json, simple_jwt_test.py: JWT 토큰 생성/검증/테스트 자동화 스크립트. 운영에는 미사용, 토큰 구조/테스트 참고만 가능. 실제 인증/테스트는 pytest/conftest.py 기반 자동화만 유지.

### 3. 임시/간이 서버/스키마/유틸
- simple_server.py, simple_schema.py: FastAPI 기반 간이 서버/초기 스키마 생성. 실전 운영에는 미사용, 구조/테스트 참고만 가능. 표준 모델/마이그레이션/엔트리포인트만 유지.
- tmp_inspect_db.py: DB 테이블/버전/구조 확인 유틸. 운영에는 미사용, DB 구조/마이그레이션 참고만 가능.

### 4. 모델/필드/테이블 업데이트
- update_auth_models.py, update_game_fields.py: 인증/게임 모델 필드/테이블 업데이트 스크립트. Alembic 마이그레이션이 표준이므로, 참고/삭제/통합 대상. 실제 운영은 Alembic revision으로만 관리.

### 5. 기타/정리 지침
- 최근 생성/수정된 파일 중, 누적학습 기준과 반대되거나 중복/레거시/테스트/임시/유틸 성격의 파일은 운영/배포 전 반드시 백업/삭제/통합 필요.
- 실전 운영/테스트/배포 시, 표준화된 모델/마이그레이션/테스트/유틸/엔트리포인트만 유지, 나머지는 참고/삭제.
- 신규 멤버/운영자는 conftest.py 기반 자동화 테스트, Alembic 마이그레이션, 표준 모델/엔트리포인트/유틸만 따라도 실전 환경 재현 가능.

---
변경 요약: 최근 백엔드 파일 중 실전 적용/누적학습 기준에 부합하는 내용만 README에 반영, 나머지는 참고/삭제/통합 권장
검증 결과: 최신 기준의 실전 적용/정리/운영/테스트/배포 기준 반영
다음 단계: 불필요/중복/테스트/임시 파일 백업/삭제, 실전 적용 파일만 유지, 신규 구조/테스트/운영 변경 시 본 섹션에 누적 업데이트
