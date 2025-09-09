/*
 * Global Store (Context + Reducer)
 * - 서버 권위 프로필/밸런스 상태 보관
 * - 최소 스키마만 우선 도입(추후 확장)
 */
"use client";

import React, { createContext, useContext, useMemo, useReducer } from "react";
import { api } from "@/lib/unifiedApi";
import { normalizeGameStatsResponse } from "@/utils/gameStatsNormalizer";

export type GlobalUserProfile = {
    id: string | number;
    nickname: string;
    goldBalance: number;
    gemsBalance?: number;
    level?: number;
    xp?: number;
    // 게임 통계 필드들 추가
    experience_points?: number;
    daily_streak?: number;
    total_games_played?: number;
    total_games_won?: number;
    total_games_lost?: number;
    win_rate?: number;
    // 관리자 여부
    isAdmin?: boolean;
    is_admin?: boolean;
    updatedAt?: string;
    [k: string]: unknown;
};

// 인벤토리 아이템(느슨한 스키마; 서버 권위와 실시간 동기화 전제)
export type InventoryItem = {
    id: string;
    name: string;
    type?: string;
    rarity?: string;
    quantity?: number;
    value?: number;
    icon?: string;
    [k: string]: unknown;
};

type GlobalState = {
    // 권위 사용자/밸런스
    profile: GlobalUserProfile | null;
    balances?: { gold: number; gems?: number };
    // 준비 플래그
    hydrated: boolean;
    lastHydratedAt?: number;
    // 게임별 통계(키: 게임 식별자)
    gameStats?: Record<string, any>;
    // 인벤토리(가벼운 캐시; 서버와 불일치 시 서버값 우선)
    inventory?: InventoryItem[];
    // 스트릭/이벤트/알림(경량)
    streak?: Record<string, any>;
    events?: Record<string, any>;
    notifications?: Array<{ id: string; type: string; message: string; at: number }>;
    // 오류 상태(옵션)
    lastError?: { message: string; at: number } | null;
};

type Actions =
    | { type: "SET_PROFILE"; profile: GlobalUserProfile | null }
    | { type: "SET_HYDRATED"; value: boolean }
    | { type: "PATCH_BALANCES"; delta: { gold?: number; gems?: number } }
    | { type: "APPLY_REWARD"; award: { gold?: number; gems?: number } }
    | { type: "MERGE_PROFILE"; patch: Partial<GlobalUserProfile> & Record<string, unknown> }
    | { type: "MERGE_GAME_STATS"; game: string; delta: Record<string, any> }
    | { type: "APPLY_PURCHASE"; items: InventoryItem[]; replace?: boolean }
    | { type: "SET_ERROR"; error: { message: string; at: number } | null }
    | { type: "SET_BALANCES"; balances: { gold: number; gems?: number } }
    | { type: "SET_STREAK"; streak: Record<string, any> }
    | { type: "SET_EVENTS"; events: Record<string, any> }
    | { type: "SET_GAME_STATS"; gameStats: Record<string, any> }
    | { type: "PUSH_NOTIFICATION"; item: { id: string; type: string; message: string; at: number } };

const initialState: GlobalState = {
    profile: null,
    balances: { gold: 0, gems: 0 },
    hydrated: false,
    lastHydratedAt: undefined,
    gameStats: {},
    inventory: [],
    streak: {},
    events: {},
    notifications: [],
    lastError: null,
};

