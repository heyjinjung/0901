import { test, expect } from '@playwright/test';

// 간단한 회원가입/로그인/프로필 스모크 (실제 라우트 명세에 따라 조정 필요)
// 프론트 UI 폼 상호작용 대신 백엔드 API 직접 호출로 빠른 안정성 확보

test.describe('Auth + Balance Smoke', () => {
  const apiBase = process.env.API_BASE_URL || 'http://localhost:8000';
  const uid = 'smoke' + Date.now();

  test('register + profile + balance', async ({ request }) => {
    // 회원 등록 (간소화된 공개 엔드포인트)
    const reg = await request.post(`${apiBase}/api/auth/register`, {
      data: { nickname: uid, invite_code: process.env.E2E_INVITE_CODE || '5858' }
    });
    expect(reg.ok()).toBeTruthy();
    const regJson = await reg.json();
    const token = regJson.access_token as string;
    expect(token).toBeTruthy();

  // 프로필 확인 (표준 엔드포인트로 정렬)
  const profile = await request.get(`${apiBase}/api/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    expect(profile.ok()).toBeTruthy();
    const profileJson = await profile.json();
    expect(profileJson.id || profileJson.nickname).toBeTruthy();

    // 권위 잔액 소스 확인
    const balance = await request.get(`${apiBase}/api/users/balance`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    expect(balance.ok()).toBeTruthy();
    const balanceJson = await balance.json();
    expect(typeof balanceJson.cyber_token_balance).toBe('number');
  });
});
