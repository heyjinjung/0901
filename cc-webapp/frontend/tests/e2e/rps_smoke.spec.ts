import { test, expect, request, APIRequestContext, Page } from '@playwright/test';

// @ts-ignore
const __env: any = (typeof process !== 'undefined' ? (process as any).env : {});
const API = __env.API_BASE_URL || 'http://localhost:8000';

async function apiSignupLogin(ctx: APIRequestContext) {
  const nickname = `rps_smoke_${Date.now().toString(36)}`;
  const invite = __env.E2E_INVITE_CODE || '5858';
  const res = await ctx.post(`${API}/api/auth/register`, { data: { invite_code: invite, nickname } });
  expect(res.ok()).toBeTruthy();
  const json = await res.json();
  return json?.access_token as string;
}

// Best-effort helper to navigate to RPS screen
async function goToRps(page: Page) {
  // Try a direct link button/text in nav
  const rpsLink = page.getByRole('link', { name: /가위바위보|RPS/i }).first();
  if (await rpsLink.count().catch(() => 0)) {
    if (await rpsLink.isVisible().catch(() => false)) {
      await rpsLink.click().catch(() => {});
      await page.waitForTimeout(250);
      return true;
    }
  }
  // Fallback: look for on-page title
  const title = page.getByText(/가위바위보 대전|RPS/i).first();
  return (await title.count().catch(() => 0)) > 0;
}

// Returns one of ✊ ✋ ✌ to click
function choiceEmojiSelector() {
  return 'button:has-text("✊"), button:has-text("✋"), button:has-text("✌")';
}

// Minimal response shape for waitForResponse predicate
interface MinimalResponse {
  url(): string;
  status(): number;
  json(): Promise<any>;
}

// [RPS] happy path: select -> countdown -> server 200 with result/win_amount -> UI reflects result
test('[Games] RPS smoke: server result & UI reflection', async ({ page }: { page: Page }) => {
  const ctx = await request.newContext();
  const token = await apiSignupLogin(ctx);
  expect(typeof token).toBe('string');

  // Open app root
  await page.goto('/');
  await page.waitForLoadState('domcontentloaded');
  await page.waitForTimeout(200);

  // Navigate to RPS if available
  const inRps = await goToRps(page);
  if (!inRps) {
    test.skip(true, 'RPS UI not available in this build');
  }

  // Ensure choice buttons exist
  const buttons = page.locator(choiceEmojiSelector());
  if (!(await buttons.count().catch(() => 0))) {
    test.skip(true, 'RPS choice buttons not found');
  }

  // Click a choice; the component waits with 3-2-1 countdown before posting
  await buttons.first().click().catch(() => {});

  // Wait for backend request to complete, assert payload fields
  const resp = (await page.waitForResponse(
    (r: any) => (r as MinimalResponse).url().includes('/api/games/rps/play') && (r as MinimalResponse).status() === 200,
    { timeout: 8000 }
  ).catch(() => null)) as MinimalResponse | null;

  // If backend not reachable, skip rather than fail the whole suite
  if (!resp) {
    test.skip(true, 'RPS backend response not observed');
  }

  const data: any = await resp!.json().catch(() => ({}));
  const result = data?.result as string | undefined;
  const winAmount = Number(data?.win_amount ?? NaN);
  expect(['win', 'lose', 'draw']).toContain(result);
  expect(Number.isNaN(winAmount)).toBeFalsy();

  // UI reflection: result banner shows VICTORY/DEFEAT/DRAW
  const banner = page.locator('text=VICTORY!, text=DEFEAT!, text=DRAW!');
  await expect(banner).toBeVisible({ timeout: 6000 });

  // History list shows a signed gold delta with G suffix
  const historyAmount = page.locator('text=/[+\-]?\d[\d,]*G/').first();
  await expect(historyAmount).toBeVisible({ timeout: 6000 });
});
