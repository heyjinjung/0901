/*
 Global setup waits for backend and frontend to be reachable to avoid early ECONNREFUSED
 inside containerized runs where Playwright may start before services are ready.
*/
import http from 'http';

function wait(ms: number) { return new Promise(res => setTimeout(res, ms)); }

async function waitForHttpOk(url: string, timeoutMs: number): Promise<void> {
  const started = Date.now();
  let lastErr: any;
  while (Date.now() - started < timeoutMs) {
    try {
      await new Promise<void>((resolve, reject) => {
        const req = http.get(url, (res) => {
          // Some endpoints may 404; treat any response as readiness if status < 500
          if (res.statusCode && res.statusCode < 500) {
            res.resume();
            resolve();
          } else {
            lastErr = new Error(`Status ${res.statusCode}`);
            res.resume();
            reject(lastErr);
          }
        });
        req.on('error', reject);
        req.setTimeout(3000, () => {
          req.destroy(new Error('timeout'));
        });
      });
      return; // success
    } catch (e) {
      lastErr = e;
    }
    await wait(1000);
  }
  throw lastErr ?? new Error(`Timeout waiting for ${url}`);
}

export default async function globalSetup() {
  const api = process.env.API_BASE_URL || 'http://backend:8000';
  const web = process.env.BASE_URL || 'http://frontend:3000';

  // Prefer explicit health endpoint for backend
  await waitForHttpOk(`${api}/health`, 60_000).catch(async () => {
    // Fallback to root if /health is not present
    await waitForHttpOk(api, 30_000);
  });

  // Frontend root should be accessible
  await waitForHttpOk(web, 60_000);
}
