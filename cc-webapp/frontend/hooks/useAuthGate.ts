import { useEffect, useState } from 'react';
import { getTokens } from '../utils/tokenStorage';

/**
 * 공통 Auth Gate 훅
 * - 클라이언트 마운트 후 한 번 토큰 존재 검사 (만료 여부는 별도 처리 필요 시 확장)
 * - isReady: 검사 완료 여부
 * - authenticated: access_token 존재 여부
 */
export function useAuthGate() {
  const [isReady, setIsReady] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    if (isReady) return; // 1회만
    try {
      const tokens = getTokens();
      setAuthenticated(!!tokens?.access_token);
    } catch {
      setAuthenticated(false);
    } finally {
      setIsReady(true);
    }
  }, [isReady]);

  return { isReady, authenticated };
}

export default useAuthGate;
