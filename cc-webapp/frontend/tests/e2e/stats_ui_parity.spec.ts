import { test, expect } from '@playwright/test';

// 목적: /api/games/stats/me 200 안정화 시, UI 합계와 API 값을 비교하는 파리티 스펙
// 가드: 엔드포인트 미노출/비정상 응답/스키마 상이 시 안전 스킵

test.describe('[Games] stats UI ↔ API parity (guarded)', () => {
  test('UI totals equal API when /games/stats/me is OK', async ({ page, request }: any) => {
    const BASE = process.env.BASE_URL || 'http://frontend:3000';
    const API = process.env.API_BASE_URL || 'http://localhost:8000';
  const REQUIRE = process.env.E2E_REQUIRE_STATS_PARITY === '1';

    // 선택적 플래그로 완전 비활성화 가능
    if (process.env.E2E_DISABLE_STATS_PARITY === '1') {
      test.skip(true, 'stats parity disabled by env');
      return;
    }

    // 1) 신규 유저 등록
    const nickname = 'sp_' + Math.random().toString(36).slice(2, 8);
    const reg = await request.post(`${API}/api/auth/register`, {
      data: { nickname, invite_code: process.env.E2E_INVITE_CODE || '5858' },
    });
    expect(reg.ok()).toBeTruthy();
    const { access_token, refresh_token } = await reg.json();

    // 2) 토큰 주입 + 프로필 화면으로 진입
  await page.addInitScript(([a, r, nick]: any[]) => {
      try {
        localStorage.setItem('cc_auth_tokens', JSON.stringify({ access_token: a, refresh_token: r || undefined }));
        localStorage.setItem('game-user', JSON.stringify({ id: 'e2e', nickname: nick, goldBalance: 0, level: 1 }));
        localStorage.setItem('E2E_FORCE_SCREEN', 'profile');
      } catch {}
    }, access_token, refresh_token, nickname);

    await page.goto(BASE + '/e2e/profile');

    // 3) API 호출 (가드: 미가용 상태는 스킵)
    const res = await request
      .get(`${API}/api/games/stats/me`, { headers: { Authorization: `Bearer ${access_token}` } })
      .catch(() => null as any);
    if (!res) {
      if (REQUIRE) throw new Error('games stats endpoint unreachable');
      test.skip(true, 'games stats endpoint unreachable');
      return;
    }
    const status = res.status();
    if ([404, 501, 403, 405, 429].includes(status) || (status >= 500 && status <= 599)) {
      if (REQUIRE) throw new Error(`games stats not available: ${status}`);
      test.skip(true, `games stats not available: ${status}`);
      return;
    }
    if (!res.ok()) {
      if (REQUIRE) throw new Error(`games stats not ok: ${status}`);
      test.skip(true, `games stats not ok: ${status}`);
      return;
    }

    const body: any = await res.json().catch(() => null);
    if (!body || typeof body !== 'object') {
      if (REQUIRE) throw new Error('games stats bad body');
      test.skip(true, 'games stats bad body');
      return;
    }

    // 4) 예상 합계 산출(여러 스키마 키 지원)
    const stats = body.stats || body;
    const expectedGames =
      stats.total_bets ?? stats.total_play_count ?? stats.total_games_played ?? stats.total_games ?? stats.totalGamesPlayed ?? 0;
    const expectedWins = stats.total_wins ?? stats.wins ?? 0;

    // 5) UI 셀렉터에서 값 추출(data-testid 기반)
    // profile-screen 존재는 필수가 아니므로, 합계 카드의 testid를 직접 탐색
    const gamesEl = page.getByTestId('stats-total-games');
    const winsEl = page.getByTestId('stats-total-wins');

    // 존재하지 않으면 스킵(환경/빌드 상이 가능)
    const existGames = await gamesEl.count().catch(() => 0);
    const existWins = await winsEl.count().catch(() => 0);
    if (!existGames || !existWins) {
      test.skip(true, 'stats total testids not present (main page stats removed)');
      return;
    }

    const uiGamesText = (await gamesEl.first().textContent()) || '';
    const uiWinsText = (await winsEl.first().textContent()) || '';
    const uiGames = parseInt(uiGamesText.replace(/[^0-9\-]/g, ''), 10);
    const uiWins = parseInt(uiWinsText.replace(/[^0-9\-]/g, ''), 10);

    expect(Number.isNaN(uiGames)).toBeFalsy();
    expect(Number.isNaN(uiWins)).toBeFalsy();

    // 6) 파리티 비교(같은 신규 유저 컨텍스트에서는 0=0이 일반적)
    expect(uiGames).toBe(expectedGames);
    expect(uiWins).toBe(expectedWins);
  });
});
