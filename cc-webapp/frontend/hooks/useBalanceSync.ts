import { useCallback, useMemo, useRef, useState } from 'react';
import { api as unifiedApi, hasAccessToken } from '@/lib/unifiedApi';

type UserLike = { goldBalance?: number } | null | undefined;

interface UseBalanceSyncOptions {
  sharedUser?: UserLike;
  onUpdateUser?: (next: any) => void;
  onAddNotification?: (msg: string) => void;
}

interface UseBalanceSyncResult {
  lastBalance: number | null;
  loading: boolean;
  error: Error | null;
  reconcileBalance: () => Promise<number | null>;
  reconcileWith: (fetchedBalance: number | null | undefined) => void;
}

/**
 * 단일 권위 소스(/api/users/balance) 기반 GOLD 동기화 훅
 * - 컴포넌트에서 공용 user 상태를 업데이트하고, DEV에서 불일치 토스트를 표시합니다.
 * @deprecated 다음 릴리스에서 제거 예정. 전역 동기화 훅 useGlobalSync.syncBalance로 대체하세요.
 */
export function useBalanceSync(options: UseBalanceSyncOptions = {}): UseBalanceSyncResult {
  const { sharedUser, onUpdateUser, onAddNotification } = options;
  const [lastBalance, setLastBalance] = useState(null as number | null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null as Error | null);
  const warnedRef = useRef(false);

  const devMode = useMemo(() => {
    // @ts-ignore - Node 타입 미설치 환경 호환
    const env = typeof process !== 'undefined' ? process.env : { NODE_ENV: 'development' };
    return env.NODE_ENV !== 'production';
  }, []);

  const maybeNotifyMismatch = useCallback(
    (currentGold: number, fetchedGold: number) => {
      if (!devMode) return;
      const msg = `DEV: GOLD 불일치 감지 → ${currentGold} → ${fetchedGold} (users/balance 권위 반영)`;
      try {
        if (onAddNotification) onAddNotification(msg);
      } catch {}
      // 콘솔 경고는 1회만
      if (!warnedRef.current) {
        // eslint-disable-next-line no-console
        console.warn('[useBalanceSync]', msg);
        warnedRef.current = true;
      }
    },
    [devMode, onAddNotification]
  );

  const applyUpdateIfNeeded = useCallback(
    (fetchedGold: number | null | undefined) => {
      const safeFetched = Number(fetchedGold ?? 0);
      const currentGold = Number((sharedUser as any)?.goldBalance ?? 0);
      if (!Number.isNaN(safeFetched) && safeFetched !== currentGold) {
        if (onUpdateUser && sharedUser && typeof sharedUser === 'object') {
          const next = { ...(sharedUser as any), goldBalance: safeFetched };
          onUpdateUser(next);
          maybeNotifyMismatch(currentGold, safeFetched);
        }
      }
      setLastBalance(safeFetched);
    },
    [maybeNotifyMismatch, onUpdateUser, sharedUser]
  );

  const reconcileWith = useCallback(
    (fetchedBalance: number | null | undefined) => {
      try {
        applyUpdateIfNeeded(fetchedBalance);
      } catch (e: any) {
        setError(e instanceof Error ? e : new Error(String(e)));
      }
    },
    [applyUpdateIfNeeded]
  );

  const reconcileBalance = useCallback(async (): Promise<number | null> => {
    setLoading(true);
    setError(null);
    try {
      // 비로그인 상태면 서버 호출 스킵 (403 콘솔 노이즈 방지)
      if (!hasAccessToken()) {
        const currentGold = Number((sharedUser as any)?.goldBalance ?? 0);
        setLastBalance(currentGold);
        return currentGold;
      }
      const res: any = await unifiedApi.get('users/balance');
      const fetchedGold =
        (res && (res.cyber_token_balance ?? res.gold ?? res.tokens)) ?? 0;
      applyUpdateIfNeeded(fetchedGold);
      return Number(fetchedGold ?? 0);
    } catch (e: any) {
      const err = e instanceof Error ? e : new Error(String(e));
      setError(err);
      return null;
    } finally {
      setLoading(false);
    }
  }, [applyUpdateIfNeeded, sharedUser]);

  return { lastBalance, loading, error, reconcileBalance, reconcileWith };
}

export default useBalanceSync;
