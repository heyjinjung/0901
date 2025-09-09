import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '@/lib/unifiedApi';

/**
 * useDashboard
 * - /api/dashboard 통합 응답 fetch
 * - 1초(TTL_MS) 내 중복 호출 dedupe
 * - invalidate() 호출로 강제 재갱신
 * @deprecated 다음 릴리스에서 제거 예정. 전역 스토어 셀렉터(useGlobalStore)와 useGameStats/useGlobalSync 조합으로 대체하세요.
 */

interface DashboardData {
  [k: string]: any; // 추후 타입 강화 예정
}

const TTL_MS = 1000;

export function useDashboard(auto = true) {
  const [data, setData] = useState(null as DashboardData | null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null as string | null);
  const lastFetchedRef = useRef(0 as number);
  const inFlightRef = useRef(null as Promise<any> | null);

  const load = useCallback(async () => {
    const now = Date.now();
    if (inFlightRef.current) return inFlightRef.current;
    if (now - lastFetchedRef.current < TTL_MS && data) return data;

    setLoading(true); setError(null);
    const p = api.get('dashboard').then((res) => {
      lastFetchedRef.current = Date.now();
      setData(res);
      return res;
    }).catch((e: any) => {
      setError(e.message || 'dashboard load failed');
      throw e;
    }).finally(() => {
      setLoading(false);
      inFlightRef.current = null;
    });
    inFlightRef.current = p;
    return p;
  }, [data]);

  const invalidate = useCallback(() => {
    lastFetchedRef.current = 0;
  }, []);

  useEffect(() => { if (auto) { load(); } }, [auto, load]);

  return { data, loading, error, reload: load, invalidate }; 
}

export default useDashboard;
