// 백엔드 게임 통계 API 응답을 프론트엔드 전역 스토어 형식으로 변환
export function normalizeGameStatsResponse(apiResponse: any) {
  if (!apiResponse?.success || !apiResponse?.stats) {
    return {};
  }

  const stats = apiResponse.stats;
  const breakdown = stats.game_breakdown || {};

  // 🎯 프론트엔드에서 기대하는 핵심 메트릭 (전역동기화)
  const normalized: Record<string, any> = {
    // 전체 통계 - 메인 대시보드용
    total_games_played: stats.total_games_played || 0,
    total_wins: stats.total_wins || 0,
    total_losses: stats.total_losses || 0,
    overall_max_win: stats.overall_max_win || 0,  // 🎯 핵심
    win_rate: stats.win_rate || 0,
    total_profit: stats.total_profit || 0,
    last_updated: stats.updated_at,
    user_id: stats.user_id,

    // 레거시 별칭 유지 (기존 컴포넌트 호환)
    total_games: stats.total_games_played || 0,  
    total_bets: stats.total_bets || 0,
  };

  // 게임별 세부 통계
  normalized.game_breakdown = {
    slot: {
      plays: breakdown.slot?.spins || 0,
      wins: breakdown.slot?.wins || 0,
      losses: breakdown.slot?.losses || 0,
      max_win: breakdown.slot?.max_win || 0
    },
    crash: {
      plays: breakdown.crash?.bets || 0,
      wins: breakdown.crash?.wins || 0,
      losses: breakdown.crash?.losses || 0,
      max_win: breakdown.crash?.max_win || 0,
      max_multiplier: breakdown.crash?.max_multiplier || null
    },
    gacha: {
      plays: breakdown.gacha?.spins || 0,
      rare_wins: breakdown.gacha?.rare_wins || 0,
      ultra_rare_wins: breakdown.gacha?.ultra_rare_wins || 0,
      max_win: breakdown.gacha?.max_win || 0
    },
    rps: {
      plays: breakdown.rps?.plays || 0,
      wins: breakdown.rps?.wins || 0,
      losses: breakdown.rps?.losses || 0,
      ties: breakdown.rps?.ties || 0
    }
  };

  // 🎯 개별 게임 레거시 필드 (기존 UI 호환)
  normalized.slot_spins = breakdown.slot?.spins || 0;
  normalized.crash_games = breakdown.crash?.bets || 0;
  normalized.gacha_pulls = breakdown.gacha?.spins || 0;
  normalized.rps_games = breakdown.rps?.plays || 0;

  return normalized;
}
