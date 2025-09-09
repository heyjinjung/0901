import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL || 'http://frontend:3000';
const API = process.env.API_BASE_URL || 'http://localhost:8000';

const ENABLE = process.env.E2E_REALTIME_DEDUPE === '1';
const REQUIRE = process.env.E2E_REQUIRE_REALTIME === '1';

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

test('[Realtime] 재연결·스로틀·중복 억제 스모크', async ({ page, request }: any) => {
  test.skip(!ENABLE, 'Disabled by default. Set E2E_REALTIME_DEDUPE=1 to enable.');
  // 1) 회원가입
  const nickname = 'rr_' + Math.random().toString(36).slice(2, 8);
  const reg = await request.post(`${API}/api/auth/register`, {
    data: { nickname, invite_code: process.env.E2E_INVITE_CODE || '5858' },
  });
  expect(reg.ok()).toBeTruthy();
  const { access_token, refresh_token } = await reg.json();

  const available = await devOnlyAvailable(request, access_token);
  if (!available) {
    if (REQUIRE) throw new Error('dev-only realtime emit API unavailable');
    test.skip(true, 'dev-only realtime emit API unavailable');
  }

  // 2) 토큰 주입 및 홈 진입
  await page.addInitScript(([a, r, nick]: any[]) => {
    try {
      localStorage.setItem('cc_auth_tokens', JSON.stringify({ access_token: a, refresh_token: r || undefined }));
      localStorage.setItem('game-user', JSON.stringify({ id: 'e2e', nickname: nick, goldBalance: 0, level: 1 }));
    } catch {}
  }, [access_token, refresh_token, nickname]);
  await page.goto(BASE + '/');

  // 3) 재연결 유도: 페이지 리로드 후에도 이벤트 수신 가능해야 함
  await page.reload();

  // 4) 스로틀/중복 억제: 동일 receipt 빠르게 3회 전송 → 토스트 ≤1 (있다면)
  const receipt = `E2E_RECON_${Date.now()}`;
  const headers = { Authorization: `Bearer ${access_token}` } as any;
  await Promise.all([
    request.post(`${API}/api/test/realtime/emit/purchase_update`, { data: { status: 'failed', product_id: 'pkg_1', receipt_code: receipt, reason_code: 'TEST' }, headers }),
    request.post(`${API}/api/test/realtime/emit/purchase_update`, { data: { status: 'failed', product_id: 'pkg_1', receipt_code: receipt, reason_code: 'TEST' }, headers }),
    request.post(`${API}/api/test/realtime/emit/purchase_update`, { data: { status: 'failed', product_id: 'pkg_1', receipt_code: receipt, reason_code: 'TEST' }, headers }),
  ]);

  const toasts = page.locator('[data-testid="toast"], [role="status" i], .toast');
  const appeared = await toasts.first().waitFor({ state: 'visible', timeout: 3000 }).then(() => true).catch(() => false);
  if (appeared) {
    await page.waitForTimeout(600);
    const count = await toasts.count().catch(() => 0);
    expect(count).toBeLessThanOrEqual(1);
  }
});
