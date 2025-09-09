# DB FK/제약조건 순서 및 의존성 그래프 (전체 테이블)

> 본 문서는 Casino-Club F2P 프로젝트의 전체 데이터베이스 테이블, FK(외래키), 제약조건(UNIQUE, CHECK 등) 및 생성/삭제/마이그레이션 시 의존성 순서를 명확히 정리합니다.
> 
> 목적: 마이그레이션 충돌, 롤백 장애, 배포 오류, 데이터 무결성 문제 예방

---

## 1. 전체 테이블/관계 목록

- users
- user_segments
- user_actions
- user_rewards
- gacha_log
- shop_transactions
- battlepass_status
- vip_access_log
- notifications
- admin_user_activity
- admin_reward
- 기타(필요시 확장)

---

## 2. FK/제약조건 의존성 트리 (텍스트)

- users
  - user_segments (user_id → users.id, ON DELETE CASCADE)
  - user_actions (user_id → users.id, ON DELETE CASCADE)
  - user_rewards (user_id → users.id, ON DELETE CASCADE)
  - gacha_log (user_id → users.id, ON DELETE CASCADE)
  - shop_transactions (user_id → users.id, ON DELETE CASCADE)
  - battlepass_status (user_id → users.id, ON DELETE CASCADE)
  - vip_access_log (user_id → users.id, ON DELETE SET NULL)
  - notifications (user_id → users.id, ON DELETE CASCADE)
  - admin_user_activity (user_id → users.id, ON DELETE SET NULL)
  - admin_reward (user_id → users.id, ON DELETE SET NULL)

- shop_transactions
  - user_rewards (shop_tx_id → shop_transactions.id, ON DELETE SET NULL)

- 기타 FK/제약조건
  - user_segments: UNIQUE(user_id)
  - user_actions: CHECK(action_type IN ...)
  - user_rewards: CHECK(reward_type IN ...)
  - gacha_log: CHECK(rarity IN ...)
  - battlepass_status: UNIQUE(user_id)
  - notifications: CHECK(type IN ...)
  - admin_user_activity: CHECK(activity_type IN ...)
  - admin_reward: CHECK(reward_type IN ...)

---

## 3. FK/제약조건 생성/삭제 순서 (마이그레이션/롤백 시)

1. 테이블 생성 순서 (의존성 적은 것 → 많은 것)
   - users
   - user_segments, battlepass_status
   - user_actions, user_rewards, gacha_log, shop_transactions, vip_access_log, notifications, admin_user_activity, admin_reward

2. FK/제약조건 생성 순서
   - 테이블 생성 후 FK/UNIQUE/CHECK 등 제약조건 추가
   - 복합 FK/SET NULL 등은 반드시 참조 대상 테이블이 먼저 생성되어야 함

3. 삭제/롤백 시 역순 적용
   - FK/제약조건 → 테이블(의존성 많은 것부터 삭제)

---

## 4. Graphviz 의존성 그래프 (예시)

```dot
// 전체 DB FK/제약조건 의존성 그래프


  users -> user_segments
  users -> user_actions
  users -> user_rewards
  users -> gacha_log
  users -> shop_transactions
  users -> battlepass_status
  users -> vip_access_log
  users -> notifications
  users -> admin_user_activity
  users -> admin_reward
  shop_transactions -> user_rewards
}
```

---

## 5. 관리/확장 가이드
- 신규 테이블/관계 추가 시 본 문서에 반드시 반영
- Alembic 마이그레이션 작성 시 본 순서/의존성 참고
- FK/제약조건 충돌, 롤백 장애 발생 시 본 문서 우선 점검
- 실제 DB 스키마와 불일치 시 즉시 업데이트

---

> 최신화: 2025-07-29, 전체 테이블/관계 기준, 누락/오류 발견 시 즉시 수정 요망
