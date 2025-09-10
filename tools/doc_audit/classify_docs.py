"""Document Classification Utility

분류 목적:
 - 레거시/혼합/현재 표준 문서 자동 탐지로 Canonical Spec 구축 지원

분류 상태(기존 + 확장):
 - RED    (LEGACY): 현재 구현과 충돌/폐기
 - YELLOW (MIXED): 혼재/부분 최신
 - GREEN  (CURRENT): 최신 표준 후보
 - CORE   (CANONICAL CANDIDATE): 핵심 시스템 표준으로 승격될 가능성이 높은 문서 (core 목록/점수 기준)

판단 규칙(우선순위 상위 → 하위 평가; 최초 매칭 강한 신호):
 1) 파일 경로/디렉토리 기반:
    - archive/, legacy/, tests/legacy → RED 강제
    - 0909, 2025-09, 최근 날짜 패턴 포함 & drift 분석/요약 → YELLOW 기본
 2) 키워드 기반 (정규식 대소문자 무시):
    - RED 신호 키워드 (누적 2개 이상 → RED):
        ["/api/shop/buy", "0일차 스트릭", "deprecated", "(legacy)", "다중 purchase 엔드포인트", "old_stats_format"]
    - YELLOW 신호 키워드 (GREEN으로 만들기 위해 제거/정규화 필요):
        ["임시", "TODO", "미검증", "중복", "정리 필요", "초안", "draft"]
    - GREEN 강화 키워드 (표준 선언):
        ["Unified Purchase", "Idempotency", "Streak 보상", "normalized", "overall_max_win", "win_rate"]
 3) 최신성 휴리스틱:
    - 최근 15일 내 수정된 파일(옵션, 파일 시스템 mtime 사용) & GREEN 키워드 ≥2 & RED 키워드=0 → GREEN 승격 후보
 4) 강등 규칙:
    - GREEN 조건 충족했더라도 RED 키워드 ≥1 + YELLOW ≥2 → YELLOW로 강등

추가 기능:
    - 파일명 날짜 패턴(YYYY-MM-DD / YYYYMMDD / YYYY-MM / YYYY) 추출 → 최근 days/extended-days 기준 가중치
    - OpenAPI drift 감지(--openapi-current / --openapi-prev 제공 시 해시 비교) → drift=True 이면 spec 관련 문서(api docs/, OpenAPI, API_MAPPING 등) YELLOW 최소 강등

출력:
    - JSON: tools/doc_audit/report.json (drift_meta 포함)
    - Markdown 요약: tools/doc_audit/report_summary.md (헤더에 drift 여부 표기)

사용 방법 (repo 루트에서):
  python tools/doc_audit/classify_docs.py --root . --days 15

추가 예정(후속 P1):
  - OpenAPI 스키마 hash 비교 후 drift 문서 자동 YELLOW 표시
  - Streak/Level 공식 값 변경 diff 검출
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
try:  # pyyaml 필요 (없으면 core 파일 설정 생략)
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any


RED_KEYWORDS = [
    r"/api/shop/buy",
    r"0일차[ ]?스트릭",
    r"deprecated",
    r"\(legacy\)",
    r"다중 purchase 엔드포인트",
    r"old_stats_format",
]

YELLOW_KEYWORDS = [
    r"임시",
    r"TODO",
    r"미검증",
    r"중복",
    r"정리 필요",
    r"초안",
    r"draft",
]

GREEN_KEYWORDS = [
    r"Unified Purchase",
    r"Idempotency",
    r"Streak 보상",
    r"normalized",
    r"overall_max_win",
    r"win_rate",
]

ARCHIVE_DIR_MARKERS = ["archive", "legacy"]

# 날짜 패턴 정규식 (우선순위 높은 포맷 우선 검사)
DATE_PATTERNS = [
    re.compile(r"(?P<full>20[0-9]{2}[-_](0[1-9]|1[0-2])[-_](0[1-9]|[12][0-9]|3[01]))"),  # YYYY-MM-DD
    re.compile(r"(?P<short>20[0-9]{2}(0[1-9]|1[0-2])(0[1-9]|[12][0-9]|3[01]))"),          # YYYYMMDD
    re.compile(r"(?P<ym>20[0-9]{2}[-_](0[1-9]|1[0-2]))"),                                  # YYYY-MM
    re.compile(r"(?P<y>20[0-9]{2})"),                                                       # YYYY
]


@dataclass
class DocRecord:
    path: str
    status: str
    red_hits: List[str]
    yellow_hits: List[str]
    green_hits: List[str]
    reasons: List[str]
    suggestions: List[str]
    mtime: str
    date_inferred: str | None
    openapi_related: bool
    score: int
    core_hint: bool
    foundation_hint: bool


@dataclass
class DriftMeta:
    openapi_drift: bool = False
    current_hash: str | None = None
    prev_hash: str | None = None


def scan_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:  # pragma: no cover
        return f""  # treat unreadable as empty


def regex_hits(patterns: List[str], text: str) -> List[str]:
    hits = []
    for p in patterns:
        if re.search(p, text, flags=re.IGNORECASE):
            hits.append(p)
    return hits


def infer_date_from_name(name: str) -> datetime | None:
    """파일명에서 날짜 후보 추출.
    가장 구체적인(YYYY-MM-DD) → YYYYMMDD → YYYY-MM → YYYY 순으로 반환.
    """
    for pattern in DATE_PATTERNS:
        m = pattern.search(name)
        if not m:
            continue
        g = m.groupdict()
        val = next((v for v in g.values() if v), None)
        if not val:
            continue
        try:
            if len(val) == 10 and val.count("-") == 2:  # YYYY-MM-DD
                return datetime.strptime(val, "%Y-%m-%d")
            if len(val) == 8 and val.isdigit():  # YYYYMMDD
                return datetime.strptime(val, "%Y%m%d")
            if len(val) == 7 and val.count("-") == 1:  # YYYY-MM
                return datetime.strptime(val, "%Y-%m")
            if len(val) == 4 and val.isdigit():  # YYYY
                return datetime.strptime(val, "%Y")
        except ValueError:  # pragma: no cover
            continue
    return None


def classify(path: Path, text: str, recent_threshold: datetime, *, openapi_related: bool, drift: bool, core_names: set[str]) -> DocRecord:
    rel = str(path).replace("\\", "/")
    red = regex_hits(RED_KEYWORDS, text)
    yellow = regex_hits(YELLOW_KEYWORDS, text)
    green = regex_hits(GREEN_KEYWORDS, text)
    reasons: List[str] = []
    suggestions: List[str] = []
    status = "YELLOW"  # default neutral (초기)
    score = 0

    name_lower = path.name.lower()
    core_hint = False
    foundation_hint = False
    # core 후보: 파일명 기반 + 설정 기반
    if path.name in core_names or any(k in name_lower for k in ["unified", "architecture", "purchase", "stats", "streak", "level", "realtime", "security", "migration", "onboarding"]):
        core_hint = True
        score += 5

    # Foundation hint: 2025-08-01 이전 + 파일명에 readme/architecture/overview/base/core 등 포함
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
    except Exception:  # pragma: no cover
        mtime = datetime.now()
    cutoff_foundation = datetime(2025, 8, 1)
    if mtime < cutoff_foundation and any(k in name_lower for k in ["readme", "architecture", "overview", "base", "core", "foundation"]):
        foundation_hint = True
        score += 4
        reasons.append("초기 토대(8월 이전 + README/ARCHITECTURE 계열)")

    # Archive enforcement
    lowered = rel.lower()
    if any(m in lowered for m in ARCHIVE_DIR_MARKERS):
        status = "RED"
        reasons.append("archive/legacy 경로")
        score -= 6

    # Strong red rule
    if len(red) >= 1:
        status = "RED"
        reasons.append(f"RED 키워드 {len(red)}개 탐지")
        score -= 3 * len(red)

    # Promote to GREEN candidate
    # mtime 이미 확보됨 (foundation 판단에서 사용)
    is_recent = mtime >= recent_threshold

    # 파일명 날짜 기반 추가 가중치 (최근 45일 내 or days*3 내)
    inferred_dt = infer_date_from_name(path.name)
    inferred_recency = False
    if inferred_dt:
        # 45일 이내면 최근으로 간주
        if inferred_dt >= datetime.now() - timedelta(days=45):
            inferred_recency = True
            reasons.append("파일명 날짜 최근(≤45d)")

    if status != "RED":
        recency_boost = (is_recent or inferred_recency)
        if recency_boost and len(green) >= 2 and len(red) == 0:
            status = "GREEN"
            reasons.append("최근/추론 날짜 + GREEN 키워드 ≥2 + RED=0")
            score += 4
        else:
            # Mixed heuristic
            if len(yellow) and len(green):
                status = "YELLOW"
                reasons.append("GREEN & YELLOW 혼재")
                score += len(green) * 2 - len(yellow)
            elif len(green) >= 3 and len(red) == 0 and len(yellow) <= 1:
                status = "GREEN"
                reasons.append("GREEN ≥3 & 불순물 적음")
                score += 5
            elif len(yellow) > 0 and status != "GREEN":
                status = "YELLOW"
                reasons.append("YELLOW 키워드 존재")
                score -= len(yellow)
            else:
                score += len(green) * 2

    # Demote rule
    if status == "GREEN" and (len(red) >= 1 or len(yellow) >= 2):
        status = "YELLOW"
        reasons.append("GREEN 조건 충족 후 강등: RED>=1 또는 YELLOW>=2")
        score -= 2

    # OpenAPI drift 영향: spec 관련 문서는 drift 발생 시 최소 YELLOW 강등
    if drift and openapi_related and status == "GREEN":
        status = "YELLOW"
        reasons.append("OpenAPI drift 감지 → GREEN 강등")
        score -= 2
    elif drift and openapi_related and status == "YELLOW":
        reasons.append("OpenAPI drift 감지")
        score -= 1
    elif drift and openapi_related and status == "RED":
        reasons.append("OpenAPI drift + RED")
        score -= 1

    # GREEN/CORE 승격 판단 (최종 점수 기반 재조정)
    # 기본 점수 조정: GREEN 최소 점수 4, CORE 최소 점수 9 (core_hint 필요)
    if status not in ("RED",):
        if core_hint and score >= 9 and len(red) == 0:
            status = "CORE"
            reasons.append("점수 기반 CORE 승격")
        elif score >= 4 and status == "YELLOW" and len(red) == 0:
            status = "GREEN"
            reasons.append("점수 기준 GREEN 승격")

    # Suggestions
    if status == "RED":
        suggestions.append("HISTORY 또는 legacy_specs 디렉토리로 이동 고려")
        if red:
            suggestions.append("레거시 엔드포인트/공식 업데이트")
    elif status == "YELLOW":
        suggestions.append("혼재 섹션 정리 및 최신 표준 반영 필요")
    elif status == "CORE":
        suggestions.append("Canonical 표준으로 CURRENT_STANDARD.md 통합 권장 (변경 시 Change Control)")
    else:
        suggestions.append("Canonical 후보 - CURRENT_STANDARD.md 병합 검토")

    return DocRecord(
        path=rel,
        status=status,
        red_hits=red,
        yellow_hits=yellow,
        green_hits=green,
        reasons=reasons,
        suggestions=suggestions,
        mtime=mtime.isoformat(timespec="seconds"),
        date_inferred=inferred_dt.isoformat() if inferred_dt else None,
    openapi_related=openapi_related,
    score=score,
    core_hint=core_hint,
    foundation_hint=foundation_hint,
    )


def generate_markdown(records: List[DocRecord], drift_meta: DriftMeta) -> str:
    header = (
        "# 문서 자동 분류 리포트\n\n"
        f"- OpenAPI Drift: {'YES' if drift_meta.openapi_drift else 'NO'}\n"
        f"- current_hash: {drift_meta.current_hash or '-'} / prev_hash: {drift_meta.prev_hash or '-'}\n\n"
    "| 경로 | 상태 | 점수 | RED | YEL | GRN | CORE | FOUND | 날짜추론 | OpenAPI | 주요 사유 | 제안 | 수정시각 |\n"
    "|------|------|-----|-----|-----|-----|------|-------|----------|---------|----------|------|---------|\n"
    )
    lines = [header]
    for r in records:
        lines.append(
            f"| {r.path} | {r.status} | {r.score} | {len(r.red_hits)} | {len(r.yellow_hits)} | {len(r.green_hits)} | {'Y' if r.core_hint else ''} | {'Y' if r.foundation_hint else ''} | "
            f"{r.date_inferred or '-'} | {'Y' if r.openapi_related else ''} | {' ; '.join(r.reasons) or '-'} | {('; '.join(r.suggestions))} | {r.mtime} |\n"
        )
    # Summary section
    total = len(records)
    red_cnt = sum(1 for r in records if r.status == "RED")
    yellow_cnt = sum(1 for r in records if r.status == "YELLOW")
    green_cnt = sum(1 for r in records if r.status == "GREEN")
    core_cnt = sum(1 for r in records if r.status == "CORE")
    summary = (
        f"\n## 요약\n\n총 {total}개 파일: CORE {core_cnt}, GREEN {green_cnt}, YELLOW {yellow_cnt}, RED {red_cnt}.\n"
        "- RED: 레거시/충돌 요소 다수 → 제거/분리 우선\n"
        "- YELLOW: 혼합/부분 최신 → 편집/정리 대상\n"
        "- GREEN: Canonical 후보 (정리 후 CORE 승격 가능)\n"
        "- CORE: 즉시 CURRENT_STANDARD 편입 고려\n"
    )
    lines.append(summary)
    return "".join(lines)


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="문서 레거시 자동 분류")
    parser.add_argument("--root", default=".", help="검색 시작 루트")
    parser.add_argument("--days", type=int, default=15, help="최근 수정판정 일수")
    parser.add_argument("--output-json", default="tools/doc_audit/report.json")
    parser.add_argument("--output-md", default="tools/doc_audit/report_summary.md")
    parser.add_argument("--openapi-current", help="현재 OpenAPI 스펙 파일 경로 (hash 비교)")
    parser.add_argument("--openapi-prev", help="이전 OpenAPI 스펙 파일 경로 (hash 비교)")
    parser.add_argument("--core-config", default="tools/doc_audit/core_files.yml", help="핵심 문서 파일명(yaml list)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    recent_threshold = datetime.now() - timedelta(days=args.days)

    md_files: List[Path] = [
        p for p in root.rglob("*.md") if "/.venv/" not in str(p).replace("\\", "/")
    ]

    drift_meta = DriftMeta()
    if args.openapi_current and args.openapi_prev:
        def file_hash(p: str) -> str:
            import hashlib
            data = Path(p).read_bytes()
            return hashlib.sha256(data).hexdigest()
        if Path(args.openapi_current).is_file() and Path(args.openapi_prev).is_file():
            drift_meta.current_hash = file_hash(args.openapi_current)
            drift_meta.prev_hash = file_hash(args.openapi_prev)
            if drift_meta.current_hash != drift_meta.prev_hash:
                drift_meta.openapi_drift = True

    core_names: set[str] = set()
    if yaml and Path(args.core_config).is_file():
        try:
            data = yaml.safe_load(Path(args.core_config).read_text(encoding="utf-8")) or []
            if isinstance(data, list):
                core_names = {str(x).strip() for x in data if x}
        except Exception:  # pragma: no cover
            pass

    records: List[DocRecord] = []
    for p in md_files:
        text = scan_file(p)
        rel_lower = str(p).replace("\\", "/").lower()
        openapi_related = any(x in rel_lower for x in ["api docs", "api_mapping", "openapi", "api_specification", "router", "endpoints"])  # heuristic
        rec = classify(p, text, recent_threshold, openapi_related=openapi_related, drift=drift_meta.openapi_drift, core_names=core_names)
        records.append(rec)

    records.sort(key=lambda r: (r.status, r.path))

    # Ensure output directory
    Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output_json, "w", encoding="utf-8") as jf:
        payload: Dict[str, Any] = {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "drift_meta": asdict(drift_meta),
            "records": [asdict(r) for r in records],
        }
        json.dump(payload, jf, ensure_ascii=False, indent=2)

    md = generate_markdown(records, drift_meta)
    with open(args.output_md, "w", encoding="utf-8") as mf:
        mf.write(md)

    print(f"생성 완료: {args.output_json}, {args.output_md}")
    print("GREEN 후보 수:", sum(1 for r in records if r.status == "GREEN"))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
