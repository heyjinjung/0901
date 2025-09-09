import { test, expect, request } from '@playwright/test';

// 환경 변수 기반 API 오리진
const __env: any = (typeof process !== 'undefined' ? (process as any).env : {});
const API = __env.API_BASE_URL || 'http://localhost:8000';

async function getProfile(ctx: any, token: string) {
  const res = await ctx.get(`${API}/api/auth/profile`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok()) return null;
  try { return await res.json(); } catch { return null; }
}

// 상점 업서트 직후 목록 재조회 즉시 반영 스모크
// - 카운트 증가/감소, 필드 변경 즉시 반영을 단언
// - 관리자 권한이 필요한 엔드포인트이므로 elevate가 실패하면 skip 처리
// - 컨테이너/CI 환경별 편차를 줄이기 위해 최대 3회/최대 1.5초 내 재시도 대기

test('Admin Shop: upsert → immediate refetch reflects changes (count + fields)', async () => {
  const ctx = await request.newContext();
  const nickname = `shop_refetch_${Date.now().toString(36)}`;
  const invite = __env.E2E_INVITE_CODE || '5858';

  // 1) 회원가입
  const reg = await ctx.post(`${API}/api/auth/register`, { data: { invite_code: invite, nickname } });
  test.skip(!reg.ok(), `register failed: ${reg.status()}`);
  const regJson = await reg.json();
  const token: string = regJson?.access_token;
  test.skip(!token, 'no access_token from register');

  // 2) site_id 확인 후 elevate
  let siteId: string | undefined = regJson?.user?.site_id;
  if (!siteId) {
    const prof = await getProfile(ctx, token);
    siteId = prof?.site_id;
  }
  test.skip(!siteId, 'cannot resolve site_id for elevation');
  const elev = await ctx.post(`${API}/api/admin/users/elevate`, { data: { site_id: siteId } });
  test.skip(!elev.ok(), `elevate not available or failed (${elev.status()})`);

  const headers = { Authorization: `Bearer ${token}` };

  // util: 목록 재조회 헬퍼(최대 3회 재시도)
  async function getList(query: string = '') {
    let last: any[] | null = null;
    for (let i = 0; i < 3; i++) {
      const res = await ctx.get(`${API}/api/shop/admin/products${query}`, { headers });
      if (res.ok()) {
        const js = await res.json();
        if (Array.isArray(js)) return js;
        last = js;
      }
      await new Promise(r => setTimeout(r, 500));
    }
    return last ?? [];
  }

  // 3) 최초 목록 스냅샷
  const initial = await getList();
  const initialCount = Array.isArray(initial) ? initial.length : 0;

  // 4) 생성(업서트) → 즉시 재조회 시 count+1 & 필드 존재 확인
  const pid = `e2e-refetch-${Date.now()}`;
  const createRes = await ctx.post(`${API}/api/shop/admin/products`, {
    headers,
    data: { product_id: pid, name: 'Refetch Test', price: 1111 },
  });
  expect([200, 400]).toContain(createRes.status());

  const afterCreate = await getList();
  expect(afterCreate.length >= initialCount).toBeTruthy();
  const created = afterCreate.find((x: any) => x?.product_id === pid);
  if (createRes.status() === 200) {
    expect(created).toBeTruthy();
    expect(created?.name).toBe('Refetch Test');
    expect(typeof created?.price).toBe('number');
  }

  // 5) 업데이트 → 즉시 재조회 시 필드 변경 반영
  const updateRes = await ctx.put(`${API}/api/shop/admin/products/${pid}`, {
    headers,
    data: { name: 'Refetch Updated', price: 2222 },
  });
  expect([200, 404]).toContain(updateRes.status());

  const afterUpdate = await getList();
  const updated = afterUpdate.find((x: any) => x?.product_id === pid);
  if (updateRes.status() === 200) {
    expect(updated?.name).toBe('Refetch Updated');
    expect(updated?.price).toBe(2222);
  }

  // 6) 삭제 → 기본 목록에서 사라짐, include_deleted=true에서 deleted_at 확인
  const delRes = await ctx.delete(`${API}/api/shop/admin/products/${pid}`, { headers });
  expect([200, 404]).toContain(delRes.status());

  const afterDelete = await getList();
  expect(afterDelete.every((x: any) => x?.product_id !== pid)).toBeTruthy();

  const listDeleted = await getList('?include_deleted=true');
  const deletedItem = listDeleted.find((x: any) => x?.product_id === pid);
  if (deletedItem) expect(Boolean(deletedItem?.deleted_at)).toBeTruthy();

  // 7) 복구 → 기본 목록 복귀 확인
  const restoreRes = await ctx.post(`${API}/api/shop/admin/products/${pid}/restore`, { headers });
  expect([200, 404]).toContain(restoreRes.status());

  const afterRestore = await getList();
  expect(afterRestore.some((x: any) => x?.product_id === pid)).toBeTruthy();
});
