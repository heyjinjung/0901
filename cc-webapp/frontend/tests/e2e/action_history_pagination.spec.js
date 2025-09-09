const { test, expect } = require('@playwright/test');

test.describe('Action history pagination', () => {
  test('navigates pages without duplication and shows controls state', async ({ page }) => {
    const base = process.env.BASE_URL || 'http://frontend:3000';
    const API = process.env.API_BASE_URL || 'http://localhost:8000';

    // 0) 인증 시드: 신규 유저 등록 후 토큰을 번들 형태로 주입
    const nickname = 'histjs_' + Math.random().toString(36).slice(2, 8);
    const reg = await page.request.post(`${API}/api/auth/register`, {
      data: { nickname, invite_code: process.env.E2E_INVITE_CODE || '5858' }
    });
    expect(reg.ok()).toBeTruthy();
    const { access_token, refresh_token } = await reg.json();
  await page.addInitScript(([a, r, nick]) => {
      try {
        localStorage.setItem('cc_auth_tokens', JSON.stringify({ access_token: a, refresh_token: r || undefined }));
        localStorage.setItem('game-user', JSON.stringify({ id: 'e2e', nickname: nick, goldBalance: 0, level: 1 }));
    // E2E: 초기화 시 바로 프로필로 진입하도록 플래그 설정
  localStorage.setItem('E2E_ACTION_HISTORY_STUB', '1');
    localStorage.setItem('E2E_FORCE_SCREEN', 'profile');
      } catch {}
    }, access_token, refresh_token, nickname);

      // UI 하단 내비게이션 렌더를 위해 최소 사용자 스텁도 주입
      await page.addInitScript((nick) => {
        try {
          const stub = {
            id: 'e2e-' + Math.random().toString(36).slice(2),
            nickname: nick,
            goldBalance: 1000,
            level: 1,
            dailyStreak: 0,
            lastLogin: new Date().toISOString(),
          };
          localStorage.setItem('game-user', JSON.stringify(stub));
        } catch {}
      }, nickname);

  await page.goto(base + '/e2e/profile');
  await expect(page.getByTestId('profile-screen').first()).toBeVisible({ timeout: 20000 });

    // 리스트 로드 대기
  const list = page.locator('[data-testid="action-history-list"]').first();
  await expect(list).toBeVisible({ timeout: 20000 });

  const firstPageIds = await list.locator('> div').evaluateAll((rows) => rows.map((r) => (r.getAttribute('data-key') || r.getAttribute('key'))));

    // 다음 페이지
    // 하단 네비게이션 전역 차단 스타일 주입 (초기화 이후 안전망)
    await page.addInitScript(() => {
      try {
        const style = document.createElement('style');
        style.setAttribute('data-e2e-bottomnav', 'off');
        style.textContent = `
          [data-testid="bottom-navigation"]{ pointer-events:none !important; opacity:0 !important; transform: translateY(200vh) !important; }
        `;
        document.head.appendChild(style);
      } catch {}
    });
    const nextBtn = page.getByTestId('action-next');
    if (await nextBtn.isEnabled()) {
      // programmatic click 우선 적용으로 클릭 간섭 회피
      await nextBtn.evaluate((btn) => btn.click());
      await page.waitForFunction((args) => {
        const el = document.querySelector(args.sel);
        if (!el) return false;
        const rows = el.querySelectorAll(':scope > div');
        if (!rows.length) return false;
        const first = rows[0].getAttribute('data-key') || rows[0].getAttribute('key');
        return !!first && first !== args.prevFirst;
      }, { sel: '[data-testid="action-history-list"]', prevFirst: (firstPageIds && firstPageIds[0]) || null }, { timeout: 5000 });
      const secondPageIds = await list.locator('> div').evaluateAll((rows) => rows.map((r) => (r.getAttribute('data-key') || r.getAttribute('key'))));
      const dup = (secondPageIds || []).filter((id) => id && (firstPageIds || []).includes(id));
      expect(dup.length).toBe(0);
    }

    // 이전 페이지 버튼 상태 확인
    const prevBtn = page.getByTestId('action-prev');
    await expect(prevBtn).toBeVisible();
  });
});
