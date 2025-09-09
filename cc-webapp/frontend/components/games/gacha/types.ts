export interface GachaStats {
  totalPulls: number;
  legendaryPulls: number;
  totalValue: number;
  pulls: number[];
  totalSpent: number;
  epicCount: number;
  legendaryCount: number;
}

export type GachaRarity = "common" | "rare" | "epic" | "legendary" | "mythic";

export interface SparkleProps {
  id: string;
  size: number;
  left: string;
  top: string;
  animationDelay: string;
  emoji?: string;
}

export interface ParticleProps {
  id: string;
  size: number;
  left: string;
  top: string;
  animationDuration: string;
  animationDelay: string;
  rarity: string;
}