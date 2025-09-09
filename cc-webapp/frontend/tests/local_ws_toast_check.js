const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  try {
    const base = process.env.BASE_URL || 'http://localhost:3000';
    console.log('Opening', base);
    await page.goto(base, { waitUntil: 'networkidle' });

    // Ensure ToastProvider is mounted
    await page.waitForTimeout(500);

    // Function to dispatch notification event
    const dispatch = async (payload) => {
      await page.evaluate((p) => window.dispatchEvent(new CustomEvent('app:notification', { detail: p })), payload);
    };

    // First dispatch: should show toast
    await dispatch({ message: 'E2E TEST TOAST', type: 'info' });
    // wait for toast node to appear
    const toastSelector = 'text=E2E TEST TOAST';
    const found = await page.waitForSelector(toastSelector, { timeout: 3000 }).then(() => true).catch(() => false);
    console.log('First toast found:', found);
    if (!found) throw new Error('Toast not found after first dispatch');

    // Dispatch duplicate within 1s: should be suppressed
    await dispatch({ message: 'E2E TEST TOAST', type: 'info' });
    // short wait then count occurrences
    await page.waitForTimeout(500);
    const occurrences = await page.$$eval("text=E2E TEST TOAST", els => els.length);
    console.log('Occurrences after duplicate:', occurrences);
    if (occurrences > 1) throw new Error('Duplicate toast not suppressed');

    // Dispatch after 2s: should show again
    await page.waitForTimeout(1600);
    await dispatch({ message: 'E2E TEST TOAST', type: 'info' });
    const occurrences2 = await page.$$eval("text=E2E TEST TOAST", els => els.length);
    console.log('Occurrences after spaced dispatch:', occurrences2);
    if (occurrences2 < 1) throw new Error('Toast missing after spaced dispatch');

    console.log('PASS: Toast appeared and duplicate suppression worked');
  } catch (e) {
    console.error('FAIL:', e && e.message);
    process.exitCode = 2;
  } finally {
    await browser.close();
  }
})();
