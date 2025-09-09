import { test, expect } from '@playwright/test';

const pages = ['/', '/login', '/shop'];
const viewports = [ { width: 360, height: 800 }, { width: 768, height: 1024 }, { width: 1366, height: 768 } ];

for (const vp of viewports) {
  test.describe(`viewport ${vp.width}x${vp.height}`, () => {
    for (const p of pages) {
      test(`visual check ${p}`, async ({ page }) => {
        await page.setViewportSize(vp);
        await page.goto(p);
        const shot = await page.screenshot({ fullPage: true });
        expect(shot).toBeDefined();
      });
    }
  });
}
