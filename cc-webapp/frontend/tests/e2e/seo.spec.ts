import { test, expect } from '@playwright/test';

const pages = ['/', '/login', '/shop'];

test.describe('SEO smoke', () => {
  for (const p of pages) {
    test(`${p} should have title and meta description`, async ({ page }) => {
      await page.goto(p);
      const title = await page.title();
      const desc = await page.locator('head meta[name="description"]').getAttribute('content');
      expect(title.length).toBeGreaterThan(5);
      expect(desc && desc.length > 10).toBeTruthy();
    });
  }
});
