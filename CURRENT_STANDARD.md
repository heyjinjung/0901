# CURRENT STANDARD (Canonical Reference)

> Scope: Single source of truth for architecture, security/auth, migrations, onboarding/data-driven ops, purchase/security, and game stats/metrics. Links point to CORE/GREEN docs verified on 2025-09-09.

## 1) 시스템 아키텍처
- System overview: docs/SYSTEM_ARCHITECTURE.md
- Architecture summary: docs/SYSTEM_ARCHITECTURE_SUMMARY.md
- Frontend structure progress: docs/FRONTEND_STRUCTURE_PROGRESS.md

## 2) 보안/인증
- STATUS_PURCHASE_SECURITY.md (purchase security baseline)
- docs/18_security_authentication_en.md (auth/security overview)
- cc-webapp/backend/app/auth/README.md (backend auth notes)

API canonical mapping: see “API mapping (authoritative)” below.

## 3) 마이그레이션
- alembic_revision_plan_20250909.md (constraints cleanup, NOT NULL, rollups)
- docs/DB_INDEX_AUDIT.md (index audit) and docs/DATABASE_BACKUP_RESTORE.md

## 4) 온보딩/데이터 드리븐 운영
- 2025-09-06_온보딩_운영_누적학습_요약.md (current operations snapshot)
- docs/2025010.data_driven_onboarding_ops_checklist.md

## 5) 구매/보안
- STATUS_PURCHASE_SECURITY.md (idempotency, integrity hash/signature)
- 0909.md (sections 16 Settlement / purchase unification; serves as background; use this doc as the up-to-date canonical umbrella)

## 6) 게임 통계/지표
- 2025-09-09_게임통계_풀스택동기화_완성.md (overall_max_win, win_rate, normalizer)
- stats_details_schema.md (keys, normalization spec)

---
## API mapping (authoritative)
This section aligns to the latest OpenAPI spec (see openapi_spec.json). Prefer these endpoints over any legacy mentions.

- Auth:
  - POST /auth/register
  - POST /auth/login
  - POST /auth/refresh
  - POST /auth/logout
  - GET  /auth/profile
  - GET  /auth/sessions

- Users:
  - GET  /api/users/profile
  - PUT  /api/users/profile
  - GET  /api/users/balance
  - GET  /api/users/info
  - GET  /api/users/stats
  - POST /api/users/tokens/add
  - GET  /api/users/{user_id}

- Admin:
  - GET  /api/admin/stats
  - POST /api/admin/users/{user_id}/ban
  - POST /api/admin/users/{user_id}/unban
  - POST /api/admin/users/{user_id}/tokens/add

- Games:
  - GET  /api/games/
  - POST /api/games/slot/spin
  - POST /api/games/gacha/pull
  - POST /api/games/crash/bet
  - POST /api/games/rps/play

- Rewards & Missions/Events:
  - GET  /api/rewards/users/{user_id}/rewards
  - POST /api/rewards/distribute
  - GET  /api/missions/
  - POST /api/missions/{mission_id}/claim
  - GET  /api/events/
  - GET  /api/events/{event_id}
  - POST /api/events/join
  - PUT  /api/events/progress/{event_id}
  - POST /api/events/claim/{event_id}
  - GET  /api/events/missions/daily
  - GET  /api/events/missions/weekly
  - GET  /api/events/missions/all
  - PUT  /api/events/missions/progress
  - POST /api/events/missions/claim/{mission_id}

- Shop:
  - POST /api/shop/purchase

- Invite:
  - POST /api/invite/generate
  - POST /api/invite/validate
  - GET  /api/invite/codes
  - PATCH /api/invite/codes/{code}/deactivate
  - GET  /api/invite/stats

- Analytics & Dashboard:
  - GET  /api/analytics/dashboard/summary
  - GET  /api/analytics/users/activity
  - GET  /api/analytics/games/stats
  - GET  /dashboard/main
  - GET  /dashboard/games
  - GET  /dashboard/social-proof

---
Notes
- Legacy docs with “초안/임시/TODO” are archived or referenced for history only. Use this document as the top landing index.
- When OpenAPI changes, refresh this section and update API_MAPPING_UPDATED.md in lockstep.
