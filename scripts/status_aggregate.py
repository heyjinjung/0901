import json
import re
from pathlib import Path
from collections import OrderedDict

STATUS_TOKENS = ["✅", "⚠️", "❌", "🚫"]

def aggregate(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    bullet_counts = {k: 0 for k in STATUS_TOKENS}
    inline_counts = {k: 0 for k in STATUS_TOKENS}  # 전체 파일(본문/헤더 포함) 등장 빈도
    other_bullet = 0

    sec_pattern = re.compile(r"^(#{2,3})\s+(.+)")
    # 허용: 선행 공백 + 목록 기호(- * +) + 공백 + 상태 이모지
    bullet_token_pattern = re.compile(r"^[ \t]*[-*+]\s*(✅|⚠️|❌|🚫)")

    current_section = None
    section_counts = OrderedDict()

    def ensure_section(sec: str):
        if not sec:
            return
        if sec not in section_counts:
            section_counts[sec] = {k: 0 for k in STATUS_TOKENS}
            section_counts[sec]["other"] = 0

    for line in lines:
        # 전체(라인 내) 토큰 등장 카운트
        for tok in STATUS_TOKENS:
            if tok in line:
                inline_counts[tok] += line.count(tok)

        m_sec = sec_pattern.match(line)
        if m_sec:
            level = len(m_sec.group(1))
            name = m_sec.group(2).strip()
            if level == 2:
                current_section = name
            elif level == 3:
                current_section = f"{current_section} > {name}" if current_section else name
            ensure_section(current_section)
            continue

        m_tok = bullet_token_pattern.match(line)
        if m_tok:
            tok = m_tok.group(1)
            if tok in bullet_counts:
                bullet_counts[tok] += 1
                if current_section:
                    ensure_section(current_section)
                    section_counts[current_section][tok] += 1
            else:
                other_bullet += 1
                if current_section:
                    ensure_section(current_section)
                    section_counts[current_section]["other"] += 1

    result = {
        "bullet_total": {
            "counts": bullet_counts,
            "other": other_bullet,
            "sum": sum(bullet_counts.values()) + other_bullet,
        },
        "inline_total": {
            "counts": inline_counts,
            "sum": sum(inline_counts.values()),
        },
        "sections": section_counts,
    }
    return result

def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("markdown", type=Path, help="Path to markdown doc (e.g. api docs/20250841-001.md)")
    ap.add_argument("--json", action="store_true", help="Output raw JSON only")
    args = ap.parse_args()
    res = aggregate(args.markdown)
    if args.json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return
    bullet = res["bullet_total"]["counts"]
    bullet_other = res["bullet_total"]["other"]
    inline = res["inline_total"]["counts"]
    print("=== BULLET TASK TOTAL (목록 항목 시작 위치) ===")
    for k in STATUS_TOKENS:
        print(f"{k}: {bullet[k]}")
    print(f"other: {bullet_other}")
    print(f"SUM: {res['bullet_total']['sum']}")
    print("\n=== FULL INLINE TOTAL (본문/헤더 포함 전체 출현 수) ===")
    for k in STATUS_TOKENS:
        print(f"{k}: {inline[k]}")
    print(f"SUM: {res['inline_total']['sum']}")
    print("\n=== SECTIONS (불릿 기준, non-zero) ===")
    for sec, sc in res["sections"].items():
        section_total = sum(sc[k] for k in STATUS_TOKENS) + sc["other"]
        if section_total == 0:
            continue
        line = ", ".join(f"{k}={sc[k]}" for k in STATUS_TOKENS if sc[k])
        if sc["other"]:
            if line:
                line += ", "
            line += f"other={sc['other']}"
        print(f"- {sec}: {line}")

if __name__ == "__main__":
    main()
