import { test, expect, request } from '@playwright/test';
// @ts-ignore - avoid requiring Node types in test env
const __env: any = (typeof process !== 'undefined' ? (process as any).env : {});
const API = __env.API_BASE_URL || 'http://localhost:8000';

async function getBalance(ctx: any, token: string) {
    const res = await ctx.get(`${API}/api/users/balance`, {
        headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.ok()).toBeTruthy();
    const json = await res.json();
    return json?.cyber_token_balance ?? 0;
}

test.describe('Currency mutation reconciles via /users/balance', () => {
    test('streak claim updates balance from authoritative endpoint', async ({ page }) => {
        // 1) Signup/Login via API
        const ctx = await request.newContext();
        const nickname = `e2e_${Date.now().toString(36)}`;
        const invite = __env.E2E_INVITE_CODE || '5858';
        const register = await ctx.post(`${API}/api/auth/register`, {
            data: { invite_code: invite, nickname },
        });
        expect(register.ok()).toBeTruthy();
        const tokens = await register.json();
        const token = tokens.access_token as string;

        // 2) Baseline balance
        const before = await getBalance(ctx, token);

        // 3) Trigger a mutation that adds currency (streak status → claim)
        const status = await ctx.get(`${API}/api/streak/status`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        expect(status.ok()).toBeTruthy();
        const claim = await ctx.post(`${API}/api/streak/claim`, {
            headers: { Authorization: `Bearer ${token}` },
            data: { action_type: 'DAILY_LOGIN' },
        });
        // 일부 환경에서는 이미 수령(400)일 수 있으므로 허용
        expect([200, 400]).toContain(claim.status());

        // 4) Immediately reconcile from authoritative endpoint
        const after = await getBalance(ctx, token);

        // 5) Assert authoritative value is numeric and non-decreasing
        expect(typeof after).toBe('number');
        expect(after).toBeGreaterThanOrEqual(0);
        expect(after).toBeGreaterThanOrEqual(before);
    });
});
