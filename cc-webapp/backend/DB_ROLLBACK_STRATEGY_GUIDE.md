# DB 롤백 전략 가이드 (PostgreSQL/SQLite)

## 1. PostgreSQL 환경 롤백 전략
- Alembic upgrade/downgrade 명령으로 마이그레이션 롤백 가능
- 운영 환경에서는 반드시 사전 백업 후 롤백 수행
- 롤백 테스트 자동화: `bash scripts/db_rollback_test.sh`
- 롤백 실패 시: 수동 복구(백업본 복원) 또는 마이그레이션 스크립트 직접 수정 필요
- 롤백 전후 DB 상태를 반드시 검증 (데이터 손실/스키마 불일치 방지)

## 2. SQLite 환경 롤백 전략
- SQLite는 NOT NULL 컬럼 추가 등 일부 마이그레이션 롤백 불가
- 우회 방안: 롤백 전 DB 파일 백업 → 롤백 실패 시 백업본 복구
- 자동화 스크립트: `bash scripts/sqlite_rollback_workaround.sh`
- 테이블 recreate가 필요한 경우, 백업본 복구가 가장 안전
- SQLite는 테스트/개발 환경 전용으로 사용 권장

## 3. 공통 안전 수칙
- 롤백/마이그레이션 전 반드시 DB 백업
- 운영/테스트 환경 분리, .env로 DB 경로/URL 관리
- 롤백 자동화 스크립트 활용, 실패 시 즉시 복구
- 롤백 전략 및 절차를 문서화하여 팀원과 공유
- CI/CD 파이프라인에 롤백/복구 테스트 포함 권장

## 4. 예시: 롤백 절차
1. DB 백업 수행 (운영: pg_dump, 개발: 파일 복사)
2. Alembic upgrade/downgrade 실행
3. 롤백 실패 시 백업본 복구
4. 복구 후 DB 상태/데이터 검증
5. 문제 발생 시 즉시 담당자/팀에 공유

---
문의: 담당자 또는 DB 관리자에게 문의
