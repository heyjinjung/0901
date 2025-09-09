/**
 * @jest-environment jsdom
 */
// NOTE: Next 15 App Router 사용으로 해당 경로가 더 이상 존재하지 않음.
// 유효성 로직은 별도 유틸로 이전 예정. 당분간 스킵 처리.
// import { validateAuthOnBoot } from '../../frontend/src/pages/_app';
const validateAuthOnBoot = async () => { };

// tokenStorage key used in app
const TOKEN_KEY = 'cc_auth_tokens';

describe.skip('App boot auth validation (skipped: App Router migration)', () => {
  beforeEach(() => {
    // clear localStorage & reset fetch
    localStorage.clear();
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  test('valid token (200) should not clear tokens', async () => {
    localStorage.setItem(TOKEN_KEY, JSON.stringify({ access_token: 'valid.jwt.token' }));
    global.fetch.mockResolvedValue({ status: 200 });

  // call the exported validator directly (no reload)
  await validateAuthOnBoot({ doReload: false });

  expect(localStorage.getItem(TOKEN_KEY)).not.toBeNull();
  });

  test('invalid token (401) should clear tokens and reload', async () => {
    localStorage.setItem(TOKEN_KEY, JSON.stringify({ access_token: 'bad.jwt.token' }));
    global.fetch.mockResolvedValue({ status: 401 });

  await validateAuthOnBoot({ doReload: false });

  expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
  });
});
