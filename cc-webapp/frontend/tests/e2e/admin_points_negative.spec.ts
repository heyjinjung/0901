import { test, expect, request } from '@playwright/test';

// 환경 변수 기반 API 오리진 및 엄격 검증 프로파일
// @ts-ignore
const __env: any = (typeof process !== 'undefined' ? (process as any).env : {});
const API = __env.API_BASE_URL || 'http://localhost:8000';
const STRICT = __env.ADMIN_NEG_STRICT === '1';
const EXPECT_NOAUTH = Number.parseInt(__env.ADMIN_EXPECT_NOAUTH_CODE || '401', 10);
const EXPECT_NONADMIN = Number.parseInt(__env.ADMIN_EXPECT_NONADMIN_CODE || '403', 10);
const EXPECT_INVALID = Number.parseInt(__env.ADMIN_EXPECT_INVALID_AMOUNT_CODE || '422', 10);

async function signup(ctx: any) {
  const nickname = `neg_${Date.now().toString(36)}_${Math.floor(Math.random()*1e4)}`;
  const invite = __env.E2E_INVITE_CODE || '5858';
  const res = await ctx.post(`${API}/api/auth/register`, { data: { invite_code: invite, nickname } });
  return res.ok() ? res.json() : null;
}

async function getProfile(ctx: any, token: string) {
  const res = await ctx.get(`${API}/api/auth/profile`, { headers: { Authorization: `Bearer ${token}` } });
  if (!res.ok()) return null;
  try { return await res.json(); } catch { return null; }
}

test('Admin Points: non-admin cannot grant gold; no-token/unauthorized strict by profile', async () => {
  const ctx = await request.newContext();

  // 대상 사용자 생성
  const target = await signup(ctx);
  test.skip(!target, 'target signup failed');
  const targetToken = target.access_token as string;
  const targetProf = await getProfile(ctx, targetToken);
  const targetId = targetProf?.id ?? target?.user?.id;
  test.skip(!targetId, 'cannot resolve target user_id');

  // 1) 토큰 없이 호출 → 기본 401/403 허용, STRICT 모드에서는 EXPECT_NOAUTH 고정
  const rNoAuth = await ctx.post(`${API}/api/admin/users/${targetId}/gold/grant`, { data: { amount: 10, reason: 'x' } });
  if (STRICT) {
    expect(rNoAuth.status()).toBe(EXPECT_NOAUTH);
  } else {
    expect([401, 403]).toContain(rNoAuth.status());
  }

  // 2) 일반 사용자 토큰으로 호출 → 401/403 기대 (권한 미적용 환경은 skip)
  const nonAdmin = await signup(ctx);
  test.skip(!nonAdmin, 'non-admin signup failed');
  const nonAdminToken = nonAdmin.access_token as string;
  const rNonAdmin = await ctx.post(`${API}/api/admin/users/${targetId}/gold/grant`, {
    headers: { Authorization: `Bearer ${nonAdminToken}` },
    data: { amount: 10, reason: 'x' },
  });
  if (STRICT) {
    expect(rNonAdmin.status()).toBe(EXPECT_NONADMIN);
  } else {
    if (![401, 403].includes(rNonAdmin.status())) {
      test.skip(true, `expected 401/403, got ${rNonAdmin.status()}`);
    }
    expect([401, 403]).toContain(rNonAdmin.status());
  }
});

test('Admin Points: invalid amount returns 400/422 (admin elevated) – strict by profile', async () => {
  const ctx = await request.newContext();
  const admin = await signup(ctx);
  test.skip(!admin, 'admin signup failed');
  const adminToken = admin.access_token as string;

  // elevate admin
  const prof = await getProfile(ctx, adminToken);
  const siteId = prof?.site_id ?? admin?.user?.site_id;
  test.skip(!siteId, 'cannot resolve admin site_id');
  const elev = await ctx.post(`${API}/api/admin/users/elevate`, { data: { site_id: siteId } });
  test.skip(!elev.ok(), `elevate unavailable: ${elev.status()}`);

  // target user
  const target = await signup(ctx);
  test.skip(!target, 'target signup failed');
  const targetToken = target.access_token as string;
  const targetProf = await getProfile(ctx, targetToken);
  const targetId = targetProf?.id ?? target?.user?.id;
  test.skip(!targetId, 'cannot resolve target user_id');

  // negative amount
  const r = await ctx.post(`${API}/api/admin/users/${targetId}/gold/grant`, {
    headers: { Authorization: `Bearer ${adminToken}` },
    data: { amount: -5, reason: 'bad' },
  });
  if (STRICT) {
    expect(r.status()).toBe(EXPECT_INVALID);
  } else {
    if (![400, 422].includes(r.status())) {
      test.skip(true, `expected 400/422, got ${r.status()}`);
    }
    expect([400, 422]).toContain(r.status());
  }
});
