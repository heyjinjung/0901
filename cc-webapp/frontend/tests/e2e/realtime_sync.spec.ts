import { test, expect } from '@playwright/test';

/**
 * E2E: 표준 WS 경로(`/api/realtime/sync`) 연결 시도 흔적이 존재하는지 간단 검증
 * 구현 세부가 숨겨져도, 에러 로그/경고 토스트/네트워크 요청 존재로 간접 확인
 */
test.describe('Realtime sync (placeholder)', () => {
  test.skip('connects to standard WS path', async () => {
    // 현재 구현은 /ws/updates 를 사용하므로 이 스펙은 보류
  });
});
