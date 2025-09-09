import { useCallback, useEffect, useState } from 'react';
import { api as unifiedApi } from '@/lib/unifiedApi';
import { useWithReconcile } from '@/lib/sync';
import { applyReward, useGlobalStore } from '@/store/globalStore';
import { getTokens } from '../utils/tokenStorage';

export interface EventItem {
  id: number;
  title: string;
  description?: string;
  end_date?: string;
  user_participation?: {
    joined: boolean;
    progress: number;
    completed: boolean;
    claimed: boolean;
  } | null;
  [k: string]: any;
}

interface UseEventsOptions { autoLoad?: boolean }
interface UseEventsReturn {
  events: EventItem[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  join: (eventId: number) => Promise<void>;
  claim: (eventId: number) => Promise<any>;
  updateProgress: (eventId: number, progress: number) => Promise<void>;
  find: (id: number) => EventItem | undefined;
}

const cache = {
  items: [] as EventItem[],
  loading: false,
  error: null as string | null,
  lastLoadedAt: 0,
  listeners: new Set<() => void>(),
};

const notify = () => { cache.listeners.forEach(l => { try { l(); } catch { } }); };

async function loadEvents() {
  if (cache.loading) return;
  // 토큰 없으면 비로그인 상태이므로 호출 스킵 (403 Forbidden (no token) 콘솔 노이즈 방지)
  let hasToken = false;
  try {
    const tokens = getTokens();
    hasToken = !!tokens?.access_token;
  } catch { /* ignore */ }
  cache.loading = true; cache.error = null; notify();
  try {
    let data: any = null;
    if (hasToken) {
      data = await unifiedApi.get('events/');
    } else {
      // 비로그인 사용자를 위해 최소 공개 리스트 시도 (서버 인증 의존 → 실패시 무시)
      try {
        data = await unifiedApi.get('events/'); // 401/403 발생시 catch에서 무시
      } catch (e) {
        data = [];
      }
    }
    if (Array.isArray(data)) {
      cache.items = data as EventItem[];
      cache.lastLoadedAt = Date.now();
    } else {
      cache.error = '이벤트 응답 형식 오류';
    }
  } catch (e: any) {
    cache.error = e?.message || '이벤트 로드 실패';
  } finally { cache.loading = false; notify(); }
}

export function useEvents(opts: UseEventsOptions = {}): UseEventsReturn {
  const { autoLoad = true } = opts;
  const [, setVer] = useState(0);
  const { dispatch } = useGlobalStore();
  const withReconcile = useWithReconcile();
  useEffect(() => { const f = () => setVer((v: number) => v + 1); cache.listeners.add(f); return () => { cache.listeners.delete(f); }; }, []);
  useEffect(() => {
    if (!autoLoad) return;
    const tokens = getTokens();
    if (!tokens?.access_token) return; // 비로그인: 이벤트 로딩 skip
    if (!cache.lastLoadedAt || Date.now() - cache.lastLoadedAt > 30_000) loadEvents();
  }, [autoLoad]);

  const refresh = useCallback(async () => {
    const tokens = getTokens();
    if (!tokens?.access_token) return; // 비로그인 상태에서는 refresh 무시
    await loadEvents();
  }, []);
  const updateOne = (id: number, mut: (e: EventItem) => EventItem) => { cache.items = cache.items.map(e => e.id === id ? mut(e) : e); notify(); };
  const join = useCallback(async (eventId: number) => {
    const res = await unifiedApi.post('events/join', { event_id: eventId });
    updateOne(eventId, e => ({ ...e, user_participation: { joined: true, progress: res?.progress ?? 0, completed: !!res?.completed, claimed: !!res?.claimed_rewards } }));
  }, []);
  const claim = useCallback(async (eventId: number) => {
    const res = await withReconcile(async (idemKey: string) =>
      unifiedApi.post(`events/claim/${eventId}`, {}, { headers: { 'X-Idempotency-Key': idemKey } })
    );
    updateOne(eventId, e => ({ ...e, user_participation: { ...(e.user_participation || { joined: true, progress: 0, completed: true, claimed: false }), claimed: true } }));
    try {
      const awarded = (res as any)?.awarded_gold ?? (res as any)?.rewards?.gold ?? (res as any)?.gold;
      if (typeof awarded === 'number' && Number.isFinite(awarded) && awarded !== 0) {
        applyReward(dispatch, { gold: Number(awarded) });
      }
    } catch { /* noop */ }
    return res;
  }, []);
  const updateProgress = useCallback(async (eventId: number, progress: number) => {
    const res = await unifiedApi.put(`events/progress/${eventId}`, { progress });
    updateOne(eventId, e => ({ ...e, user_participation: { joined: true, progress: res?.progress ?? progress, completed: !!res?.completed, claimed: !!res?.claimed_rewards } }));
  }, []);
  const find = useCallback((id: number) => cache.items.find(e => e.id === id), []);
  return { events: cache.items, loading: cache.loading, error: cache.error, refresh, join, claim, updateProgress, find };
}

export default useEvents;
