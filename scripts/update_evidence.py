#!/usr/bin/env python3
"""Update 0909.md 19.2 evidence table with commit hash and line references (UTF-8 safe).

Usage:
  python scripts/update_evidence.py --doc 0909.md
"""
import argparse
import pathlib
import subprocess
import sys

CLAIMS = [
    "overall_max_win / win_rate 구현 완료",
    "Unified Purchase 표준화",
    "DB 제약 정리 필요 (shop_tx/follow/event_link/game_stats)",
    "이벤트 리워드 플로우 미검증",
    "승/패 파생 JSON 세부 통계 재도입",
    "E2E 실패 3건 (Admin Guard/Auth Migration/Daily Reward)",
    "Streak/XP 공식 단일화",
    "Idempotency Unique Key 단일화",
    "Follow/Relation/Event 링크 제약 축소",
    "game_stats.user_id NOT NULL 필요",
]

FILE_MAP = {
    CLAIMS[0]: "2025-09-09_게임통계_풀스택동기화_완성.md",
    CLAIMS[1]: "api docs/20250808.md",
    CLAIMS[2]: "0909데이터베이스.md",
    CLAIMS[3]: "2025-09-06_온보딩_운영_누적학습_요약.md",
    CLAIMS[4]: "2025-09-09_게임통계_풀스택동기화_완성.md",
    CLAIMS[5]: "E2E_failed_tests_20250909.md",
    CLAIMS[6]: "2025-09-06_온보딩_운영_누적학습_요약.md",
    CLAIMS[7]: "0909데이터베이스.md",
    CLAIMS[8]: "0909데이터베이스.md",
    CLAIMS[9]: "0909데이터베이스.md",
}

def last_commit(path: str) -> str:
    try:
        out = subprocess.check_output(["git","log","-1","--pretty=format:%h","--", path], stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except subprocess.CalledProcessError:
        return ""

def find_line_numbers(doc_text: str):
    line_map = {}
    lines = doc_text.splitlines()
    for i,l in enumerate(lines, start=1):
        for c in CLAIMS:
            # match start of table row with claim snippet
            if l.startswith("| "+c+" |"):
                line_map[c] = i
    return line_map

def update_table(doc_path: pathlib.Path):
    text = doc_path.read_text(encoding='utf-8')
    # locate 19.2 table header
    if "### 19.2 변경 근거 매핑 테이블" not in text:
        print("19.2 table not found", file=sys.stderr)
        return 1
    line_map = find_line_numbers(text)
    new_lines = []
    for line in text.splitlines():
        if line.startswith("| "):
            for claim in CLAIMS:
                if line.startswith(f"| {claim} |"):
                    commit = last_commit(FILE_MAP.get(claim, "")) or "(n/a)"
                    # replace Commit / LineRef columns (3rd & 4th)
                    parts = [p.strip() for p in line.split('|')][1:-1]
                    if len(parts) >= 6:
                        # columns: 주장/결정, 근거, Commit, LineRef, 상태, 비고
                        parts[2] = commit
                        parts[3] = f"L{line_map.get(claim,'?')}"
                        line = "| " + " | ".join(parts) + " |"
                    break
        new_lines.append(line)
    doc_path.write_text("\n".join(new_lines)+"\n", encoding='utf-8')
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--doc', default='0909.md')
    args = ap.parse_args()
    p = pathlib.Path(args.doc)
    if not p.exists():
        print("doc not found", file=sys.stderr)
        return 1
    rc = update_table(p)
    if rc == 0:
        print("Evidence table updated.")
    return rc

if __name__ == '__main__':
    raise SystemExit(main())
