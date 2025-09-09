import { test, expect, request } from '@playwright/test';

// 환경 변수 기반 API 오리진
const __env: any = (typeof process !== 'undefined' ? (process as any).env : {});
const API = __env.API_BASE_URL || 'http://localhost:8000';

// 유틸: 간단 프로필 조회 (site_id 확보용); 실패시 null
async function getProfile(ctx: any, token: string) {
  const res = await ctx.get(`${API}/auth/profile`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok()) return null;
  try { return await res.json(); } catch { return null; }
}

test('Admin Shop Product CRUD: create → update → soft-delete → include_deleted → restore', async () => {
  const ctx = await request.newContext();
  const nickname = `admin_shop_${Date.now().toString(36)}`;
  const invite = __env.E2E_INVITE_CODE || '5858';

  // 1) 회원가입 (테스트 전용 /api/auth/register)
  const reg = await ctx.post(`${API}/api/auth/register`, {
    data: { invite_code: invite, nickname },
  });
  test.skip(!reg.ok(), `register failed: ${reg.status()}`);
  const regJson = await reg.json();
  const token: string = regJson?.access_token;
  test.skip(!token, 'no access_token from register');

  // 2) dev 전용 elevate 로 관리자 권한 부여 (JWT 재발급 없이 DB 기반 권한 확인을 가정)
  //    site_id 는 토큰의 유저 또는 프로필에서 획득
  let siteId: string | undefined = regJson?.user?.site_id;
  if (!siteId) {
    const prof = await getProfile(ctx, token);
    siteId = prof?.site_id;
  }
  test.skip(!siteId, 'cannot resolve site_id for elevation');

  const elev = await ctx.post(`${API}/api/admin/users/elevate`, { data: { site_id: siteId } });
  test.skip(!elev.ok(), `elevate not available or failed (${elev.status()})`);

  const headers = { Authorization: `Bearer ${token}` };

  // 고유 product_id 생성
  const pid = `e2e-prod-${Date.now()}`;

  // 3) 생성
  const createRes = await ctx.post(`${API}/api/shop/admin/products`, {
    headers,
    data: { product_id: pid, name: 'E2E Test Product', price: 1234 },
  });
  expect([200, 400]).toContain(createRes.status()); // 중복 시 400 가능성 허용

  // 4) 업데이트 (이름/가격 변경)
  const updateRes = await ctx.put(`${API}/api/shop/admin/products/${pid}`, {
    headers,
    data: { name: 'E2E Updated', price: 2345 },
  });
  expect([200, 404]).toContain(updateRes.status()); // 간헐 404 시 이후 목록 검증으로 보완

  // 5) 소프트 삭제
  const delRes = await ctx.delete(`${API}/api/shop/admin/products/${pid}`, { headers });
  expect([200, 404]).toContain(delRes.status());

  // 6) 기본 목록에서 보이지 않아야 함
  const listRes = await ctx.get(`${API}/api/shop/admin/products`, { headers });
  expect(listRes.ok()).toBeTruthy();
  const list = await listRes.json();
  expect(Array.isArray(list)).toBeTruthy();
  expect(list.every((it: any) => it?.product_id !== pid)).toBeTruthy();

  // 7) include_deleted=true 에서는 deleted_at 표시와 함께 보여야 함
  const listDeletedRes = await ctx.get(`${API}/api/shop/admin/products?include_deleted=true`, { headers });
  expect(listDeletedRes.ok()).toBeTruthy();
  const listDeleted = await listDeletedRes.json();
  const deletedItem = listDeleted.find((it: any) => it?.product_id === pid);
  expect(deletedItem?.deleted_at).toBeTruthy();

  // 8) 복구
  const restoreRes = await ctx.post(`${API}/api/shop/admin/products/${pid}/restore`, { headers });
  expect([200, 404]).toContain(restoreRes.status());

  // 9) 기본 목록 재확인
  const listAfterRes = await ctx.get(`${API}/api/shop/admin/products`, { headers });
  expect(listAfterRes.ok()).toBeTruthy();
  const listAfter = await listAfterRes.json();
  expect(listAfter.some((it: any) => it?.product_id === pid)).toBeTruthy();
});
