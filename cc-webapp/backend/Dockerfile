FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .
# Normalize line endings for shell scripts to avoid /usr/bin/env: not found
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh || true

# 포트 노출
EXPOSE 8000

# 기본 시작 명령(개발용 --reload). Compose에서 backend는 entrypoint로 마이그레이션 수행 후 이 명령 실행.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
