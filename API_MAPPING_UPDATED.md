# API 매핑 (Canonical) — OpenAPI 동기화 완료 (2025-09-09)

이 문서는 최신 OpenAPI 사양(openapi_spec.json)에 맞춰 정리한 권위 있는(mapping) 문서입니다. 아래 표에 없는 레거시 경로/초안은 사용하지 마세요.

## 인증 (Auth)
| 메소드 | 경로           | 설명 |
|--------|----------------|------|
| POST   | /auth/register | 사용자 등록 |
| POST   | /auth/login    | 로그인 |
| POST   | /auth/refresh  | 토큰 갱신 |
| POST   | /auth/logout   | 로그아웃 |
| GET    | /auth/profile  | 내 프로필 |
| GET    | /auth/sessions | 활성 세션 목록 |

## 사용자 (Users)
| 메소드 | 경로                   | 설명 |
|--------|------------------------|------|
| GET    | /api/users/profile     | 프로필 조회 |
| PUT    | /api/users/profile     | 프로필 수정 |
| GET    | /api/users/balance     | 잔액 조회 |
| GET    | /api/users/info        | 정보 조회 |
| GET    | /api/users/stats       | 통계 조회 |
| POST   | /api/users/tokens/add  | 토큰 추가 |
| GET    | /api/users/{user_id}   | 사용자 단건 |

## 관리자 (Admin)
| 메소드 | 경로                                        | 설명 |
|--------|---------------------------------------------|------|
| GET    | /api/admin/stats                            | 관리자 통계 |
| POST   | /api/admin/users/{user_id}/ban              | 사용자 차단 |
| POST   | /api/admin/users/{user_id}/unban            | 사용자 차단 해제 |
| POST   | /api/admin/users/{user_id}/tokens/add       | 관리자 토큰 지급 |

## 게임 (Games)
| 메소드 | 경로                      | 설명 |
|--------|---------------------------|------|
| GET    | /api/games/               | 게임 목록 |
| POST   | /api/games/slot/spin      | 슬롯 스핀 |
| POST   | /api/games/gacha/pull     | 가챠 뽑기 |
| POST   | /api/games/crash/bet      | 크래시 베팅 |
| POST   | /api/games/rps/play       | 가위바위보 |

## 보상/미션/이벤트 (Rewards, Missions, Events)
| 메소드 | 경로                                              | 설명 |
|--------|---------------------------------------------------|------|
| GET    | /api/rewards/users/{user_id}/rewards              | 사용자 보상 목록 |
| POST   | /api/rewards/distribute                           | 보상 지급 |
| GET    | /api/missions/                                    | 사용자 미션 목록 |
| POST   | /api/missions/{mission_id}/claim                  | 미션 보상 수령 |
| GET    | /api/events/                                      | 이벤트 목록 |
| GET    | /api/events/{event_id}                            | 이벤트 상세 |
| POST   | /api/events/join                                  | 이벤트 참여 |
| PUT    | /api/events/progress/{event_id}                   | 이벤트 진행 갱신 |
| POST   | /api/events/claim/{event_id}                      | 이벤트 보상 수령 |
| GET    | /api/events/missions/daily                        | 일일 미션 |
| GET    | /api/events/missions/weekly                       | 주간 미션 |
| GET    | /api/events/missions/all                          | 전체 미션 |
| PUT    | /api/events/missions/progress                     | 미션 진행 갱신 |
| POST   | /api/events/missions/claim/{mission_id}           | 미션 보상 수령 |

## 상점 (Shop)
| 메소드 | 경로               | 설명 |
|--------|--------------------|------|
| POST   | /api/shop/purchase | 상품 구매 (idempotency 정책 내부 문서 참조) |

## 초대 (Invite)
| 메소드 | 경로                                    | 설명 |
|--------|-----------------------------------------|------|
| POST   | /api/invite/generate                     | 초대 코드 생성 |
| POST   | /api/invite/validate                     | 초대 코드 검증 |
| GET    | /api/invite/codes                        | 내가 만든 코드 목록 |
| PATCH  | /api/invite/codes/{code}/deactivate      | 초대 코드 비활성화 |
| GET    | /api/invite/stats                        | 초대 통계 |

## 분석/대시보드 (Analytics & Dashboard)
| 메소드 | 경로                               | 설명 |
|--------|------------------------------------|------|
| GET    | /api/analytics/dashboard/summary   | 대시보드 요약 |
| GET    | /api/analytics/users/activity      | 사용자 활동 |
| GET    | /api/analytics/games/stats         | 게임 통계 |
| GET    | /dashboard/main                    | 메인 대시보드 |
| GET    | /dashboard/games                   | 게임 대시보드 |
| GET    | /dashboard/social-proof            | 소셜프루프 |

---
참고
- 상기 경로는 openapi_spec.json을 기준으로 정리되었습니다. 스펙 변경 시 본 문서와 CURRENT_STANDARD.md를 함께 갱신하세요.
- 구매/보안 세부 정책은 STATUS_PURCHASE_SECURITY.md를, 게임 지표 표준은 stats_details_schema.md를 참조하세요.
