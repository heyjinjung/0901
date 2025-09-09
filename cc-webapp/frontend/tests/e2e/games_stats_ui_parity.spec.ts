import { test, expect, request } from '@playwright/test';

// UI 합계 = /api/games/stats/me 파리티 스펙 (가드 포함)
// 실행 조건: E2E_REQUIRE_STATS_PARITY=1 이고, /api/games/stats/me 가 200일 때만

const API = process.env.API_BASE_URL || 'http://localhost:8000';

async function apiSignup(ctx: any) {
    const nickname = `ui_parity_${Date.now().toString(36)}`;
    const invite = process.env.E2E_INVITE_CODE || '5858';
    const res = await ctx.post(`${API}/api/auth/register`, { data: { invite_code: invite, nickname } });
    if (!res.ok()) return null;
    try { return await res.json(); } catch { return null; }
}

async function ensureSomeGameActions(page: import('@playwright/test').Page, ctx: any, accessToken: string) {
    // 시도: RPS 클릭 1회, Crash 짧은 러닝, Gacha 1회 API 호출
    // 환경/라우팅에 따라 존재하지 않을 수 있으므로 전부 best-effort로 시도하고 실패해도 계속 진행
    // 1) RPS
    try {
        const rpsLink = page.getByRole('link', { name: /가위바위보|RPS/i }).first();
        if (await rpsLink.count() > 0 && await rpsLink.isVisible()) {
            await rpsLink.click();
            const rpsButtons = page.locator('button:has-text("\u270a"), button:has-text("\u270b"), button:has-text("\u270c")');
            if (await rpsButtons.count() > 0) {
                await rpsButtons.first().click({ trial: true }).catch(() => { });
                await rpsButtons.first().click().catch(() => { });
                await page.waitForTimeout(500);
            }
        }
    } catch { }

    // 2) Crash
    try {
        const crashLink = page.getByRole('link', { name: /크래시|Crash/i }).first();
        if (await crashLink.count() > 0 && await crashLink.isVisible()) {
            await crashLink.click();
            const startBtn = page.getByRole('button', { name: /게임 시작|Start/i }).first();
            if (await startBtn.count() > 0 && await startBtn.isVisible()) {
                await startBtn.click().catch(() => { });
                await page.waitForTimeout(600);
                const cashoutBtn = page.getByRole('button', { name: /캐시아웃|Cashout/i }).first();
                if (await cashoutBtn.count() > 0 && await cashoutBtn.isVisible()) {
                    await cashoutBtn.click({ trial: true }).catch(() => { });
                    await cashoutBtn.click().catch(() => { });
                    await page.waitForTimeout(300);
                }
            }
        }
    } catch { }

    // 3) Gacha via API
    try {
        await ctx.post(`${API}/api/gacha/pull`, { headers: { Authorization: `Bearer ${accessToken}` } }).catch(() => null);
    } catch { }
}

async function fetchServerStats(ctx: any, token: string) {
    const res = await ctx.get(`${API}/api/games/stats/me`, { headers: { Authorization: `Bearer ${token}` } }).catch(() => null);
    if (!res || !res.ok()) return null;
    try { return await res.json(); } catch { return null; }
}

async function readUiTotal(page: import('@playwright/test').Page): Promise<number | null> {
    // 우선순위 셀렉터: 명시적 testid → 대체 testid → 텍스트 패턴
    const trySelectors = [
        '[data-testid="stats-total"]',
        '[data-testid="stats-total-actions"]',
        '[data-testid="games-stats-total"]',
    ];
    for (const sel of trySelectors) {
        const el = page.locator(sel).first();
        if (await el.count() > 0 && await el.isVisible().catch(() => false)) {
            const txt = await el.textContent().catch(() => '');
            const n = Number((txt || '').replace(/[^0-9.-]/g, ''));
            if (!Number.isNaN(n)) return n;
        }
    }
    // 텍스트 패턴: "총 플레이" 또는 "Total" 등에서 숫자 추출
    const candidate = page.locator('text=/총\s*플레이|Total\s*Actions/i').first();
    if (await candidate.count().catch(() => 0) > 0) {
        const txt = await candidate.textContent().catch(() => '');
        const m = (txt || '').match(/([0-9][0-9,\.]*)/);
        if (m) {
            const n = Number(m[1].replace(/[^0-9.-]/g, ''));
            if (!Number.isNaN(n)) return n;
        }
    }
    return null;
}

test('[Games] UI total equals /games/stats/me (guarded)', async ({ page }: { page: import('@playwright/test').Page }) => {
    // 가드: 환경 변수 필요
    test.skip(process.env.E2E_REQUIRE_STATS_PARITY !== '1', 'E2E_REQUIRE_STATS_PARITY!=1');

    const ctx = await request.newContext();
    const reg = await apiSignup(ctx);
    test.skip(!reg?.access_token, 'register failed');
    const token: string = reg.access_token;

    // 엔드포인트 가용성 체크
    const probe = await ctx.get(`${API}/api/games/stats/me`, { headers: { Authorization: `Bearer ${token}` } }).catch(() => null);
    test.skip(!probe || !probe.ok(), `stats endpoint unavailable: ${probe ? probe.status() : 'no-resp'}`);

    // 앱 진입 후 게임 액션 유도
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(200);
    await ensureSomeGameActions(page, ctx, token);

    // 서버 합계 조회
    const server = await fetchServerStats(ctx, token);
    test.skip(!server || typeof server !== 'object', 'no server stats');

    // 서버 합계 숫자 후보: total, total_actions, actions, sum 등 – 존재하는 첫 숫자 사용
    const serverCandidates = [
        (server as any)?.total,
        (server as any)?.total_actions,
        (server as any)?.actions,
        (server as any)?.sum,
    ].filter(v => typeof v === 'number');
    test.skip(serverCandidates.length === 0, 'no numeric total in server stats');
    const serverTotal: number = Number(serverCandidates[0]);

    // 대시보드/프로필에서 UI 합계 추출 시도
    // 홈에 노출되지 않으면 내비 버튼으로 이동 시도
    const toDashboard = page.getByRole('link', { name: /대시보드|Dashboard|게임 센터|Game Center/i }).first();
    if (await toDashboard.count().catch(() => 0) > 0 && await toDashboard.isVisible().catch(() => false)) {
        await toDashboard.click().catch(() => { });
        await page.waitForTimeout(200);
    }
    const uiTotal = await readUiTotal(page);
    test.skip(uiTotal == null, 'no UI total testid/text detected');

    expect(typeof uiTotal).toBe('number');
    expect(uiTotal).toBe(serverTotal);
});
