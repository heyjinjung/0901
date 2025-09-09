/**
 * 토큰 스토리지 유틸리티
 * JWT 토큰 관리를 위한 함수들
 */

// 로컬 스토리지에 저장된 토큰 키 (신규 통합 번들)
const TOKEN_KEY = 'cc_auth_tokens';
// 레거시 단일 키 (이후 제거 예정: 2025-09-01 이후 쓰기 중단 계획)
const LEGACY_ACCESS_KEY = 'cc_access_token';
const LEGACY_ACCESS_EXP_KEY = 'cc_access_exp';

/**
 * 레거시 키가 존재하고 번들 키가 없을 경우 자동 마이그레이션.
 * - access_token 필수, refresh_token 은 알 수 없으므로 null 유지.
 * - 마이그레이션 후 콘솔 경고 한 번 출력.
 * - 예외 발생 시 조용히 무시(안전성 최우선).
 */
function migrateLegacyIfNeeded() {
  if (typeof window === 'undefined') return null;
  try {
    const bundle = localStorage.getItem(TOKEN_KEY);
    if (bundle) return JSON.parse(bundle); // 이미 번들 존재

    const legacyAccess = localStorage.getItem(LEGACY_ACCESS_KEY);
    if (!legacyAccess) return null; // 마이그레이션 필요 없음

    // refresh 토큰은 알 수 없으므로 null 설정 (향후 강제 재로그인 트리거 가능)
    const migrated = { access_token: legacyAccess, refresh_token: null };
    localStorage.setItem(TOKEN_KEY, JSON.stringify(migrated));
    console.warn('[tokenStorage] 레거시 토큰 자동 마이그레이션 수행 (refresh_token=null). 2025-09-15 이후 레거시 키 제거 예정.');
    return migrated;
  } catch (e) {
    console.error('[tokenStorage] 레거시 마이그레이션 실패:', e);
    return null;
  }
}

/**
 * 토큰 인터페이스 정의
 * @typedef {Object} AuthTokens
 * @property {string} access_token - 액세스 토큰
 * @property {string} refresh_token - 리프레시 토큰
 */

/**
 * 로컬 스토리지에서 토큰 가져오기
 * @returns {AuthTokens|null} 토큰 객체 또는 null
 */
export const getTokens = () => {
  if (typeof window === 'undefined') return null;
  try {
    let tokensStr = localStorage.getItem(TOKEN_KEY);
    if (!tokensStr) {
      // 번들이 없으면 레거시 마이그레이션 시도
      const migrated = migrateLegacyIfNeeded();
      if (migrated) return migrated;
      return null;
    }
    const parsedTokens = JSON.parse(tokensStr);
    return parsedTokens;
  } catch (error) {
    console.error('토큰 가져오기 오류:', error);
    return null;
  }
};

/**
 * 액세스 토큰 가져오기
 * @returns {string|null} 액세스 토큰 또는 null
 */
export const getAccessToken = () => {
  const tokens = getTokens();
  const accessToken = tokens?.access_token || null;
  return accessToken;
};

/**
 * 로컬 스토리지에 토큰 저장하기
 * @param {Object} tokens - 저장할 토큰 객체 {access_token, refresh_token}
 */
export const setTokens = (tokens) => {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
    // 레거시 키 동기화 (점진적 제거 전까지 유지) - 2025-09-01 이후 제거 예정
    if (tokens?.access_token) {
      try { localStorage.setItem(LEGACY_ACCESS_KEY, tokens.access_token); } catch { }
      // 미들웨어용 쿠키 설정
      try { 
        document.cookie = `auth_token=${tokens.access_token}; path=/; max-age=86400; SameSite=Lax`;
      } catch { }
    }
  } catch (error) {
    console.error('토큰 저장 오류:', error);
  }
};

/**
 * 로컬 스토리지에서 토큰 삭제하기
 */
export const clearTokens = () => {
  if (typeof window === 'undefined') return;

  try {
    localStorage.removeItem(TOKEN_KEY);
    // 레거시 키도 삭제
    localStorage.removeItem(LEGACY_ACCESS_KEY);
    localStorage.removeItem(LEGACY_ACCESS_EXP_KEY);
    // 쿠키도 삭제
    document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
  } catch (error) {
    console.error('토큰 삭제 오류:', error);
  }
};

/**
 * 토큰이 유효한지 확인하기
 * @returns {boolean} 토큰 유효 여부
 */
export const isAuthenticated = () => {
  const tokens = getTokens();
  if (!tokens?.access_token) return false;

  try {
    // JWT 토큰의 만료 시간 확인
    const payload = JSON.parse(atob(tokens.access_token.split('.')[1]));
    return payload.exp > Math.floor(Date.now() / 1000);
  } catch (error) {
    console.error('토큰 검증 오류:', error);
    return false;
  }
};
