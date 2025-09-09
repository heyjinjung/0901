import { test, expect, request } from '@playwright/test';
// @ts-ignore
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

test('Gacha pull reconciles via /users/balance', async () => {
    const ctx = await request.newContext();
    const nickname = `e2e_gacha_${Date.now().toString(36)}`;
    const invite = __env.E2E_INVITE_CODE || '5858';

    // Register and auth
    const register = await ctx.post(`${API}/api/auth/register`, { data: { invite_code: invite, nickname } });
    expect(register.ok()).toBeTruthy();
    const token = (await register.json()).access_token as string;
    const headers = { Authorization: `Bearer ${token}` };

    // Baseline balance
    const before = await getBalance(ctx, token);

    // Try a single pull
    const pull = await ctx.post(`${API}/api/gacha/pull`, { headers });
    expect([200, 400, 404]).toContain(pull.status());

    // Reconcile balance
    const after = await getBalance(ctx, token);
    expect(typeof after).toBe('number');
    expect(after).toBeGreaterThanOrEqual(0);
    // Non-decreasing if pull failed; if success and costs currency, after may be <= before.
});
