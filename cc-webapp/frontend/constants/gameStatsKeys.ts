// 서버 스키마 확장/변경 시 이 키 목록만 업데이트하면 UI 셀렉터가 자동 추적됩니다.
// 주의: 키 이름은 백엔드 OpenAPI(/api/games/stats/me)와 동기화 유지.

export const TOTAL_KEYS_GLOBAL = [
  'total_games_played',
  'total_games',
  'games',
  'plays',
  'spins',
  'slot_spins',
  'crash_games',
  'gacha_pulls',
  'rps_games',
] as const;

export const GAME_ID_ALIASES: Record<string, string[]> = {
  // 슬롯 통계가 slots/slot_machine/neon_slot 등으로 올 수 있어 별칭 확장
  slot: ['slot', 'slots', 'slot_machine', 'neon_slot'],
  rps: ['rps', 'rock_paper_scissors'],
  gacha: ['gacha'],
  // crash_game 변형 대비
  crash: ['crash', 'crash_game'],
};

export const PLAY_COUNT_KEYS_BY_GAME: Record<string, string[]> = {
  // total_spins/sin_count 등의 스네이크/다양 키도 추적
  slot: ['totalSpins', 'total_spins', 'spin_count', 'spins', 'plays', 'games', 'total_games', 'slot_spins'],
  rps: ['totalGames', 'matches', 'games', 'plays', 'rps_games'],
  gacha: ['totalPulls', 'pulls', 'plays', 'gacha_pulls'],
  crash: ['totalGames', 'games', 'plays', 'crash_games'],
};

export const BEST_SCORE_KEYS_BY_GAME: Record<string, string[]> = {
  slot: ['biggestWin', 'max_win', 'highest_win'],
  rps: ['bestStreak', 'best_streak', 'max_streak'],
  gacha: ['legendaryPulls', 'legendary_count', 'legendaryCount'],
  crash: ['highestMultiplier', 'max_multiplier'],
};

// 세부 지표 키들(게임별 커스텀)
export const SLOT_JACKPOT_KEYS = ['jackpotHits', 'jackpots', 'jackpot_count'] as const;
export const SLOT_TOTAL_WINNINGS_KEYS = [
  'totalWinnings',
  'total_payout',
  'total_winnings',
] as const;

export const GACHA_EPIC_COUNT_KEYS = ['epicCount', 'epic_count'] as const;
export const GACHA_LEGENDARY_COUNT_KEYS = [
  'legendaryCount',
  'legendary_count',
  'ultra_rare_item_count',
] as const;

export const RPS_WINS_KEYS = ['wins', 'totalWins'] as const;
