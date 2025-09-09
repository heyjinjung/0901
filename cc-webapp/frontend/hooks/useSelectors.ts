// 전역 스토어 셀렉터 훅: 컴포넌트는 로컬 user state 대신 이 훅만 사용
// 주의: 로컬 user 객체를 임의 변형하지 말 것. 항상 전역 스토어 업데이트/withReconcile 사용.
"use client";

import { useMemo } from "react";
import { useGlobalProfile, useGlobalStore } from "@/store/globalStore";
import { useGlobalTotalGames } from "./useGameStats";

export function useUserProfile() {
	// null 가능성 유지: 비로그인/미하이드레이트 상태 처리
	return useGlobalProfile();
}

export function useUserGold() {
	const p = useGlobalProfile();
	return p?.goldBalance ?? 0;
}

export function useUserLevel() {
	const p = useGlobalProfile();
	// level 또는 experience_points 기반 레벨 계산
	return (p as any)?.level ?? Math.floor(((p as any)?.experience_points ?? 0) / 500) + 1;
}

export function useIsAdmin() {
	const p = useGlobalProfile() as any;
	return !!p?.isAdmin || !!p?.is_admin;
}

export function useUserSummary() {
	const p = useGlobalProfile() as any;
	const { state } = useGlobalStore();
	const globalTotalGames = useGlobalTotalGames();
	
	// 전역 게임 통계에서 승리수와 연승수 계산
	const gameStats = state?.gameStats || {};
	const allStatsEntries = Object.values(gameStats);
	
	// 각 게임별 승리수 합계 계산
	const totalWins = useMemo(() => {
		return allStatsEntries.reduce((total: number, entry: any) => {
			const normalizedEntry = entry && typeof entry === 'object' 
				? ('data' in entry && entry.data ? entry.data : entry)
				: {};
			const wins = normalizedEntry?.total_wins ?? normalizedEntry?.wins ?? normalizedEntry?.totalWins ?? 0;
			return total + (typeof wins === 'number' && !Number.isNaN(wins) ? wins : 0);
		}, 0);
	}, [allStatsEntries]);

	// 현재 연승수 계산 (가장 높은 값 사용)
	const currentWinStreak = useMemo(() => {
		const streaks = allStatsEntries.map((entry: any) => {
			const normalizedEntry = entry && typeof entry === 'object' 
				? ('data' in entry && entry.data ? entry.data : entry)
				: {};
			return normalizedEntry?.current_win_streak ?? normalizedEntry?.currentWinStreak ?? normalizedEntry?.winStreak ?? 0;
		});
		return Math.max(0, ...streaks);
	}, [allStatsEntries]);

	// 연속보상 경험치 반영: streak에서 받은 포인트를 경험치에 합산
	const streakRewardXp = (() => {
		const streak = state?.streak || {};
		// streak.reward_points 또는 streak.xp_reward 등 다양한 필드 지원
		const xp = streak.reward_points ?? streak.xp_reward ?? streak.xp ?? 0;
		return typeof xp === 'number' && xp > 0 ? xp : 0;
	})();

	// dailyStreak: 0일차는 1일차로 보정
	const dailyStreak = Math.max(1, p?.daily_streak ?? p?.dailyStreak ?? 1);

	// 경험치: 프로필 경험치 + streak 보상 경험치
	const experiencePoints = (p?.experience_points ?? p?.xp ?? 0) + streakRewardXp;

	return useMemo(
		() => ({
			nickname: p?.nickname ?? "",
			gold: p?.goldBalance ?? 0,
			level: p?.level ?? Math.floor((experiencePoints / 500) + 1),
			dailyStreak,
			experiencePoints,
			totalGamesPlayed: globalTotalGames,
			totalGamesWon: totalWins,
			totalGamesLost: Math.max(0, globalTotalGames - totalWins),
			winRate: globalTotalGames > 0 ? (totalWins / globalTotalGames) * 100 : 0,
			currentWinStreak: currentWinStreak,
			isAdmin: !!(p?.isAdmin || p?.is_admin),
		}),
		[
			p?.nickname, 
			p?.goldBalance, 
			p?.level, 
			dailyStreak,
			experiencePoints,
			globalTotalGames,
			totalWins,
			currentWinStreak,
			p?.isAdmin, 
			p?.is_admin
		]
	);
}

// 범용 메모이즈 셀렉터: 복수 컴포넌트에서 동일 파생값 재사용 시 사용
export function useProfileSelector<T>(selector: (p:any)=>T, deps?: any[]) {
	const p = useGlobalProfile() as any;
	const v = selector(p);
	return useMemo(()=>v, deps && deps.length ? deps : [v]);
}
