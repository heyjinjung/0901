# PostgreSQL 및 Redis 연결 문제 해결 가이드

이 문서는 Casino-Club F2P 프로젝트의 PostgreSQL 및 Redis 연결 문제를 해결하기 위한 가이드입니다.

## PostgreSQL 비밀번호 인증 오류 해결

### 문제 상황
VS Code PostgreSQL 확장을 사용하여 연결 시도 시 다음 오류가 발생합니다:
```
pgsql: Connection error: Failed to initialize object explorer session: Connection error: connection failed: connection to server at "127.0.0.1", port 5432 failed: FATAL: password authentication failed for user "cc_user"
```

### 원인
1. Docker 컨테이너 내부에서 사용되는 비밀번호와 외부 연결 시 사용되는 비밀번호가 다를 수 있습니다.
2. pg_hba.conf 파일의 인증 방식 설정이 외부 접속을 제한할 수 있습니다.
3. 환경 변수와 실제 사용자 설정이 일치하지 않을 수 있습니다.

### 해결 방법

#### 1. 올바른 비밀번호 확인
```powershell
# PostgreSQL Docker 컨테이너 환경 변수에서 실제 비밀번호 확인
docker exec cc_postgres env | findstr POSTGRES_PASSWORD
```

#### 2. PostgreSQL 사용자 및 비밀번호 재설정
```powershell
# PostgreSQL 컨테이너에 접속
docker exec -it cc_postgres bash

# PostgreSQL에 superuser로 연결
psql -U postgres

# cc_user 비밀번호 변경
ALTER USER cc_user WITH PASSWORD 'new_password';

# 연결 테스트
\c cc_webapp cc_user
```

#### 3. pg_hba.conf 설정 수정 (필요한 경우)
```powershell
# 현재 설정 확인
docker exec cc_postgres cat /var/lib/postgresql/data/pg_hba.conf

# 설정 파일 수정 (필요한 경우)
docker exec -it cc_postgres bash
apt-get update && apt-get install -y nano
nano /var/lib/postgresql/data/pg_hba.conf

# 외부 접속을 위해 다음과 같이 수정:
# host all all 0.0.0.0/0 md5
```

#### 4. PostgreSQL 컨테이너 재시작
```powershell
docker restart cc_postgres
```

## Redis 연결 문제 해결

### 문제 상황
1. Redis 포트(6379)가 호스트로 매핑되어 있지 않음
2. Redis 비밀번호가 설정되어 있으나 알 수 없음

### 해결 방법

#### 1. Redis 포트 매핑 추가
`docker-compose.yml` 파일을 수정하여 Redis 포트 매핑을 추가합니다:

```yaml
redis:
  # 기존 설정...
  ports:
    - "6379:6379"
```

#### 2. Redis 비밀번호 확인 및 설정
```powershell
# Redis Docker 컨테이너 환경 변수에서 비밀번호 확인
docker exec cc_redis env | findstr REDIS_PASSWORD

# Redis 설정 확인
docker exec cc_redis cat /usr/local/etc/redis/redis.conf

# 비밀번호 설정 (필요한 경우)
docker exec -it cc_redis redis-cli
config set requirepass "new_password"
config rewrite
```

#### 3. Redis 컨테이너 재시작
```powershell
docker restart cc_redis
```

## VS Code 확장 설정

### PostgreSQL 확장 설정
1. VS Code에서 PostgreSQL 확장을 설치합니다 (이미 설치되어 있을 경우 건너뜁니다).
2. 새 연결을 추가할 때 다음 설정을 사용합니다:
   - Host: localhost
   - Port: 5432
   - Database: cc_webapp
   - User: cc_user
   - **인증 유형**: Password
   - Password: cc_password
   - 애플리케이션 이름: vscode-pgsql
   - 연결 타임아웃: 15

### Redis 확장 설정
1. VS Code에서 Redis 확장을 설치합니다.
2. 새 연결을 추가할 때 다음 설정을 사용합니다:
   - Host: localhost
   - Port: 6379
   - Password: (올바른 비밀번호 입력)
