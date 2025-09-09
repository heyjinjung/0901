# 2025-09-09 Alembic Revision 초안 (제약 정리 번들)

## 1. 목적
현재 DB 스키마 상 과도/불일치 UNIQUE 및 NULL 허용으로 인한 무결성/확장성/경제 로깅 위험을 단일 Revision 번들로 정리.

## 2. 영향 대상 테이블 및 변경 요약
| 테이블 | 현 구조 문제 | 변경 후 | 비고 |
|--------|--------------|---------|------|
| shop_transactions | user_id UNIQUE (추정), product_id UNIQUE (추정), (user_id, product_id, idempotency_key) 복합 UNIQUE 공존 | 개별 UNIQUE 제거, 복합(멱등)만 유지 | 중복 구매 허용 + 멱등 보장 |
| follow_relations | user_id UNIQUE, target_user_id UNIQUE, (user_id,target_user_id) 복합 UNIQUE | 단일 UNIQUE 제거, 복합만 유지 | 다:다 팔로우 허용 |
| event_mission_links | event_id UNIQUE, mission_template_id UNIQUE, (event_id, mission_template_id) 복합 UNIQUE | 단일 UNIQUE 제거, 복합만 유지 | 중복 제약 제거 |
| game_stats | user_id NULL 허용 | user_id NOT NULL | orphan 방지 |

## 3. 마이그레이션 단계 설계
1) 존재 검사 (inspector.get_indexes / get_unique_constraints / get_columns)
2) 조건부 제거(DROP CONSTRAINT/INDEX IF EXISTS)
3) ALTER TABLE ... SET NOT NULL (NULL 존재 시 선행 정제)
4) 트랜잭션 내 순차 적용 (PostgreSQL)

## 4. 사전 정제 쿼리 (예상)
```sql
-- game_stats NULL user_id 임시 보정 (만일 존재 시)
UPDATE game_stats SET user_id = 0 WHERE user_id IS NULL; -- 또는 해당 row 삭제/아카이브 전략 선택
```
(실사용 시 0 dummy user 미사용 권장 → orphan row 삭제 권고)

## 5. Upgrade 스니펫 (초안)
```python
from alembic import op
import sqlalchemy as sa

revision = '20250909_consolidate_constraints'
down_revision = 'f79d04ea1016'  # 현재 head (사용자 제공 기준)
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # shop_transactions 제약 정리
    if 'shop_transactions' in inspector.get_table_names():
        uniques = inspector.get_unique_constraints('shop_transactions')
        drop_names = [u['name'] for u in uniques if u['column_names'] in (['user_id'], ['product_id'])]
        for name in drop_names:
            op.drop_constraint(name, 'shop_transactions', type_='unique')

    # follow_relations
    if 'follow_relations' in inspector.get_table_names():
        uniques = inspector.get_unique_constraints('follow_relations')
        drop_names = [u['name'] for u in uniques if u['column_names'] in (['user_id'], ['target_user_id'])]
        for name in drop_names:
            op.drop_constraint(name, 'follow_relations', type_='unique')

    # event_mission_links
    if 'event_mission_links' in inspector.get_table_names():
        uniques = inspector.get_unique_constraints('event_mission_links')
        drop_names = [u['name'] for u in uniques if u['column_names'] in (['event_id'], ['mission_template_id'])]
        for name in drop_names:
            op.drop_constraint(name, 'event_mission_links', type_='unique')

    # game_stats user_id NOT NULL
    if 'game_stats' in inspector.get_table_names():
        cols = inspector.get_columns('game_stats')
        user_col = next((c for c in cols if c['name'] == 'user_id'), None)
        if user_col and user_col.get('nullable', True):
            # 데이터 정제 (NULL row 제거)
            conn.execute(sa.text("DELETE FROM game_stats WHERE user_id IS NULL"))
            op.alter_column('game_stats', 'user_id', existing_type=sa.Integer(), nullable=False)


def downgrade():
    # NOTE: 안전한 완전 복구 복잡 → 최소 rollback 로직만 제공
    op.alter_column('game_stats', 'user_id', existing_type=sa.Integer(), nullable=True)
    # 단일 UNIQUE 복구는 필요 시 수동 처리(로그 기록 권장)
```

## 6. 테스트 체크리스트
- 로컬 dev DB 백업 후 적용
- alembic upgrade head → heads 1개 유지
- 신규 구매 시 동일 product_id + 다른 idempotency_key 허용 확인
- follow_relations 다:다 삽입 성공
- event_mission_links 복합 dup 방지 정상
- game_stats insert 시 user_id NULL 실패 확인

## 7. 리스크 및 롤백 전략
| 리스크 | 완화 | 롤백 |
|--------|------|------|
| 기존 UNIQUE 삭제 후 의도치 않은 중복 폭증 | 애플리케이션 단 멱등키/비즈니스 검증 유지 | DB 백업 복원 |
| game_stats orphan row 존재 | 사전 DELETE 처리 | 백업 복원 |
| 다운그레이드 시 UNIQUE 구조 복구 미흡 | 문서에 downgrade 한계 명시 | 수동 재생성 |

## 8. 후속 문서화
- 개선안2.md DRIFT PATCH NOTE 하위 ‘DB 제약 정리’ 항목 추가(상세 적용 후)
- 0909.md P0/P1 로드맵 항목 상태 업데이트(‘제약 정리 → 적용됨’)

(끝)
