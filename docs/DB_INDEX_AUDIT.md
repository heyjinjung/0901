# DB Index & Constraint Audit (Initial Pass)

Goal: Ensure critical query patterns have supporting indexes before MVP launch. This is a static audit snapshot; implement migrations separately after confirming with slow query logs / EXPLAIN.

## 1. Key Access Patterns (Assumed)
| Pattern | Tables | Recommended Strategy |
|---------|--------|----------------------|
| Fetch recent game sessions per user | game_sessions (Game?) | INDEX(user_id, created_at DESC) |
| Fetch purchase history per user | shop_purchases / transactions | INDEX(user_id, created_at DESC) |
| Reward claims lookup | rewards / reward_claims | INDEX(user_id, reward_id) or UNIQUE(user_id, reward_id) if one-claim policy |
| Notification delivery filtering | notifications, notification_targets | INDEX(user_id, is_read, created_at) partial on (is_read=false) |
| Mission progress per user | mission_progress | INDEX(user_id, mission_id) UNIQUE(user_id, mission_id) |
| Chat messages recent per room | chat_messages | INDEX(room_id, created_at DESC) + INDEX(user_id, created_at) |
| Analytics aggregation by day/user | analytics_events | INDEX(event_date, user_id) |

## 2. Existing Observations (Sampling)
- Many models already include `user_id` with `index=True`.
- Composite multi-column indexes largely absent (need to verify migrations). Single-column `user_id` may not cover ORDER BY created_at queries efficiently.
- Some uniqueness enforced at app logic only (e.g. potential multiple reward claims).

## 3. Proposed New Indexes / Constraints
| Table | New Index / Constraint | Rationale | Priority |
|-------|------------------------|-----------|----------|
| game_sessions | IX_game_sessions_user_created (`user_id`, `created_at`) | Pagination by newest per user | HIGH |
| shop_purchases (or equivalent) | IX_shop_purchases_user_created (`user_id`, `created_at`) | Recent purchase history | HIGH |
| reward_claims | UQ_reward_claims_user_reward (`user_id`, `reward_id`) | Prevent duplicate claim | HIGH |
| mission_progress | UQ_mission_progress_user_mission (`user_id`, `mission_id`) | One row per mission per user | HIGH |
| notifications | IX_notifications_user_unread (`user_id`, `is_read`, `created_at`) WHERE is_read = false | Fast unread list | MEDIUM |
| chat_messages | IX_chat_messages_room_created (`room_id`, `created_at`) | Room timeline retrieval | MEDIUM |
| chat_messages | IX_chat_messages_user_created (`user_id`, `created_at`) | User moderation/audit | LOW |
| analytics_events | IX_analytics_events_date_user (`event_date`, `user_id`) | Daily cohort aggregations | MEDIUM |

## 4. Constraints Integrity
| Need | Strategy |
|------|----------|
| Enforce single active invite code per user? | UNIQUE(user_id) if business rule | TBD |
| Prevent negative balances | CHECK(balance >= 0) | Already? verify |
| Ensure enum textual status correctness | Use CHECK(status IN (...)) or Enum type | Partial |

## 5. Migration Plan (Draft)
1. Confirm table exact names in Alembic models.
2. Create single migration adding composite indexes & uniqueness.
3. Use `CONCURRENTLY` for large tables (Postgres only) (optional if small pre-launch).
4. Test with `EXPLAIN ANALYZE` before & after for a heavy query.

## 6. Validation Checklist
- [ ] Identify actual slow queries (enable `log_min_duration_statement=200ms`).
- [ ] Confirm row counts (< 1M may defer some medium priority indexes).
- [ ] Ensure uniqueness additions have no duplicates (pre-check query). 
- [ ] Add down-revision safe drops.

## 7. Next Steps
- Gather production-like workload sample.
- Revisit after 1 week of telemetry.

---
This file is a living document; update after confirming real query patterns.
