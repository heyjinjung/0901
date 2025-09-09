# Game Stats Details 확장 스키마 초안 (2025-09-09)

## 1. 목적
승/패/최대이익 등 파생 필드를 Normalizer 단순 aggregate 외 세부 breakdown 형태로 재도입하여:
- UI: 게임별 성과 뱃지/차트 렌더링
- 추천/세그먼트: 고위험/고빈도 패턴 분석
- Rollup summary (향후) 기반 Materialized Aggregation 사전 검증

## 2. 스키마 개요
```jsonc
{
  "success": true,
  "stats": {
    "aggregate": {
      "total_games_played": 1234,
      "total_wins": 678,
      "total_losses": 556,
      "win_rate": 0.549,
      "overall_max_win": 9500
    },
    "details": {
      "crash": { "wins": 120, "losses": 100, "max_win": 2400, "total": 220 },
      "slot":  { "wins": 300, "losses": 280, "max_win": 5000, "total": 580 },
      "gacha": { "wins": 180, "losses": 150, "max_win": 1400, "total": 330 },
      "rps":   { "wins": 78,  "losses": 26,  "max_win": 700,  "total": 104 }
    },
    "last_updated": "2025-09-09T12:34:56Z"
  }
}
```

## 3. 파생 규칙
- win_rate = round(total_wins / max(1,total_games_played), 3)
- overall_max_win = max(details.*.max_win)
- details.*.total = details.*.wins + details.*.losses
- aggregate.total_games_played = sum(details.*.total)
- 일관성 검증: sum(details.*.wins) == aggregate.total_wins (불일치 시 서버 재계산 경고 로깅)

## 4. 백엔드 구현 가이드
- 소스: service layer (GameStatsService.aggregate_user_stats)
- 데이터 원천: game_stats 누적 테이블(없으면 on-the-fly group by)
- 누락 게임 타입 처리: 존재하지 않으면 {wins:0,losses:0,max_win:0,total:0}
- 캐시 키: cache:game_stats:user:{id}:v2 (TTL 5s, 파생 포함)
- 버전 필드(stats_version=2) 헤더 or response root optional 추가 → 클라이언트 마이그레이션 안전화

## 5. 마이그레이션 영향
- DB 구조 변경 불필수(파생 계산은 쿼리/코드 레벨). 단, 성능 향상을 위해 P2에서 summary 테이블 도입 예정.

## 6. 테스트 전략
| 구분 | 케이스 | 검증 포인트 |
|------|--------|-------------|
| Happy | 다수 게임 혼합 | aggregate vs details 합 일치 |
| Zero  | 모든 값 0 | division by zero 방지, win_rate=0 |
| Partial | 특정 게임 없음 | 누락 게임 0 필드 삽입 |
| MaxWin | 단일 게임 최대 | overall_max_win 일치 |
| Drift | aggregate != sum(details) | 서버 경고 로그 + self-heal 재계산 |

### Pytest 예시 스냅샷 (초안)
```python
payload = client.get('/api/games/stats/me').json()
assert payload['stats']['aggregate']['total_wins'] == \
    sum(v['wins'] for v in payload['stats']['details'].values())
```

## 7. 성능/캐시 고려
- TTL 5s: 실시간성 vs 부하 균형.
- 캐시 미스율 모니터링 (Prometheus counter: game_stats_cache_miss_total).

## 8. 출시 절차(Rollout)
1) 서버 구현 + feature flag(stats_details_v2) 기본 off
2) 내부 QA 활성화 → E2E 스냅샷 추가
3) 프로덕션 점진적 10% 트래픽 활성 → 오류 없음 확인
4) flag 제거 & 0909.md 19.2 상태 '미해결→확정' 업데이트

## 9. 향후 확장
- streak 연관 보정(연승 longest_win_streak)
- 손실 변동성 지표(variance) 도입
- user_segments 업데이트 트리거 (고위험군 탐지)
