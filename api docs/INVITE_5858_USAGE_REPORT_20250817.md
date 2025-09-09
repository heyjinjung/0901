# INVITE 5858 사용량 리포트 (최근 30일)

생성일: 2025-08-17
분석 대상: invite_code = 5858
분석 기간: NOW() - 30일 ~ NOW()

## 1. 원본 일별 집계
| Day | Signups |
|-----|---------|
| 2025-08-15 | 1 |
| 2025-08-16 | 5 |

(빈 날짜=사용량 0)

수행 SQL:
```sql
SELECT date_trunc('day', created_at) AS day, invite_code, COUNT(*) signups
FROM users
WHERE invite_code='5858'
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY 1,2
ORDER BY 1;
```

## 2. 총합 및 비율
- 총 가입(5858): 6
- 전체 대비 비율 계산 필요(전체 users 대비) → 다음 쿼리 실행 권장:
```sql
SELECT
  SUM(CASE WHEN invite_code='5858' THEN 1 ELSE 0 END)::int AS signups_5858,
  COUNT(*)::int AS total_signups,
  ROUND(100.0*SUM(CASE WHEN invite_code='5858' THEN 1 ELSE 0 END)/COUNT(*),2) AS pct
FROM users
WHERE created_at >= NOW() - INTERVAL '30 days';
```

## 3. 리스크 평가 스냅샷
- 5858 집중도 임계(예: >60%) 여부: (전체 대비 쿼리 후 판단)
- 현재 데이터로는 30일 창 내 활동 낮음 → 회전 지연 허용 가능

## 4. 아카이빙
- 원본 CSV: `temp_invite_usage_5858.csv` (저장 필요 시 logs 또는 data_export 이동 권장)

## 5. 다음 액션 제안
1) 전체 대비 비율 쿼리 실행 후 문서 업데이트
2) Prometheus 지표(emitted_invite_signups_total{code="5858"}) 연동 시 동일 기간 그래프화
3) 회전 정책 유지 여부 분기 (현재: 영구 허용 정책 유지)
