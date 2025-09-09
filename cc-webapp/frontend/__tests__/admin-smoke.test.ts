// Tiny smoke: just verifies admin pages are defined and importable in Next app

test('admin pages import', async () => {
  const stats = await import('../app/admin/stats/page');
  const campaigns = await import('../app/admin/campaigns/page');
  const shop = await import('../app/admin/shop/page');
  expect(stats).toBeTruthy();
  expect(campaigns).toBeTruthy();
  expect(shop).toBeTruthy();
});
