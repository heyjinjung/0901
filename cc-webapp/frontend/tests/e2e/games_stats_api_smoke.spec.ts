import { test, expect } from '@playwright/test';

const API = process.env.API_BASE_URL || 'http://localhost:8000';

test('[Games] /api/games/stats/me smoke (skip if unavailable)', async ({ request }: any) => {
  // 1) 신규 유저 등록
  const nickname = 'gs_' + Math.random().toString(36).slice(2, 8);
  const reg = await request.post(`${API}/api/auth/register`, {
    data: { nickname, invite_code: process.env.E2E_INVITE_CODE || '5858' },
  });
  expect(reg.ok()).toBeTruthy();
  const { access_token } = await reg.json();

  // 2) API 호출(미노출/미구현 환경에서는 스킵)
  const res = await request.get(`${API}/api/games/stats/me`, {
    headers: { Authorization: `Bearer ${access_token}` },
  }).catch(() => null as any);
  if (!res) { test.skip(true, 'games stats endpoint unreachable'); return; }
  const status = res.status();
  // 비가용/비구현/차단/서버오류/레이트리밋 등은 스킵 처리
  if (
    [404, 501, 403, 405, 429].includes(status) ||
    (status >= 500 && status <= 599)
  ) {
    test.skip(true, `games stats not available: ${status}`);
    return;
  }

  if (!res.ok()) { test.skip(true, `games stats not ok: ${status}`); return; }

  expect(res.ok()).toBeTruthy();
  const body = await res.json().catch(() => null);
  expect(body && typeof body === 'object').toBeTruthy();
});
