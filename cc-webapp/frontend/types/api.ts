// Minimal API types aligned with backend games router
export type CrashBetRequest = {
  bet_amount: number;
  auto_cashout_multiplier?: number | null;
};

export type CrashBetResponse = {
  success: boolean;
  game_id: string;
  bet_amount: number;
  potential_win: number;
  max_multiplier: number;
  message: string;
  balance: number;
};

export type SlotSpinResponse = {
  reels: string[];
  win_amount: number;
  is_jackpot: boolean;
  balance: number;
};

export type RPSPlayResponse = {
  success: boolean;
  player_choice: 'rock' | 'paper' | 'scissors';
  computer_choice: 'rock' | 'paper' | 'scissors';
  result: 'win' | 'lose' | 'draw';
  win_amount: number;
  message: string;
  balance: number;
  streak: number | null;
};