function reducer(state: GlobalState, action: Actions): GlobalState {
    switch (action.type) {
        case "SET_PROFILE":
            return { ...state, profile: action.profile, hydrated: true, lastHydratedAt: Date.now() };
    case "SET_HYDRATED":
            return { ...state, hydrated: action.value, lastHydratedAt: action.value ? Date.now() : state.lastHydratedAt };
        case "PATCH_BALANCES": {
            if (!state.profile) return state;
            const gold = state.profile.goldBalance ?? 0;
            const gems = (state.profile as any).gemsBalance ?? 0;
            return {
                ...state,
                profile: {
                    ...state.profile,
                    goldBalance: gold + (action.delta.gold ?? 0),
                    gemsBalance: gems + (action.delta.gems ?? 0),
                } as GlobalUserProfile,
        balances: { gold: (state.balances?.gold ?? gold) + (action.delta.gold ?? 0), gems: (state.balances?.gems ?? gems) + (action.delta.gems ?? 0) },
            };
        }
        case "APPLY_REWARD": {
            if (!state.profile) return state;
            const gold = state.profile.goldBalance ?? 0;
            const gems = (state.profile as any).gemsBalance ?? 0;
            const addGold = Number(action.award.gold ?? 0);
            const addGems = Number(action.award.gems ?? 0);
            return {
                ...state,
                profile: {
                    ...state.profile,
                    goldBalance: gold + (Number.isFinite(addGold) ? addGold : 0),
                    gemsBalance: gems + (Number.isFinite(addGems) ? addGems : 0),
                } as GlobalUserProfile,
        balances: { gold: (state.balances?.gold ?? gold) + (Number.isFinite(addGold) ? addGold : 0), gems: (state.balances?.gems ?? gems) + (Number.isFinite(addGems) ? addGems : 0) },
            };
        }
        case "MERGE_PROFILE": {
            if (!state.profile) {
                // If profile isn't set yet, create one from patch minimally
                return { ...state, profile: { goldBalance: 0, nickname: "", id: "unknown", ...(action.patch as any) } };
            }
            return { ...state, profile: { ...state.profile, ...(action.patch as any) } as GlobalUserProfile };
        }
        case "MERGE_GAME_STATS": {
            const current = state.gameStats || {};
            const prev = (current[action.game] as any) || {};

            const deepMergeNumericAdd = (a: any, b: any): any => {
                if (Array.isArray(a) && Array.isArray(b)) return [...a, ...b];
                if (typeof a === "number" && typeof b === "number") return a + b;
                if (a === undefined) return b;
                if (b === undefined) return a;
                if (typeof a === "object" && typeof b === "object") {
                    const out: Record<string, any> = { ...a };
                    for (const k of Object.keys(b)) {
                        out[k] = deepMergeNumericAdd((a as any)[k], (b as any)[k]);
                    }
                    return out;
                }
                return b; // 다른 타입은 최근 delta로 덮기
            };

            const mergedForGame = deepMergeNumericAdd(prev, action.delta);
            return { ...state, gameStats: { ...current, [action.game]: mergedForGame } };
        }
        case "APPLY_PURCHASE": {
            const current = state.inventory || [];
            if (action.replace) {
                return { ...state, inventory: [...action.items] };
            }
            // 동일 id는 수량 합산(없으면 append)
            const byId: Record<string, InventoryItem> = {};
            for (const it of current) byId[it.id] = { ...it };
            for (const it of action.items) {
                const prev = byId[it.id];
                if (prev) {
                    byId[it.id] = {
                        ...prev,
                        ...it,
                        quantity: (prev.quantity ?? 0) + (it.quantity ?? 0),
                    };
                } else {
                    byId[it.id] = { ...it } as InventoryItem;
                }
            }
            return { ...state, inventory: Object.values(byId) };
        }
        case "SET_ERROR":
            return { ...state, lastError: action.error };
        case "SET_BALANCES":
            return { ...state, balances: { ...action.balances }, profile: state.profile ? { ...state.profile, goldBalance: action.balances.gold, gemsBalance: action.balances.gems } as GlobalUserProfile : state.profile };
        case "SET_STREAK":
            return { ...state, streak: { ...action.streak } };
        case "SET_EVENTS":
            return { ...state, events: { ...action.events } };
        case "SET_GAME_STATS":
            return { ...state, gameStats: { ...action.gameStats } };
        case "PUSH_NOTIFICATION":
            return { ...state, notifications: [{ ...action.item }, ...(state.notifications || [])].slice(0, 50) };
        default:
            return state;
    }
}

type DispatchFn = (action: Actions) => void;
const StoreContext = createContext(null as unknown as { state: GlobalState; dispatch: DispatchFn } | null);

export function GlobalStoreProvider(props: { children?: React.ReactNode }) {
    const [state, dispatch] = useReducer(reducer, initialState);
    const value = useMemo(() => ({ state, dispatch }), [state]);
    return React.createElement((StoreContext as any).Provider, { value }, props.children as any);
}

export function useGlobalStore() {
    const ctx = useContext(StoreContext);
    if (!ctx) throw new Error("useGlobalStore must be used within GlobalStoreProvider");
    return ctx;
}

export function useGlobalProfile() {
    return useGlobalStore().state.profile;
}

export function useIsHydrated() {
    return useGlobalStore().state.hydrated;
}

// Action helpers
export function setProfile(dispatch: DispatchFn, profile: GlobalUserProfile | null) {
    dispatch({ type: "SET_PROFILE", profile });
}

export function setHydrated(dispatch: DispatchFn, value: boolean) {
    dispatch({ type: "SET_HYDRATED", value });
}

