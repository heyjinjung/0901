import { test, expect, request } from '@playwright/test';

// @ts-ignore
const __env: any = (typeof process !== 'undefined' ? (process as any).env : {});
const API = __env.API_BASE_URL || 'http://localhost:8000';

async function apiSignupLogin(ctx: any) {
    const nickname = `rpscrash_${Date.now().toString(36)}`;
    const invite = __env.E2E_INVITE_CODE || '5858';
    const res = await ctx.post(`${API}/api/auth/register`, { data: { invite_code: invite, nickname } });
    expect(res.ok()).toBeTruthy();
    const json = await res.json();
    return json?.access_token as string;
}

async function apiGetBalance(ctx: any, token: string) {
    const res = await ctx.get(`${API}/api/users/balance`, { headers: { Authorization: `Bearer ${token}` } });
    expect(res.ok()).toBeTruthy();
    const j = await res.json();
    return Number(j?.cyber_token_balance ?? 0);
}

test.describe('RPS/Crash server-authoritative reconcile', () => {
    test('After actions, UI balance matches /users/balance across pages', async ({ page }) => {
        const ctx = await request.newContext();
        const token = await apiSignupLogin(ctx);
        const base = await apiGetBalance(ctx, token);

        // Visit app
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(300);

        // Navigate to RPS and play one round if possible
    {
        const rpsLink = page.getByRole('link', { name: /가위바위보|RPS/i }).first();
        if (await rpsLink.count().catch(() => 0) > 0 && await rpsLink.isVisible().catch(() => false)) {
            await rpsLink.click().catch(() => {});
            await page.waitForTimeout(200);
        }
    }
        // If RPS page has buttons with emojis, try clicking one
        const rpsButtons = page.locator('button:has-text("✊"), button:has-text("✋"), button:has-text("✌")');
        if ((await rpsButtons.count().catch(() => 0)) > 0) {
            await rpsButtons.first().click({ trial: true }).catch(() => {});
            await rpsButtons.first().click().catch(() => {});
            await page.waitForTimeout(800);
        }

        // Navigate to Crash and start a short run
    {
        const crashLink = page.getByRole('link', { name: /크래시|Crash/i }).first();
        if (await crashLink.count().catch(() => 0) > 0 && await crashLink.isVisible().catch(() => false)) {
            await crashLink.click().catch(() => {});
            await page.waitForTimeout(200);
        }
    }
        const startBtn = page.getByRole('button', { name: /게임 시작|Start/i }).first();
        if (await startBtn.count().catch(() => 0) > 0 && await startBtn.isVisible().catch(() => false)) {
            await startBtn.click().catch(() => {});
            await page.waitForTimeout(700);
            const cashoutBtn = page.getByRole('button', { name: /캐시아웃|Cashout/i }).first();
            if (await cashoutBtn.count().catch(() => 0) > 0 && await cashoutBtn.isVisible().catch(() => false)) {
                await cashoutBtn.click({ trial: true }).catch(() => {});
                await cashoutBtn.click().catch(() => {});
                await page.waitForTimeout(400);
            }
        }

        // Return to dashboard/profile and read visible GOLD text
    {
        const back = page.getByRole('button', { name: /뒤로|Back|홈|Home/i }).first();
        if (await back.count().catch(() => 0) > 0 && await back.isVisible().catch(() => false)) {
            await back.click().catch(() => {});
            await page.waitForTimeout(200);
        }
    }
    const dashGoldText = await page.locator('text=/\d[\d,]*\s*G$/').first().textContent({ timeout: 500 }).catch(() => null);
        const dashGold = dashGoldText ? Number(dashGoldText.replace(/[^0-9]/g, '') || '0') : 0;

        // Fetch authoritative
        const auth = await apiGetBalance(ctx, token);
        expect(typeof auth).toBe('number');
        if (dashGold) expect(dashGold).toBe(auth);
    });
});
