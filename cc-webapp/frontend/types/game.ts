export interface Game {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export interface GameAction {
  // Define game action properties here
}

export interface Reward {
  id: string;
  name: string;
  description: string;
  amount: number;
}
