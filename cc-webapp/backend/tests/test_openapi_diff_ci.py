import json
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.ci_core

BASE_DIR = Path(__file__).resolve().parent.parent
BASELINE_PATH = BASE_DIR / "current_openapi.json"
# 실제 baseline 은 프로젝트 루트 cc-webapp/backend/current_openapi.json 사용
ALT_BASELINE_PATH = Path(__file__).resolve().parents[2] / "cc-webapp" / "backend" / "current_openapi.json"

client = TestClient(app)

REQUIRED_PATHS = [
    "/health",
    "/api/shop/buy-limited",
]

REQUIRED_SCHEMA = "HealthResponse"
REQUIRED_HEALTH_FIELDS = {"status", "timestamp", "version", "redis_connected"}


def _load_baseline():
    for p in (BASELINE_PATH, ALT_BASELINE_PATH):
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                return json.load(f)
    pytest.skip("OpenAPI baseline (current_openapi.json) not found")


def test_openapi_diff_contract_stable():
    """핵심 경로/스키마가 제거되지 않았고 새 필드(redis_connected)가 포함되었는지 검증.
    - 필수 PATH 존재
    - HealthResponse 스키마에 redis_connected 존재
    - 제거(breaking)된 path 없음 (baseline 대비)
    """
    baseline = _load_baseline()
    live = client.get("/openapi.json").json()

    baseline_paths = set(baseline.get("paths", {}).keys())
    live_paths = set(live.get("paths", {}).keys())

    # 필수 경로 존재
    for p in REQUIRED_PATHS:
        assert p in live_paths, f"필수 경로 누락: {p}"

    # 제거된 경로 (baseline 에 있었는데 live 에 없음) -> 허용 안함 (경고성 실패)
    removed = baseline_paths - live_paths
    # 단, /docs 관련 내부 경로 제외 가능 (현재 없음) -> 바로 assert
    assert not removed, f"OpenAPI 경로 제거 감지: {removed}"

    # HealthResponse 필드 검사
    components = live.get("components", {}).get("schemas", {})
    health_schema = components.get(REQUIRED_SCHEMA)
    assert health_schema, "HealthResponse 스키마 누락"
    props = set(health_schema.get("properties", {}).keys())
    missing = REQUIRED_HEALTH_FIELDS - props
    assert not missing, f"HealthResponse 필드 누락: {missing}"

    # redis_connected 타입 검증 (boolean 혹은 nullable boolean)
    redis_prop = health_schema["properties"].get("redis_connected")
    assert redis_prop, "redis_connected 프로퍼티 없음"
    typ = redis_prop.get("type")
    # nullable boolean 은 anyOf/oneOf 로 표현될 수 있음
    assert (
        typ == "boolean" or
        "oneOf" in redis_prop or
        "anyOf" in redis_prop
    ), f"redis_connected 타입 비정상: {redis_prop}"

    # baseline 과 live 의 version 변화 허용 (문제 없음)
    # 추가: 핵심 경로 buy-limited operationId 존재
    buy_limited = live["paths"].get("/api/shop/buy-limited", {})
    get_def = buy_limited.get("post")
    assert get_def, "buy-limited POST 정의 누락"
    assert "operationId" in get_def, "buy-limited operationId 누락"
