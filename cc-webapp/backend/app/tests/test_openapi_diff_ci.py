import json
import os
from pathlib import Path

# 간단한 OpenAPI 계약 변화 감시 스모크
# 다양한 컨테이너/로컬 경로에서 동작하도록 경로 탐색을 유연화

HERE = Path(__file__).resolve()

def _find_openapi_file() -> Path:
    candidates = [
        # 1) 패키지 로컬(app/) 위치(컨테이너 표준)
        HERE.parents[1] / "current_openapi.json",           # /app/app/current_openapi.json
        # 2) 백엔드 루트 위치
        HERE.parents[2] / "current_openapi.json",           # /app/current_openapi.json
        # 3) 레포 루트 기준(cc-webapp/backend/app/..)
        HERE.parents[3] / "backend" / "app" / "current_openapi.json",
        # 4) 구절대 경로(일부 CI 환경 가정)
        Path("/backend/app/current_openapi.json"),
    ]
    for p in candidates:
        if p.exists():
            return p
    # 마지막 수단: 존재하지 않는 기본 경로 반환(검증에서 메시지 표시)
    return candidates[0]

CUR_SPEC = _find_openapi_file()
SNAPSHOT = CUR_SPEC.parent / "openapi_snapshot.json"

REQUIRED_PATHS = [
    "/health",
    "/api/auth/login",
    "/api/actions",
    "/api/shop/buy",
]

def test_openapi_is_valid_json():
    assert CUR_SPEC.exists(), f"current_openapi.json not found: {CUR_SPEC}"
    data = json.loads(CUR_SPEC.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    # 최소 경로 확인
    paths = data.get("paths") or {}
    for p in REQUIRED_PATHS:
        assert p in paths, f"required path missing in OpenAPI: {p}"


def test_openapi_snapshot_diff_is_generated_when_changed():
    # 스냅샷이 있으면 핵심 경로 삭제 같은 파괴적 변경을 거칠게 감지
    if not SNAPSHOT.exists():
        # 스냅샷이 아직 없다면 초기화 단계로 통과(차기 CI에서 비교)
        return
    cur = json.loads(CUR_SPEC.read_text(encoding="utf-8"))
    old = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    cur_paths = set((cur.get("paths") or {}).keys())
    old_paths = set((old.get("paths") or {}).keys())
    removed = old_paths - cur_paths
    # 중요한 경로가 제거되면 실패(필요 시 allowlist 적용)
    breaking = removed.intersection(set(REQUIRED_PATHS))
    assert not breaking, f"Breaking OpenAPI change: required paths removed: {sorted(breaking)}"
