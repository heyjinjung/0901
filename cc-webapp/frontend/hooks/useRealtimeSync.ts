"use client";

import { useEffect, useRef } from "react";
import { useRealtimeSync as useWSContext } from "@/contexts/RealtimeSyncContext";
import { useGlobalStore, applyReward, mergeGameStats, applyPurchase, reconcileBalance } from "@/store/globalStore";

// WS 연결/재연결/토큰 교체 처리, 이벤트→store 액션 매핑
export function useRealtimeSync() {
  const ws = useWSContext();
  const { dispatch } = useGlobalStore();
  const boundRef = useRef(false);

  useEffect(() => {
    if (boundRef.current) return;
    boundRef.current = true;

    // RealtimeSyncContext에서 상태 변화가 있으면 필요한 store 액션 트리거
    const unsub = setInterval(() => {
      const s = ws.state;
      // 최근 보상 → applyReward 적용 후 최종 reconcile은 외부(액션 후)에서 별도 수행
      const last = s.recent_rewards[0];
      if (last) {
        const g = Number((last.reward_data as any)?.awarded_gold ?? (last.reward_data as any)?.gold ?? 0);
        if (Number.isFinite(g) && g !== 0) {
          applyReward(dispatch, { gold: g });
        }
      }
      // 구매 진행/완료는 서버 프로필 이벤트 혹은 balance API로 정합화
      if (s.purchase.last_updated) {
        // 가벼운 재조정 트리거(스로틀은 RealtimeSyncProvider/서버에서 조절)
        reconcileBalance(dispatch).catch(()=>{});
      }
      // 통계는 stats_update 케이스에서 병합
      const keys = Object.keys(s.stats || {});
      if (keys.length) {
        for (const k of keys) {
          mergeGameStats(dispatch, k, (s.stats as any)[k]?.data || {});
        }
      }
    }, 1500);

    return () => clearInterval(unsub);
  }, [ws, dispatch]);

  return ws;
}
