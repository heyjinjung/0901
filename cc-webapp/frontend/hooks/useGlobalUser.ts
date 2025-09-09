// memoized selector 훅: 전역 프로필 일부를 메모이즈하여 불필요 리렌더 방지
"use client";

import { useMemo } from "react";
import { useGlobalStore } from "@/store/globalStore";

export function useGlobalUser() {
  const { state } = useGlobalStore();
  return state.profile;
}

export function useGlobalUserSelector<T>(selector: (p: any) => T, deps: any[] = []) {
  const { state } = useGlobalStore();
  const value = selector(state.profile);
  // 메모이즈: 선택된 값이 변경되지 않으면 같은 참조 반환
  // 주의: 프리미티브/얕은 비교 전제. 복합객체는 selector에서 안정 레퍼런스를 구성
  return useMemo(() => value, deps.length ? deps : [value]);
}

export function useUserGoldMemo() {
  const { state } = useGlobalStore();
  const gold = state.profile?.goldBalance ?? 0;
  return useMemo(() => gold, [gold]);
}
