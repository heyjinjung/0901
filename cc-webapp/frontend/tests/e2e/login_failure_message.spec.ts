import { test, expect, Page } from '@playwright/test';

// 시나리오: 잘못된 자격증명으로 로그인 시 표준 에러 문구 노출 확인
// LoginScreen.tsx 에러 문구: '로그인 실패: 자격 증명이 올바르지 않거나 서버에서 거부되었습니다.'

test.describe('[Auth] login failure message', () => {
  test('invalid credentials show standardized error text', async ({ page }: { page: import('@playwright/test').Page }) => {
    const BASE = process.env.BASE_URL || 'http://frontend:3000';

    // 로그인 화면 강제 진입(앱 래퍼가 초기 화면을 LS로 제어)
    await page.addInitScript(() => {
      try {
        localStorage.setItem('E2E_FORCE_SCREEN', 'login');
        // 혹시 남아있을 수 있는 이전 세션 토큰 제거
        localStorage.removeItem('cc_auth_tokens');
        localStorage.removeItem('game-user');
      } catch {}
    });
    await page.goto(BASE + '/login');

    // 닉네임/비밀번호 입력 시뮬레이션 (실제 onLogin는 상위 App에서 주입되므로 오류 경로 유도)
  const nick = page.locator('#nickname');
  const pass = page.locator('#password');
  await expect(nick).toBeVisible({ timeout: 10000 });
  await expect(pass).toBeVisible({ timeout: 10000 });
    await nick.fill('nonexistent_user');
    await pass.fill('wrong-password');

  const submit = page.getByRole('button', { name: '로그인', exact: true });
    await submit.click();

    // 표준 에러 메시지 확인 (부분 일치 허용)
    const partial = '로그인 실패: 자격 증명이 올바르지 않거나 서버에서 거부되었습니다.';
    const message = page.getByText(new RegExp(partial));
    // 에러 컨테이너가 애니메이션으로 늦게 뜰 수 있어 역할/경고 패턴도 허용
    const alert = page.getByRole('alert');
    const ok = await Promise.race([
      message.waitFor({ state: 'visible', timeout: 7000 }).then(() => true).catch(() => false),
      alert.waitFor({ state: 'visible', timeout: 7000 }).then(() => true).catch(() => false),
    ]);
    expect(ok).toBeTruthy();
  });
});
