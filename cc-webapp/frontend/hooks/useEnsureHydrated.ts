"use client";

import { useEffect } from "react";
import { hydrateFromServer, useGlobalStore } from "@/store/globalStore";

// 마운트 시 프로필/밸런스/통계를 병렬 로드하고 ready flag를 설정
export function useEnsureHydrated() {
  const { dispatch, state } = useGlobalStore();
  useEffect(() => {
    if (!state.hydrated) {
      hydrateFromServer(dispatch);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
}
