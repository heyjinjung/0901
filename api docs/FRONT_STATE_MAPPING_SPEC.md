# Frontend Global State Mapping Spec (Phase A Foundation)

문서 버전: 2025-08-21
관련 백엔드 변경: 통합 /api/dashboard, 이벤트 progress_version & last_progress_at, 표준화된 이벤트 claim 응답(reward_items[])

## 1. 목적
프론트엔드 전역 상태 구조(스토어/캐시/쿼리 키)를 Phase A 범위에서 명확히 정의하여:
- 중복 fetch 감소 (통합 dashboard 활용)
- 이벤트/미션/보상 진행도 클라이언트 캐싱 일관성 확보 (progress_version 기반 무효화)
- 향후 Kafka 실시간 갱신(Stream 또는 SSE) 적용 시 최소 변경으로 확장 가능하도록 key 규칙 표준화

## 2. 설계 원칙
1. 단일 책임: 각 slice 는 하나의 bounded context (auth, dashboard, progress, economy 등) 관리
2. 낙관/비관 혼합: write 직후 progress_version 선반영 → 실패 시 rollback
3. 멱등/버전: progress_version + last_progress_at 조합으로 서버 우선 정합성 유지
4. 캐시 키 규약: `<domain>:<entity>:<id|variant>` / 목록은 `list` or 필터 사양 추가
5. 소비 계층: 서버 상태(Server Cache) ↔ 파생 UI 상태(View) 명확 분리

## 3. 상위 구조 개요
```
rootState
  auth: AuthState
  user: UserProfileState
  dashboard: DashboardAggregateState
  progress: ProgressState
    events: EventProgressSlice
    missions: MissionProgressSlice
  rewards: RewardState
  shop: ShopState
  game: GameRuntimeState
  economy: EconomyState
  system: SystemMetaState
```

## 4. Slice 상세
### 4.1 auth
| Field | Type | Source | Invalidation | Notes |
|-------|------|--------|--------------|-------|
| status | 'idle'|'loading'|'authenticated'|'error' | login flows | logout/login | UI gate |
| accessToken | string|null | /api/auth/login | refresh/expire | 저장소 localStorage + memory shadow |
| refreshToken | string|null | /api/auth/login | rotate | HttpOnly cookie 대체 고려 |
| userId | number|null | decoded JWT or /api/auth/me | logout | 디버그 시 직접 id 사용 금지 (selector 제공) |

### 4.2 user (profile)
| Field | Type | Source | Invalidation |
| nickname | string | /api/users/profile | profile update success |
| avatar | string | profile fetch | update |
| goldBalance | number | dashboard.main.gold_balance OR /api/users/wallet | shop purchase, reward claim (server push) |
| streak | {count:number, lastClaimedAt?:string} | /api/streak/status | claim success or dashboard refresh |

동기화 규칙: goldBalance 는 우선 dashboard 응답의 authoritative value 사용. 개별 변경 API(구매/claim) 응답에도 balance 가 있으면 덮어씀.

### 4.3 dashboard (unified aggregate)
`GET /api/dashboard` 응답 -> normalized 저장
```
DashboardAggregateState {
  main: { level:number, exp:number, gold_balance:number, streak:{count:number,nextResetAt?:string} }
  games: { recent:[{game_type:string, last_played_at:string, last_result?:string}], stats:{ total_spins:number, win_rate:number } }
  social_proof: { online_users:number, active_events:number } (예시 값, 실제 응답과 diff 시 버전 bump)
  _meta: { generated_at:string, version:number }
}
```
추가 meta.version: 로컬 계산 필드 (스키마 hash). backend 스키마 변경 시 문서 갱신.

Invalidation Sources:
- 로그인 직후 최초 fetch
- focus revalidate (탭 재진입)
- 보상/구매 완료 후 gold_balance 차이 감지 시 강제 refetch

### 4.4 progress.events
```
EventProgressSlice {
  byId: {
    [eventId:number]: {
       eventId,
       joined: boolean,
       requirements: { type:string, target:number, current:number }[]
       completed: boolean,
       claimed: boolean,
       progressVersion: number,
       lastProgressAt?: string,
       rewardPreview: RewardItem[]
    }
  }
  list: number[]           // ordering per backend priority
  lastSyncedAt?: string
}
```
소스:
- 목록: GET /api/events → list + byId skeleton merge
- 상세/참여: POST /api/events/join/{id} → joined=true
- 진행 갱신: PUT /api/events/progress/{id} (또는 향후 gameplay hook push)
- 보상 수령: POST /api/events/claim/{id} (response.progress_version 사용)

동시성 처리:
1) progress 요청 optimistic: current += delta, progressVersion += 1 (tentative)
2) 응답 수신
   - success: 서버 progress_version 비교 → 불일치시 서버 값 우선 & current 재동기화
   - failure(409/412): 즉시 전체 event 재fetch

Claim 응답 (표준):
```
{
  event_id, claimed_reward: { gold:number, items?:[...] }, progress_version, reward_items:[{type,value,...}], new_balance
}
```

### 4.5 progress.missions
구조 events 와 유사. 차이점:
- missionType: daily | weekly | achievement
- resetAt (daily/weekly)
- key: `<type>:<missionId>` 내부 저장 but UI selector 는 그룹별 분리
- Claim 표준화 예정 (현재 이벤트와 동일 형태로 맞출 계획 Phase B)

### 4.6 rewards
| Field | Type | Source | Notes |
| pendingCount | number | derived(events+missions where completed && !claimed) | selector 계산 |
| lastClaimedAt | string? | claim responses | 최근 UX 배지 강조 |
| recentClaims | ClaimSummary[] | append from claim responses | 최대 N(20) 유지 |

