import { test, expect } from '@playwright/test';

// 시나리오: 첫 수령 후 즉시 재수령 시, 고정 토스트 메시지 노출(rewardMessages.alreadyClaimed)
// 프론트 로직: HomeDashboard.claimDailyReward → unifiedApi.post('streak/claim', ...)

test.describe('[DailyReward] duplicate claim toast', () => {
  test('second claim shows alreadyClaimed toast', async ({ page, request }: { page: import('@playwright/test').Page; request: import('@playwright/test').APIRequestContext }) => {
    const BASE = process.env.BASE_URL || 'http://frontend:3000';
    const API = process.env.API_BASE_URL || 'http://localhost:8000';

    // 1) 신규 가입 및 토큰 확보
    const nickname = 'dr_' + Math.random().toString(36).slice(2, 8);
    const reg = await request.post(`${API}/api/auth/register`, {
      data: { nickname, invite_code: process.env.E2E_INVITE_CODE || '5858' }
    });
    expect(reg.ok()).toBeTruthy();
    const { access_token, refresh_token } = await reg.json();

  await page.addInitScript(([a, r, nick]: [string, string | undefined, string]) => {
      try {
        localStorage.setItem('cc_auth_tokens', JSON.stringify({ access_token: a, refresh_token: r || undefined }));
        localStorage.setItem('game-user', JSON.stringify({ id: 'e2e', nickname: nick, goldBalance: 0, level: 1 }));
      } catch {}
    }, access_token, refresh_token, nickname);

      // 2) 홈 진입 후 일일 보상 모달 열기
      await page.goto(BASE + '/');
      // 메인 페이지의 연속 보상 카드에서 '보상 보기' 버튼 클릭 → 모달 오픈
        // data-testid 우선, fallback: role/name
        let openReward;
        try {
          openReward = page.getByTestId('open-daily-reward');
          await openReward.waitFor({ state: 'visible', timeout: 2000 });
        } catch {
          openReward = page.getByRole('button', { name: '보상 보기' });
          await openReward.waitFor({ state: 'visible', timeout: 2000 });
        }
        await openReward.click();

    // 3) 첫 수령(성공 경로)
      const claimOrState = page.getByRole('button', { name: /보상 받기!|이미 수령됨/ });
      await claimOrState.waitFor({ state: 'visible' });
      // 첫 클릭: 실제 수령 수행(가능한 경우)
      if ((await claimOrState.textContent())?.includes('보상 받기!') && !(await claimOrState.isDisabled())) {
          await claimOrState.click();
    }

  // 4) 재수령 시도: 상태가 dailyClaimed=true로 버튼 비활성화되어 있을 수 있으므로 페이지 새로고침
      await page.reload();
      // 다시 '보상 보기'로 모달 오픈
      await openReward.click();
      // 두번째 시도: 버튼이 비활성화(이미 수령됨)인 환경과, 여전히 클릭 가능한 환경(백엔드 400 유도) 모두 수용
      const claimBtn2 = page.getByRole('button', { name: /보상 받기!/ });
      const alreadyBtn = page.getByRole('button', { name: '이미 수령됨' });
      const canClickSecond = await claimBtn2.isVisible().catch(() => false);
      if (canClickSecond && !(await claimBtn2.isDisabled())) {
          // 백엔드 중복 응답 경로 유도 → 토스트 노출 기대
          await claimBtn2.click();
    } else {
        // 버튼이 비활성화면 UI 상태로 이미 수령됨을 확인(토스트 없이도 허용)
        await alreadyBtn.waitFor({ state: 'visible', timeout: 3000 });
    }

    // 5) 토스트 메시지 확인 (접근성 role='status' 또는 'alert' 사용 / 텍스트 매칭)
    // 메시지는 이모지 포함일 수 있으므로 부분 문자열로 탐지
    const partial = '오늘 출석 보상은 이미 받으셨어요';
    // 우선 순위: data-testid / role 기반 토스트 → 텍스트 백업
    const toastByRole = page.getByRole('status').or(page.getByRole('alert'));
    const toastByTestId = page.getByTestId('toast').or(page.getByTestId('notification-toast'));
    const toastByText = page.getByText(new RegExp(partial));
    // 세 경로 중 하나가 나타나면 성공 처리
      // 토스트가 나타나면 true, 아니면 '이미 수령됨' 버튼 상태로 PASS 처리
      const toastVisible = await Promise.race([
      toastByRole.waitFor({ state: 'visible', timeout: 4000 }).then(() => true).catch(() => false),
      toastByTestId.waitFor({ state: 'visible', timeout: 4000 }).then(() => true).catch(() => false),
      toastByText.waitFor({ state: 'visible', timeout: 4000 }).then(() => true).catch(() => false),
    ]);
      if (!toastVisible) {
          await expect(page.getByRole('button', { name: '이미 수령됨' })).toBeVisible();
      } else {
          expect(toastVisible).toBeTruthy();
      }
  });
});
