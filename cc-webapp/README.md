# CC Webapp - Comprehensive Entertainment Platform

## 🌟 Project Overview

CC Webapp is a modern, full-stack web application designed to provide an engaging and interactive user experience through a variety of mini-games, personalized content, and reward systems. It features a Next.js frontend and a Python FastAPI backend, supported by PostgreSQL, Redis, and Kafka for data management and asynchronous task processing. The entire application is containerized using Docker and orchestrated with Docker Compose for ease of development, deployment, and scaling.

This project aims to deliver a rich user journey with features like:
-   Interactive mini-games (Slots, Rock-Paper-Scissors, Roulette).
-   Personalized adult content unlocking based on user engagement and segmentation.
-   A gacha system for rewards.
-   User profiles with personalized recommendations.
-   Real-time notifications and emotion-driven feedback.

## 🛠️ Prerequisites

기본 인증 설정:
```env
# 기본 인증 설정
JWT_SECRET=매우_안전한_시크릿_키
AUTHORIZED_USERS_ONLY=true
```

추가 참고사항:
- 제한된 사용자 환경
- 사전 승인된 계정만 접근 가능

## 🚀 Getting Started / Running with Docker Compose

This is the recommended way to run the entire CC Webapp stack for local development and testing.

1.  **Clone the Repository:**
    If you haven't already, clone this repository to your local machine.

2.  **Environment Configuration (`.env` file):**
    *   At the root of the `cc-webapp` project, create a `.env` file. This file will store environment variables that Docker Compose will use to configure the services.
    *   You can use `cc-webapp/backend/.env.example` as a template for backend-specific variables, but your root `.env` file should contain variables used by `docker-compose.yml`, such as:
        ```env
        # PostgreSQL Settings
        POSTGRES_USER=cc_user
        POSTGRES_PASSWORD=cc_secret_password
        POSTGRES_DB=cc_webapp_db
        POSTGRES_PORT=5432 # Host port for PostgreSQL

        ### 삭제됨 Redis Settings
        REDIS_PORT=6379 # Host port for Redis

        ### 삭제됨 Kafka Settings
        KAFKA_HOST_PORT=9093 # Host port for Kafka broker access

        # Backend Settings
        BACKEND_PORT=8000 # Host port for Backend API
        JWT_SECRET=a_very_secure_secret_for_jwt_please_change_this_for_production

        # Frontend Settings
        FRONTEND_PORT=3000 # Host port for Frontend App

        # Sentry (Optional - for error tracking)
        # SENTRY_DSN=your_sentry_dsn_here

        # Environment type (development, staging, production)
        ENVIRONMENT=development
        ```
    *   Adjust these values as needed for your local setup, especially ports if defaults are taken.

3.  **Build and Run the Application:**
    *   Navigate to the root of the `cc-webapp` project directory in your terminal.
    *   Execute the following command:
        ```bash
        docker-compose up --build -d
        ```
        *   `--build`: Forces Docker Compose to build the images for the `backend` and `frontend` services before starting them. This is useful on the first run or after code changes.
        *   `-d`: Runs the containers in detached mode (in the background).
    *   This command will:
        *   Pull necessary base images (PostgreSQL, Redis, Kafka, Zookeeper, Node, Python).
        *   Build the custom Docker images for the `backend` and `frontend` as per their respective `Dockerfiles`.
        *   Start all defined services in the correct order due to `depends_on` and `healthcheck` configurations.
        *   The backend's `entrypoint.sh` script will automatically run database migrations (`alembic upgrade head`) after the database is ready.

4.  **Accessing the Services:**
    Once all containers are up and healthy (check with `docker-compose ps`):
    *   **Frontend Application:** Open your web browser and navigate to `http://localhost:3000` (or the port specified by `FRONTEND_PORT` in your `.env` file).
    *   **Backend API:** The API will be accessible at `http://localhost:8000` (or `BACKEND_PORT`).
        *   **API Documentation (Swagger UI):** `http://localhost:8000/docs`
        *   **Health Check:** `http://localhost:8000/health`
        *   **Prometheus Metrics:** `http://localhost:8000/metrics`

5.  **Viewing Logs:**
    To view logs from all running services:
    ```bash
    docker-compose logs -f
    ```
    To view logs for a specific service (e.g., `backend`):
    ```bash
    docker-compose logs -f backend
    ```

