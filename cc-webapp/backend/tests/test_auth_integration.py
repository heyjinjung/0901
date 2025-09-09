import pytest
pytest.skip("Legacy auth integration 테스트(손상된 문법) 임시 비활성화 — 리팩터 후 복원 예정", allow_module_level=True)

"""(SKIPPED)
원본 파일은 손상된 상태였으며 모든 실행 코드 제거됨.
리팩터 목표:
1) FastAPI TestClient 기반 end-to-end happy path
2) signup -> profile -> refresh -> logout -> 401 검증 순서
3) fixture: create_user, auth_client
"""

# (이 파일은 의도적으로 비어있습니다.)
