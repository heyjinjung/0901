// Global setup waits for backend and frontend readiness using fetch.
// Using JS avoids TS node typing issues inside the Playwright container.

async function wait(ms) { return new Promise(res => setTimeout(res, ms)); }

async function waitForOk(url, timeoutMs) {
  const started = Date.now();
  let lastErr;
  while (Date.now() - started < timeoutMs) {
    try {
      const resp = await fetch(url, { method: 'GET' });
      // Treat any non-5xx as readiness (200/404 are fine for root)
      if (resp.status < 500) return;
      lastErr = new Error(`Status ${resp.status}`);
    } catch (e) {
      lastErr = e;
    }
    await wait(1000);
  }
  throw lastErr ?? new Error(`Timeout waiting for ${url}`);
}

module.exports = async () => {
  const api = process.env.API_BASE_URL || 'http://backend:8000';
  const web = process.env.BASE_URL || 'http://frontend:3000';

  // Backend first (prefer health, fallback to root)
  try {
    await waitForOk(`${api}/health`, 60_000);
  } catch (_) {
    await waitForOk(api, 30_000);
  }

  // Then frontend: prefer lightweight healthz if available
  try {
    await waitForOk(`${web}/healthz`, 60_000);
  } catch (_) {
    await waitForOk(web, 60_000);
  }

  // Optional: auto-toggle E2E flags when backend capabilities are ready.
  // This keeps frontend design untouched and only influences which tests run/assert strictly.
  try {
    // 1) Get a throwaway token (dev invite code assumed)
    const nickname = 'gs_' + Math.random().toString(36).slice(2, 8);
    const regResp = await fetch(`${api}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nickname, invite_code: process.env.E2E_INVITE_CODE || '5858' }),
    }).catch(() => null);

    if (!regResp || !regResp.ok) return;
    const regJson = await regResp.json().catch(() => ({}));
    const access = regJson?.access_token;
    const refresh = regJson?.refresh_token;
    if (!access) return;

    // Share tokens to tests if they want to reuse
    process.env.E2E_ACCESS_TOKEN = process.env.E2E_ACCESS_TOKEN || access;
    if (refresh) process.env.E2E_REFRESH_TOKEN = process.env.E2E_REFRESH_TOKEN || refresh;

    const authHeaders = { Authorization: `Bearer ${access}` };

    // 2) Stats parity readiness: /api/games/stats/me returns 200 and object
    // Do NOT enforce here to avoid premature failures; CI flips REQUIRE explicitly.
    try {
      const s = await fetch(`${api}/api/games/stats/me`, { headers: authHeaders });
      if (s.ok) {
        const data = await s.json().catch(() => null);
        if (data && typeof data === 'object') {
          process.env.E2E_PARITY_READY = process.env.E2E_PARITY_READY || '1';
        }
      }
    } catch {}

    // 3) Shop sync readiness: catalog has items
    if (!process.env.E2E_SHOP_SYNC) {
      try {
        const c = await fetch(`${api}/api/shop/catalog`, { headers: authHeaders });
        if (c.ok) {
          const catalog = await c.json().catch(() => null);
          const items = Array.isArray(catalog?.items) ? catalog.items : Array.isArray(catalog) ? catalog : [];
          if (items.length > 0) {
            process.env.E2E_SHOP_SYNC = '1';
          }
        }
      } catch {}
    }

    // 4) Realtime dev emit availability → mapping smoke enable
    if (!process.env.E2E_REALTIME_MAPPING) {
      try {
        const r = await fetch(`${api}/api/test/realtime/emit/stats_update`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...authHeaders },
          body: JSON.stringify({ stats: { ping: 1 } }),
        }).catch(() => null);
        if (r && r.status >= 200 && r.status < 300) {
          process.env.E2E_REALTIME_MAPPING = '1';
        }
      } catch {}
    }
  } catch {
    // best-effort; never fail setup due to auto-flagging
  }
};
