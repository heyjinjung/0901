import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

const pages = ['/', '/login', '/shop'];
const viewports = [ { width: 360, height: 800 }, { width: 768, height: 1024 }, { width: 1366, height: 768 } ];

test.describe('accessibility checks', () => {
  for (const page of pages) {
    test(`${page} should have no critical axe violations`, async ({ page: pwPage }) => {
      await pwPage.goto(page);
      const accessibilityScanResults = await new AxeBuilder({ page: pwPage }).analyze();
      const violations = accessibilityScanResults.violations.filter(v => v.impact === 'critical' || v.impact === 'serious');
      expect(violations.length, `axe violations found: ${JSON.stringify(violations, null, 2)}`).toBe(0);
    });
  }
});
