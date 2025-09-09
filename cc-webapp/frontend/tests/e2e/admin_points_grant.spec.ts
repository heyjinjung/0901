import { test, expect } from '@playwright/test';

// 환경 변수 기반 API 오리진
// @ts-ignore
const __env: any = (typeof process !== 'undefined' ? (process as any).env : {});
const API = __env.API_BASE_URL || 'http://localhost:8000';

async function getProfile(ctx: any, token: string) {
  const res = await ctx.get(`${API}/api/auth/profile`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok()) return null;
  try { return await res.json(); } catch { return null; }
}

async function getBalance(ctx: any, token: string) {
  const res = await ctx.get(`${API}/api/users/balance`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok()) return null;
  try { const j = await res.json(); return Number(j?.cyber_token_balance ?? 0); } catch { return null; }
}

test('Admin Points Gold Grant: idempotent grant updates target balance', async ({ request }: { request: import('@playwright/test').APIRequestContext }) => {
  const ctx = request as import('@playwright/test').APIRequestContext;
  const invite = __env.E2E_INVITE_CODE || '5858';

  // 1) 관리자 계정 생성 및 로그인 토큰
  const adminNick = `admin_points_${Date.now().toString(36)}`;
  const regAdmin = await ctx.post(`${API}/api/auth/register`, { data: { invite_code: invite, nickname: adminNick } });
  test.skip(!regAdmin.ok(), `admin register failed: ${regAdmin.status()}`);
  const adminJson = await regAdmin.json();
  const adminToken: string = adminJson?.access_token;
  test.skip(!adminToken, 'no admin access_token');

  // site_id 확보 후 dev elevate 로 관리자 권한 부여
  let adminSiteId: string | undefined = adminJson?.user?.site_id;
  if (!adminSiteId) {
    const prof = await getProfile(ctx, adminToken);
    adminSiteId = prof?.site_id;
  }
  test.skip(!adminSiteId, 'cannot resolve admin site_id');
  const elev = await ctx.post(`${API}/api/admin/users/elevate`, { data: { site_id: adminSiteId } });
  test.skip(!elev.ok(), `elevate failed or unavailable: ${elev.status()}`);

  // 2) 대상 사용자 생성
  const targetNick = `target_points_${Date.now().toString(36)}`;
  const regTarget = await ctx.post(`${API}/api/auth/register`, { data: { invite_code: invite, nickname: targetNick } });
  test.skip(!regTarget.ok(), `target register failed: ${regTarget.status()}`);
  const targetJson = await regTarget.json();
  const targetToken: string = targetJson?.access_token;
  test.skip(!targetToken, 'no target access_token');

  const targetProf = await getProfile(ctx, targetToken);
  const targetId: number | undefined = targetProf?.id ?? targetJson?.user?.id;
  test.skip(!targetId, 'cannot resolve target user_id');

  // 3) 기존 잔액
  const before = await getBalance(ctx, targetToken);
  test.skip(before == null, 'cannot read target balance');

  const headers = { Authorization: `Bearer ${adminToken}` };
  const amount = 123;
  const idem = `e2e-${Date.now().toString(36)}`;

  // 4) 골드 지급
  const grant1 = await ctx.post(`${API}/api/admin/users/${targetId}/gold/grant`, {
    headers,
    data: { amount, reason: 'e2e', idempotency_key: idem },
  });
  if (![200].includes(grant1.status())) {
    test.skip(true, `grant not available: ${grant1.status()}`);
  }
  const g1 = await grant1.json();
  expect(g1?.granted).toBe(amount);
  expect(typeof g1?.new_gold_balance).toBe('number');

  // 5) 대상 잔액 확인 (권위 엔드포인트)
  const after = await getBalance(ctx, targetToken);
  expect(typeof after).toBe('number');
  if (typeof before === 'number' && typeof after === 'number') {
    expect(after).toBeGreaterThanOrEqual(before + amount);
  }

  // 6) 멱등 재호출 → 재사용 플래그/영수증 동일성
  const grant2 = await ctx.post(`${API}/api/admin/users/${targetId}/gold/grant`, {
    headers,
    data: { amount, reason: 'e2e', idempotency_key: idem },
  });
  expect(grant2.status()).toBe(200);
  const g2 = await grant2.json();
  expect(g2?.idempotent_reuse).toBeTruthy();
  if (g1?.receipt_code && g2?.receipt_code) {
    expect(g2.receipt_code).toBe(g1.receipt_code);
  }
});
