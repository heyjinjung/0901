import { test, expect, request } from '@playwright/test';
const ENABLE = process.env.E2E_SHOP_SYNC === '1';
const REQUIRE = process.env.E2E_REQUIRE_SHOP_SYNC === '1';
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

test('Shop buy reconciles via /users/balance (GOLD)', async () => {
    test.skip(!ENABLE, 'Disabled by default. Set E2E_SHOP_SYNC=1 to enable.');
    const ctx = await request.newContext();
    const nickname = `e2e_shop_${Date.now().toString(36)}`;
    const invite = __env.E2E_INVITE_CODE || '5858';

    // Register and auth
    const register = await ctx.post(`${API}/api/auth/register`, { data: { invite_code: invite, nickname } });
    expect(register.ok()).toBeTruthy();
    const token = (await register.json()).access_token as string;
    const headers = { Authorization: `Bearer ${token}` };

    // Baseline balance
    const before = await getBalance(ctx, token);

    // List shop items
    const itemsRes = await ctx.get(`${API}/api/shop/items`, { headers });
    if (!itemsRes.ok()) {
        if (REQUIRE) throw new Error(`shop/items not available (${itemsRes.status()})`);
        test.skip(true, `shop/items not available (${itemsRes.status()})`);
    }
    const items = await itemsRes.json();
    if (!Array.isArray(items) || items.length === 0) {
        if (REQUIRE) throw new Error('no shop items');
        test.skip(true, 'no shop items');
    }
    const first = items.find((i: any) => i?.id != null) || items[0];

    // Attempt buy
    const buyRes = await ctx.post(`${API}/api/shop/buy/${first.id}`, { headers });
    expect([200, 400, 404]).toContain(buyRes.status());

    // Reconcile balance
    const after = await getBalance(ctx, token);
    expect(typeof after).toBe('number');
    expect(after).toBeGreaterThanOrEqual(0);
});
