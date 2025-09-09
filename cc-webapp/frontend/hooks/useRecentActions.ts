import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '@/lib/unifiedApi';

export interface RecentAction {
  id: number;
  user_id: number;
  action_type: string;
  created_at: string;
  action_data?: Record<string, any> | null;
}

/**
 * useRecentActions
 * - 특정 사용자 최근 액션 목록 로드
 * - TTL 내 중복 호출 방지(dedupe)
 */
export function useRecentActions(userId?: number, limit = 10, auto = true) {
  const [actions, setActions] = useState(null as RecentAction[] | null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null as string | null);
  const lastFetchedRef = useRef(0);
  const inFlightRef = useRef(null as Promise<any> | null);

  const TTL_MS = 1000; // 1초 dedupe

  const load = useCallback(async () => {
    if (!userId || userId <= 0) return null;
    const now = Date.now();
    if (inFlightRef.current) return inFlightRef.current;
    if (now - lastFetchedRef.current < TTL_MS && actions) return actions;

    setLoading(true); setError(null);
    const p = api
      .get(`actions/recent/${userId}`)
      .then((res) => {
        lastFetchedRef.current = Date.now();
        const list = Array.isArray(res) ? (res as RecentAction[]) : [];
        setActions(limit > 0 ? list.slice(0, limit) : list);
        return list;
      })
      .catch((e: any) => {
        setError(e?.message || 'recent actions load failed');
        throw e;
      })
      .finally(() => {
        setLoading(false);
        inFlightRef.current = null;
      });
    inFlightRef.current = p;
    return p;
  }, [userId, limit, actions]);

  const reload = useCallback(() => {
    lastFetchedRef.current = 0;
    return load();
  }, [load]);

  useEffect(() => {
    if (auto) {
      load();
    }
  }, [auto, load]);

  return { actions, loading, error, reload };
}

export default useRecentActions;