### 4.7 shop
| Field | Type | Source | Invalidation |
| catalog | Product[] | /api/shop/catalog | feature flag or TTL 5m |
| limited | LimitedPackage[] | /api/shop/limited | stock change push or refetch |
| transactions.byId | Tx | POST /api/shop/buy (idempotent) | status 변화 |

구매 흐름:
1) optimistic: goldBalance -= expected_cost (shadow)
2) 실패 시 rollback, 성공 시 dashboard/main.gold_balance 동기화
3) 멱등: idempotency-key header → 실패 재시도 동일 응답 사용 (서버 캐시 활용)

### 4.8 game
| Field | Type | Source |
| activeSession | { gameType, sessionId, startedAt } | start endpoint |
| lastResult | { deltaGold, multiplier, finishedAt } | finish endpoint |
| statsCache | subset from dashboard.games.stats | read-through |

게임 액션 후 hook(Phase C): 이벤트/미션 progress 자동 반영 (이벤트 id 목록 캐시 참고)

### 4.9 economy
| Field | Type | Source |
| featureFlags | { economyV2:boolean } | /api/flags or inferred catalog merge |
| priceBook | { [productId]: { gold:number, priceCents:number, discount?:number } } | catalog normalize |

### 4.10 system
| Field | Type | Source |
| appVersion | string | build time inject |
| latencySampleMs | number | ping endpoint rolling avg |
| lastRefocusAt | string | window focus listener |
| hydrationState | 'ssr'|'csr' | runtime |

## 5. 서버 상태 Fetch & 캐싱 전략
| Domain | Transport | Cache Layer | Stale TTL | Revalidate Trigger |
|--------|----------|-------------|----------|--------------------|
| dashboard | REST GET /api/dashboard | react-query | 15s | claim, purchase, focus |
| events list | REST GET /api/events | react-query | 30s | join/claim/progress mismatch |
| event detail | derive + targeted refetch | react-query | 0 (depends on list) | manual on error |
| missions | REST GET /api/missions | react-query | 60s | claim, daily reset |
| catalog | REST GET | react-query | 5m | flag toggle, purchase error w/price mismatch |
| limited stock | REST GET | polling (5s) or push | 5s | purchase / hold expiration |

## 6. progress_version 동기화 규칙
| Scenario | Client Action | Resolution |
|----------|---------------|------------|
| Optimistic + success (matching) | keep local | no-op |
| Success but server version > local+1 | overwrite local (lost update detected) | refetch delta? (Phase C) |
| PUT returns conflict (409/412) | discard optimistic, full refetch events | unify error code contract |
| Claim with lower version than local | treat as stale; immediate refetch | log anomaly (metrics) |

## 7. 이벤트 스트림 (미래 확장, Kafka→SSE/WS)
Topic → UI mapping (예정):
| Topic | Payload | Affects |
|-------|---------|---------|
| reward.granted | {user_id, source_type, source_id, delta_gold, balance, ts} | user.goldBalance, rewards.recentClaims |
| event.progress | {event_id, progress_version, current} | progress.events[event_id].requirements | 
| mission.progress | {mission_id, progress_version, current} | progress.missions[...] |
| shop.purchase | {tx_id, status, amount_gold, balance} | shop.transactions, user.goldBalance |

클라이언트는 progress_version gap >1 감지 시 해당 entity refetch.

## 8. 선택적 메모리 최적화
- list 와 byId 의 중복 requirements 제거: requirements 는 byId만 저장, list는 id 배열
- recentClaims 배열은 최대 길이 초과 시 slice(0,limit)
- goldBalance shadow rollback 큐: 최근 N(3) optimistic mutation 전 값 저장

## 9. 마이그레이션 체크리스트 (적용 순서)
1) backend /api/dashboard 배포 & claim response 확장 (완료)
2) frontend state slice scaffold 생성 (빈 reducer / react-query keys)
3) 기존 분리된 fetch 호출 → unified dashboard fetch 로 교체
4) event claim UI 에 progress_version 대응 (표시 optional)
5) optimistic progress 적용 (PUT) + rollback 처리
6) reward_items 표준 shape UI 반영
7) goldBalance authority 교체 (dashboard.main.gold_balance)

## 10. 리스크 & 대응 (프론트 범위)
| Risk | Impact | Mitigation |
|------|--------|------------|
| progress_version desync | 잘못된 진행도 표시 | gap>1 감지시 refetch |
| claim race (이중 클릭) | 중복 지급 UI 표시 | 버튼 disable + idempotency key reuse |
| catalog stale discount | 잘못된 가격 표기 | 가격 mismatch 400 시 catalog refetch |
| limited stock overrender | 구매 실패 UX 저하 | purchase 실패 코드별 재시도 안내 |
| optimistic rollback 누락 | 음수 잔액 순간 노출 | shadow rollback guard + floor(0) |

## 11. 후속 Phase B 확장 포인트
- Mission claim 응답 이벤트 claim 과 동일 스키마 정렬
- reward.granted 실시간 스트림 수신 → goldBalance push 기반 전환
- unified progress hook (게임 결과 POST → 자동 이벤트/미션 갱신 broadcast)

---
Appendix A. TypeScript Interfaces (요약)
```ts
interface RewardItem { type: string; amount: number; meta?: Record<string, any>; }
interface EventProgressEntity {
  eventId: number; joined: boolean; completed: boolean; claimed: boolean;
  requirements: { type: string; target: number; current: number }[];
  progressVersion: number; lastProgressAt?: string; rewardPreview: RewardItem[];
}
interface DashboardAggregateState { main: { level:number; exp:number; gold_balance:number; streak:{count:number; nextResetAt?:string} }; games: any; social_proof: any; _meta:{generated_at:string; version:number}; }
```
```}
