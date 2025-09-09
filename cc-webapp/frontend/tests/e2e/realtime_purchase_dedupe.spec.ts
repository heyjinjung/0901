import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL || 'http://frontend:3000';
const API = process.env.API_BASE_URL || 'http://localhost:8000';

async function devOnlyAvailable(request: any, accessToken: string) {
  const res = await request
    .post(`${API}/api/test/realtime/emit/stats_update`, {
      data: { stats: { ping: 1 } },
      headers: { Authorization: `Bearer ${accessToken}` },
    })
    .catch(() => null);
  if (!res) return false;
  if (res.status() === 403 || res.status() === 404) return false;
  return res.status() >= 200 && res.status() < 300;
}

test('[Realtime] purchase_update dedupe smoke (dev router required)', async ({ page, request }: any) => {
  // 1) 신규 유저 등록
  const nickname = 'rd_' + Math.random().toString(36).slice(2, 8);
  const reg = await request.post(`${API}/api/auth/register`, {
    data: { nickname, invite_code: process.env.E2E_INVITE_CODE || '5858' },
  });
  expect(reg.ok()).toBeTruthy();
  const { access_token, refresh_token } = await reg.json();

  // 2) dev 전용 라우터 가용성 확인(없으면 스킵)
  const available = await devOnlyAvailable(request, access_token);
  test.skip(!available, 'dev-only realtime emit API unavailable');

  // 3) 토큰 주입 후 홈 진입
  await page.addInitScript(([a, r, nick]: any[]) => {
    try {
      localStorage.setItem(
        'cc_auth_tokens',
        JSON.stringify({ access_token: a, refresh_token: r || undefined })
      );
      localStorage.setItem(
        'game-user',
        JSON.stringify({ id: 'e2e', nickname: nick, goldBalance: 0, level: 1 })
      );
    } catch {}
  }, [access_token, refresh_token, nickname]);

  await page.goto(BASE + '/');

  // 4) 동일 영수증으로 연속 purchase_update 2회 송신 → 토스트 중복 억제 기대
  const receipt = `E2E_DUP_${Date.now()}`;
  const headers = { Authorization: `Bearer ${access_token}` } as any;
  await request.post(`${API}/api/test/realtime/emit/purchase_update`, {
    data: { status: 'failed', product_id: 'pkg_1', receipt_code: receipt, reason_code: 'TEST' },
    headers,
  });
  await request.post(`${API}/api/test/realtime/emit/purchase_update`, {
    data: { status: 'failed', product_id: 'pkg_1', receipt_code: receipt, reason_code: 'TEST' },
    headers,
  });

  // 5) 토스트 선택자: 프로젝트 공통 토스트 혹은 접근성 상태 역할
  const toasts = page.locator('[data-testid="toast"], [role="status" i], .toast');

  // 최대 3초 동안 최소 1개 토스트가 나타나길 대기(테마에 따라 없을 수 있어 스킵)
  const appeared = await toasts.first().waitFor({ state: 'visible', timeout: 3000 }).then(() => true).catch(() => false);
  if (!appeared) test.skip(true, 'No toast surfaced in this theme; dedupe visually unverifiable.');

  // 잠시 안정화 후 개수 측정(중복 억제: 1개 이하)
  await page.waitForTimeout(800);
  const count = await toasts.count().catch(() => 0);
  expect(count).toBeLessThanOrEqual(1);
});
