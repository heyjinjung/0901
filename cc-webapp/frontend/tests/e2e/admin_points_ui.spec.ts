import { test, expect } from '@playwright/test';

test.describe('Admin Points UI smoke', () => {
  test('page renders and form validates inputs', async ({ page }: { page: import('@playwright/test').Page }) => {
    // 단순 렌더 확인(권한 요구 UI 라우팅은 우회, 페이지 접근만 체크)
    await page.goto('/admin/points');
    await page.waitForLoadState('domcontentloaded');

    // 필드 존재 확인(가드 처리): 권한 가드/리다이렉트 환경에서는 필드 미노출 가능 → 그 경우 안내 텍스트 확인 후 테스트 종료
    const userInput = page.locator('#user_id');
    const amountInput = page.locator('#amount');
    const memoInput = page.locator('#memo');
    const submit = page.getByRole('button', { name: /포인트 지급|지급 중/i });

    const formVisible = await userInput.first().isVisible().catch(() => false);
    if (!formVisible) {
      // 비관리자 guard 배너 data-testid 명시적 확인
      const guardBanner = page.getByTestId('admin-guard-banner');
      await expect(guardBanner).toBeVisible();
      test.fixme(true, 'Admin Points page guarded; skipping UI form assertions in non-admin context');
      return;
    }

    await expect(userInput).toHaveCount(1);
    await expect(amountInput).toHaveCount(1);
    await expect(memoInput).toHaveCount(1);

    // 기본적으로 비활성(입력 전)
    await expect(submit).toBeDisabled();

    // 유효하지 않은 값 → 여전히 비활성
    await userInput.fill('abc');
    await amountInput.fill('-10');
    await expect(submit).toBeDisabled();

    // 유효 값 입력 → 활성화 기대
    await userInput.fill('123');
    await amountInput.fill('50');
    await expect(submit).toBeEnabled();
  });
});
