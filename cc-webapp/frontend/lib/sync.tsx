import React, { useEffect, useContext } from 'react';
import { api, API_ORIGIN } from './unifiedApi';
import {
  useGlobalStore,
  reconcileBalance,
  applyReward as storeApplyReward,
} from '@/store/globalStore';

// hydrate profile + balances + stats
export async function hydrateProfile(dispatch: any) {
  try {
    const [profileRes, balanceRes, statsRes] = await Promise.all([
      api.get('auth/me').catch(() => null),
      api.get('users/balance').catch(() => null),
      api.get('games/stats/me').catch(() => null),
    ]);

    if (profileRes) dispatch({ type: 'SET_USER', user: profileRes });
    if (balanceRes) dispatch({ type: 'SET_BALANCES', balances: balanceRes });
    if (statsRes) dispatch({ type: 'MERGE_GAME_STATS', stats: statsRes });
  } catch (e) {
    // ignore
    // console.warn('[sync] hydrateProfile failed', e)
  }
}

export function EnsureHydrated(props: { children?: React.ReactNode }) {
  const { state, dispatch } = useGlobalStore();
  useEffect(() => {
    if (state.ready) return;
    hydrateProfile(dispatch).finally(() => {
      dispatch({ type: 'SET_READY', ready: true });
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return <>{props.children ?? null}</>;
}

function toWs(origin: string) {
  return origin.replace(/^http/i, 'ws');
}

export function RealtimeSyncProvider(props: { children?: React.ReactNode }) {
  const { state, dispatch } = useGlobalStore();

  useEffect(() => {
    if (typeof window === 'undefined') return;
    let ws: WebSocket | null = null;
    let closed = false;

    const url = `${toWs(API_ORIGIN)}/ws/updates`;
    try {
      ws = new WebSocket(url);
      ws.onopen = () => console.log('[sync] WS connected', url);
      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data);
          const type = msg?.type;
          const payload = msg?.data || msg?.payload || {};
          const targetId = payload?.user_id ?? payload?.id ?? payload?.target_user_id;

          switch (type) {
            case 'profile_update':
              if (targetId && state.user?.id && String(targetId) === String(state.user.id)) {
                // if profile_update targets current user, reconcile
                reconcileBalance(dispatch);
              } else {
                hydrateProfile(dispatch);
              }
              window.dispatchEvent(
                new CustomEvent('app:notification', {
                  detail: { type: 'profile_update', message: '프로필 업데이트', payload },
                })
              );
              break;
            case 'purchase_update':
              if (
                targetId &&
                state.user?.id &&
                String(targetId) === String(state.user.id) &&
                payload?.new_balance
              ) {
                dispatch({ type: 'SET_BALANCES', balances: payload.new_balance });
              } else {
                hydrateProfile(dispatch);
              }
              window.dispatchEvent(
                new CustomEvent('app:notification', {
                  detail: { type: 'purchase_update', message: '구매 상태 변경', payload },
                })
              );
              break;
            case 'reward_granted':
              if (targetId && state.user?.id && String(targetId) === String(state.user.id)) {
                const r: any = payload?.reward || payload;
                if ((r?.awarded_gold || r?.gold) && typeof storeApplyReward === 'function') {
                  (storeApplyReward as any)(dispatch as any, {
                    gold: Number(r.awarded_gold ?? r.gold ?? 0),
                    gems: Number(r.awarded_gems ?? r.gems ?? 0),
                  });
                } else {
                  hydrateProfile(dispatch);
                }
              }
              window.dispatchEvent(
                new CustomEvent('app:notification', {
                  detail: { type: 'reward_granted', message: '보상 수령', payload },
                })
              );
              break;
            case 'game_update':
              if (payload?.stats) dispatch({ type: 'MERGE_GAME_STATS', stats: payload.stats });
              break;
            default:
              break;
          }
        } catch (e) {
          /* ignore */
        }
      };
      ws.onclose = () => {
        if (!closed) {
          setTimeout(() => {
            if (!closed) hydrateProfile(dispatch);
          }, 1500);
        }
      };
      ws.onerror = () => {
        ws?.close();
      };
    } catch (e) {
      console.warn('[sync] WS init failed', e);
    }

    return () => {
      closed = true;
      try {
        ws?.close();
      } catch {}
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.user?.id]);

  return <>{props.children ?? null}</>;
}

// uuid helper
function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export async function withReconcile<T>(
  dispatch: any,
  serverCall: (idemKey: string) => Promise<T>,
  options: { reconcile?: boolean } = { reconcile: true }
) {
  const idem = uuidv4();
  try {
    const res = await serverCall(idem);
    return res;
  } finally {
    if (options.reconcile !== false) {
      try {
        await reconcileBalance(dispatch);
      } catch {}
    }
  }
}

export function withIdempotency(headers: Record<string, string> = {}, key?: string) {
  const out = { ...headers };
  if (!out['X-Idempotency-Key']) out['X-Idempotency-Key'] = key || uuidv4();
  return out;
}

export async function postWithIdemAndReconcile(
  dispatch: any,
  path: string,
  body?: any,
  opts: any = {}
) {
  const headers = withIdempotency(opts.headers || {}, opts.idemKey);
  return withReconcile(dispatch, () => api.post(path, body, { ...opts, headers }));
}

export function useWithReconcile() {
  const { dispatch } = useGlobalStore();
  return (serverCall: (idemKey: string) => Promise<any>, opts?: any) => {
    if (!dispatch) throw new Error('useWithReconcile requires GlobalStoreProvider');
    return withReconcile(dispatch, serverCall, opts);
  };
}