##  останавливать приложение (Stopping the Application)

To stop all running services and remove the containers:
```bash
docker-compose down
```
If you also want to remove the named volume used by PostgreSQL (this will delete database data):
```bash
docker-compose down -v
```

## 🧪 Running Tests

Tests can be run against the services managed by Docker Compose or locally using virtual environments/npm.

### Backend Tests (Pytest)

*   **Via Docker Compose (recommended for integration tests):**
    ```bash
    docker-compose exec backend pytest tests/
    ```
*   **Locally (requires manual setup of DB, Redis, Kafka):**
    Refer to `cc-webapp/backend/README.md` for instructions on running `pytest` in a local Python virtual environment.

### Frontend Tests (Jest & Cypress)

*   **Unit/Component Tests (Jest) via Docker Compose:**
    ```bash
    docker-compose exec frontend npm test -- --watchAll=false
    ```
*   **Unit/Component Tests (Jest) Locally:**
    Refer to `cc-webapp/frontend/README.md` for instructions on `npm test`.
*   **End-to-End Tests (Cypress):**
    Cypress tests are best run against the application served by `docker-compose up`.
    1.  Ensure all services are running: `docker-compose up -d`
    2.  Open the Cypress Test Runner (from `cc-webapp/frontend` directory):
        ```bash
        npm run cy:open
        # Or, if you prefer to run from project root: cd frontend && npm run cy:open && cd ..
        ```
    3.  Run headlessly:
        ```bash
        npm run cy:run
        ```

## 🤝 How to Contribute (Placeholder)

We welcome contributions! Please follow these general guidelines:
*   **Coding Conventions:**
    *   Backend (Python): Adhere to PEP 8. Use Black for formatting if possible.
    *   Frontend (JavaScript/React): Adhere to common community standards. Use Prettier for formatting.
    *   Aim for clear, readable, and maintainable code.
*   **Testing Guidelines:**
    *   Write unit tests for new backend logic and complex frontend components/utilities.
    *   Write E2E tests for significant user flows.
    *   Ensure all tests pass before submitting pull requests (`npm test`, `pytest`, `npm run cy:run`).
*   **Branching & Pull Requests:**
    *   Create feature branches from `develop` (or `main` if that's the primary development branch).
    *   Ensure your branch is up-to-date with the target branch before submitting a PR.
    *   PRs should be reviewed before merging.
*   **Local Development & Deployment:**
    *   Use Docker Compose for a consistent local development environment that mirrors staging/production closely.
    *   Refer to individual `README.md` files in `backend/` and `frontend/` for more specific development details.

## 📂 Project Structure Overview
*   `.github/workflows/`: CI pipeline configurations (e.g., `ci.yml`).
*   `backend/`: Contains the FastAPI backend application.
    *   `app/`: Core application code (main app, routers, utils, models).
    *   `alembic/`: Database migration scripts.
    *   `scripts/`: Utility scripts (e.g., Kafka consumer).
    *   `tests/`: Pytest unit/integration tests for the backend.
    *   `Dockerfile`: For building the backend Docker image.
    *   `entrypoint.sh`: Handles DB migrations and starts the backend app in Docker.
    *   `README.md`: Backend-specific documentation.
*   `frontend/`: Contains the Next.js frontend application.
    *   `app/`: Page components and layouts (App Router structure).
    *   `components/`: Shared React components.
    *   `hooks/`: Custom React hooks.
    *   `utils/`: Frontend utility functions.
    *   `public/`: Static assets.
    *   `__tests__/`: Jest unit/component tests.
    *   `cypress/`: Cypress E2E tests.
    *   `Dockerfile`: For building the frontend Docker image.
    *   `README.md`: Frontend-specific documentation.
*   `monitoring/`: Example configurations for Prometheus, Grafana, and k6 load tests.
*   `deployment/nginx/`: Example Nginx reverse proxy configuration.
*   `docker-compose.yml`: Orchestrates all services for local development and deployment.
*   `.env.example` (typically in `backend/` or a root example): Template for environment variables.
*   `README.md`: This file - overall project overview and setup.
*   `RELEASE_NOTES_DRAFT.md`: Draft release notes for the current version.
