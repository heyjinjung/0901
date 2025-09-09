# Casino-Club F2P 프로젝트 데이터베이스 연결 가이드

이 문서는 Casino-Club F2P 프로젝트에서 PostgreSQL 및 Redis 데이터베이스에 연결하기 위한 세부 정보를 제공합니다.

## 1. PostgreSQL 연결 정보

### 명령줄 접속 (Docker 내부)
```bash
# Docker 컨테이너 내에서 접속
docker exec cc_postgres psql -U cc_user -d cc_webapp

# 비밀번호 입력 필요 시
docker exec cc_postgres psql -U cc_user -d cc_webapp -W
# 비밀번호: cc_password
```

### IDE/외부 도구 접속
```
# 연결 정보
호스트: localhost
포트: 5432
데이터베이스: cc_webapp
사용자 이름: cc_user
비밀번호: cc_password
```

### VS Code PostgreSQL 확장 설정
1. 왼쪽 사이드바에서 PostgreSQL 확장 아이콘 클릭
2. 새 연결 추가 버튼 클릭
3. 다음과 같이 입력:
   - 서버 이름: localhost
   - 인증 유형: Password
   - 사용자 이름: cc_user
   - 비밀번호: cc_password
   - 데이터베이스: cc_webapp
   - 연결 이름: Local-Postgres
   - 서버 그룹: Servers
   - 포트: 5432
   - 애플리케이션 이름: vscode-pgsql
   - 연결 타임아웃: 15

## 2. Redis 연결 정보

### 명령줄 접속 (Docker 내부)
```bash
# Redis CLI 접속 
docker exec -it cc_redis redis-cli

# 인증 필요 시
docker exec -it cc_redis redis-cli
> AUTH <비밀번호>  # 비밀번호 확인 필요
```

### 외부 도구 접속 (Redis Commander)
현재 Redis는 외부 포트가 매핑되어 있지 않아 접속이 불가합니다. 외부 접속을 위한 포트 매핑 구성이 필요합니다.

#### Redis 외부 접속 가능하게 설정하는 방법
1. `docker-compose.yml` 파일을 수정:
   ```yaml
   services:
     redis:
       ports:
         - "6379:6379"  # 이 라인 추가
   ```

2. 컨테이너 재시작:
   ```powershell
   docker-compose up -d redis
   ```

3. Redis Commander 연결 설정:
   ```
   호스트: localhost
   포트: 6379
   이름: cc_redis
   ```

## 3. Microsoft Entra ID (Azure AD) 인증 설정

### VS Code에서 Entra ID 인증 사용
현재 설정은 Microsoft Entra ID (구 Azure AD) 인증을 사용하도록 변경되었습니다. 자세한 설정 방법은 [POSTGRESQL_ENTRA_AUTH_SETUP.md](./POSTGRESQL_ENTRA_AUTH_SETUP.md) 문서를 참조하세요.

### 필요한 구성 단계
1. PostgreSQL 컨테이너에 Entra ID 인증 설정 적용
2. 데이터베이스에 Entra ID 사용자 및 권한 설정
3. VS Code PostgreSQL 확장에서 Entra ID 인증 방식 선택

## 4. 주의사항 및 팁

### PostgreSQL 인증 관련
- Docker 내부에서는 일반 비밀번호 인증을 사용하고, IDE에서는 Entra ID 인증을 사용합니다.
- pg_hba.conf 설정에 따라 인증 방식이 다를 수 있습니다.
- 문제 발생 시 인증 방식을 확인해보세요: `docker exec cc_postgres cat /var/lib/postgresql/data/pg_hba.conf`

### Redis 보안 관련
- Redis는 기본적으로 인증이 필요합니다.
- 운영 환경에서는 외부 포트 노출을 최소화하는 것이 좋습니다.

### 데이터베이스 백업
```powershell
# PostgreSQL 백업
.\docker-manage.ps1 backup

# 또는 직접 명령어 사용
docker exec cc_postgres pg_dump -U cc_user cc_webapp > backup_$(Get-Date -Format "yyyyMMdd").sql
```

## 4. 트러블슈팅

### PostgreSQL 연결 오류
- **인증 실패**: 올바른 비밀번호 확인 (Docker 내부: cc_password, 외부: password123)
- **연결 거부**: 포트 매핑 및 pg_hba.conf 설정 확인
- **DB 없음**: 데이터베이스가 생성되었는지 확인 후 필요시 생성

### Redis 연결 오류
- **연결 거부**: 포트 매핑 확인
- **인증 실패**: 올바른 비밀번호 확인
- **권한 문제**: Redis 설정 파일에서 보안 설정 확인

## 5. 참고 자료
- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)
- [Redis 공식 문서](https://redis.io/documentation)
- [Docker Compose 네트워킹](https://docs.docker.com/compose/networking/)
