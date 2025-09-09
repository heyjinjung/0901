# PostgreSQL에서 Microsoft Entra ID (Azure AD) 인증 설정 가이드

이 문서는 Casino-Club F2P 프로젝트의 PostgreSQL 데이터베이스에서 Microsoft Entra ID (구 Azure AD) 인증을 구성하는 방법을 설명합니다.

## 필요 사항

1. Microsoft Entra ID 테넌트
2. PostgreSQL 서버에 액세스 권한
3. VS Code의 PostgreSQL 확장 (최신 버전)

## 1. PostgreSQL 컨테이너 준비

Docker 컨테이너에서 Microsoft Entra ID 인증을 설정하려면 추가 구성이 필요합니다:

```powershell
# 스크립트를 컨테이너에 복사
docker cp scripts/configure-pg-entra-auth.sh cc_postgres:/tmp/

# 스크립트에 실행 권한 부여
docker exec cc_postgres chmod +x /tmp/configure-pg-entra-auth.sh

# 스크립트 실행
docker exec cc_postgres /tmp/configure-pg-entra-auth.sh
```

## 2. PostgreSQL에서 Microsoft Entra ID 사용자 설정

SQL 스크립트를 사용하여 Entra ID 사용자를 PostgreSQL에 설정합니다:

```powershell
# SQL 스크립트를 컨테이너에 복사
docker cp scripts/setup-entra-auth.sql cc_postgres:/tmp/

# SQL 스크립트 실행
docker exec cc_postgres psql -U cc_user -d cc_webapp -f /tmp/setup-entra-auth.sql
```

## 3. VS Code PostgreSQL 확장에서 Entra ID 인증 설정

1. VS Code에서 PostgreSQL 확장을 엽니다.
2. 새 연결을 추가합니다:
   - 서버 이름: localhost
   - 인증 유형: Entra Auth
   - Entra 계정: rhqnrl0103@gmail.com
   - Entra 사용자 이름: rhqnrl0103@gmail.com
   - 데이터베이스: cc_webapp
   - 연결 이름: Local-Postgres
   - 서버 그룹: Servers

## 4. 문제 해결

### 인증 실패 시
- Microsoft Entra ID 토큰이 만료되었을 수 있습니다. VS Code에서 로그아웃 후 다시 로그인해보세요.
- `pg_hba.conf` 설정이 올바른지 확인하세요.
- PostgreSQL에서 Entra ID 사용자가 올바르게 생성되었는지 확인하세요.

### 권한 문제
- Entra ID 사용자에게 적절한 권한이 부여되었는지 확인하세요:
  ```sql
  -- 권한 확인
  SELECT * FROM information_schema.role_table_grants 
  WHERE grantee = 'rhqnrl0103@gmail.com';
  ```

## 5. 보안 고려사항

Microsoft Entra ID 인증은 패스워드 기반 인증보다 더 안전하지만, 다음 사항을 고려하세요:

- 개발 환경에서만 이 설정을 사용하세요.
- 운영 환경에서는 보다 강화된 설정을 사용하세요.
- 테넌트 ID와 같은 민감한 정보는 환경 변수로 관리하세요.

## 6. 추가 자료

- [PostgreSQL 문서: 외부 인증](https://www.postgresql.org/docs/current/auth-methods.html)
- [VS Code PostgreSQL 확장 문서](https://github.com/microsoft/vscode-postgresql)
- [Microsoft Entra ID 인증 개요](https://learn.microsoft.com/azure/active-directory/fundamentals/auth-overview)