export function patchBalances(dispatch: DispatchFn, delta: { gold?: number; gems?: number }) {
    dispatch({ type: "PATCH_BALANCES", delta });
}

export function applyReward(dispatch: DispatchFn, award: { gold?: number; gems?: number }) {
    dispatch({ type: "APPLY_REWARD", award });
}

export function mergeProfile(dispatch: DispatchFn, patch: Partial<GlobalUserProfile> & Record<string, unknown>) {
    dispatch({ type: "MERGE_PROFILE", patch });
}

// 통계 병합(숫자는 누적, 배열은 concat, 객체는 재귀 병합)
export function mergeGameStats(dispatch: DispatchFn, game: string, delta: Record<string, any>) {
    dispatch({ type: "MERGE_GAME_STATS", game, delta });
}

// 인벤토리 적용(append 기본, replace=true 시 교체)
export function applyPurchase(dispatch: DispatchFn, items: InventoryItem[], options?: { replace?: boolean }) {
    dispatch({ type: "APPLY_PURCHASE", items, replace: options?.replace });
}

// 고수준 액션들(hydrate/reconcile)
export async function hydrateFromServer(dispatch: DispatchFn) {
    try {
        const [me, bal, stats] = await Promise.all([
            api.get("auth/me"),
            api.get("users/balance").catch(() => null),
            api.get("games/stats/me").catch(() => null),
        ]);
        const goldFromBalanceRaw = (bal as any)?.gold ?? (bal as any)?.gold_balance ?? (bal as any)?.cyber_token_balance ?? (bal as any)?.balance;
        const mapped = {
            id: me?.id ?? me?.user_id ?? "unknown",
            nickname: me?.nickname ?? me?.name ?? "",
            goldBalance: Number.isFinite(Number(goldFromBalanceRaw)) ? Number(goldFromBalanceRaw) : Number(me?.gold ?? me?.gold_balance ?? 0),
            gemsBalance: Number(me?.gems ?? me?.gems_balance ?? 0),
            level: me?.level ?? me?.battlepass_level ?? undefined,
            // XP/experience normalization
            xp: me?.experience_points ?? me?.experience ?? me?.xp ?? 0,
            experience_points: me?.experience_points ?? me?.experience ?? me?.xp ?? 0,
            maxExperience: me?.max_experience ?? me?.maxExperience ?? 1000,
            // daily streak normalization (server may use snake_case or camelCase)
            daily_streak: me?.daily_streak ?? me?.dailyStreak ?? me?.streak ?? 0,
            dailyStreak: me?.daily_streak ?? me?.dailyStreak ?? me?.streak ?? 0,
            updatedAt: new Date().toISOString(),
            ...me,
        } as GlobalUserProfile as any;
        const balances = { gold: mapped.goldBalance ?? 0, gems: (mapped as any).gemsBalance ?? 0 };
        setProfile(dispatch, mapped);
        dispatch({ type: "SET_BALANCES", balances });
        if (stats && typeof stats === 'object') {
            try { 
                console.log('[hydrateFromServer] 원본 게임 통계:', stats);
                // 백엔드 응답을 프론트엔드 형식으로 변환
                const normalizedStats = normalizeGameStatsResponse(stats);
                console.log('[hydrateFromServer] 정규화된 게임 통계:', normalizedStats);
                dispatch({ type: "MERGE_GAME_STATS", game: "_me", delta: normalizedStats }); 
                console.log('[hydrateFromServer] 게임 통계 스토어에 저장 완료');
            } catch (e) { 
                console.warn('게임 통계 처리 실패:', e);
            }
        } else {
            console.warn('[hydrateFromServer] 게임 통계 데이터 없음:', stats);
        }
    } catch (e:any) {
        dispatch({ type: "SET_ERROR", error: { message: e?.message || "hydrateFromServer failed", at: Date.now() } });
    } finally {
        setHydrated(dispatch, true);
    }
}

export async function reconcileBalance(dispatch: DispatchFn) {
    try {
        const bal = await api.get("users/balance");
        const gold = Number((bal as any)?.gold ?? (bal as any)?.gold_balance ?? (bal as any)?.cyber_token_balance ?? (bal as any)?.balance ?? 0);
        const gems = Number((bal as any)?.gems ?? (bal as any)?.gems_balance ?? 0);
        dispatch({ type: "SET_BALANCES", balances: { gold, gems } });
    } catch (e:any) {
        dispatch({ type: "SET_ERROR", error: { message: e?.message || "reconcileBalance failed", at: Date.now() } });
    }
}

export function getLastError(state: GlobalState) { return state.lastError; }
