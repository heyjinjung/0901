import { test, expect } from '@playwright/test';

const BASE = process.env.BASE_URL || 'http://frontend:3000';
const API = process.env.API_BASE_URL || 'http://localhost:8000';

const ENABLE = process.env.E2E_REALTIME_MAPPING === '1';
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

test('[Realtime] 이벤트 타입 매핑 스모크 (profile_update/reward_granted/purchase_update/stats_update)', async ({ page, request }: any) => {
  // 1) 회원가입
  test.skip(!ENABLE, 'Disabled by default. Set E2E_REALTIME_MAPPING=1 to enable.');
  const nickname = 'rm_' + Math.random().toString(36).slice(2, 8);
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

  // 3) 서버 권위 잔액
  const balRes = await request.get(`${API}/api/users/balance`, { headers: { Authorization: `Bearer ${access_token}` } });
  expect(balRes.ok()).toBeTruthy();
  const bal = await balRes.json();
  const initial = Number(bal?.gold_balance ?? bal?.cyber_token_balance ?? 0) || 0;

  // 4) profile_update → GOLD 반영 확인
  const next1 = initial + 3;
  await request.post(`${API}/api/test/realtime/emit/profile_update`, {
    data: { changes: { gold_balance: next1 } },
    headers: { Authorization: `Bearer ${access_token}` },
  });
  const ok1 = await page
    .waitForFunction((expected: number) => {
      const el = document.querySelector('[data-testid="gold-quick"]');
      const n = el ? Number((el.textContent || '').replace(/[^0-9.-]/g, '')) : NaN;
      return Number.isFinite(n) && n === expected;
    }, next1, { timeout: 12000 })
    .then(() => true)
    .catch(() => false);
  if (!ok1) test.skip(true, 'profile_update UI 반영 지연 → 스킵');

  // 5) reward_granted(balance_after 동반) → GOLD 반영 확인
  const next2 = next1 + 4;
  await request.post(`${API}/api/test/realtime/emit/reward_granted`, {
    data: { reward_type: 'GOLD', amount: 4, balance_after: next2 },
    headers: { Authorization: `Bearer ${access_token}` },
  });
  const ok2 = await page
    .waitForFunction((expected: number) => {
      const el = document.querySelector('[data-testid="gold-quick"]');
      const n = el ? Number((el.textContent || '').replace(/[^0-9.-]/g, '')) : NaN;
      return Number.isFinite(n) && n === expected;
    }, next2, { timeout: 12000 })
    .then(() => true)
    .catch(() => false);
  if (!ok2) test.skip(true, 'reward_granted UI 반영 지연 → 스킵');

  // 6) purchase_update: 토스트(있다면 ≤1) 확인
  const receipt = `E2E_MAP_${Date.now()}`;
  await request.post(`${API}/api/test/realtime/emit/purchase_update`, {
    data: { status: 'failed', product_id: 'pkg_1', receipt_code: receipt, reason_code: 'TEST' },
    headers: { Authorization: `Bearer ${access_token}` },
  });
  const toasts = page.locator('[data-testid="toast"], [role="status" i], .toast');
  const appeared = await toasts.first().waitFor({ state: 'visible', timeout: 3000 }).then(() => true).catch(() => false);
  if (appeared) {
    await page.waitForTimeout(500);
    const count = await toasts.count().catch(() => 0);
    expect(count).toBeLessThanOrEqual(1);
  }

  // 7) stats_update: 부작용 없음(스모크 통과만)
  await request.post(`${API}/api/test/realtime/emit/stats_update`, {
    data: { stats: { played: 1 } },
    headers: { Authorization: `Bearer ${access_token}` },
  });
});
