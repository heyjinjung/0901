import { GameItem } from './index';

export interface GachaItem extends GameItem {
  id: string;
  name: string;
  // Keep the same type union as GameItem to remain compatible
  type: GameItem['type'];
  rarity: 'common' | 'rare' | 'epic' | 'legendary' | 'mythic';
  rate: number;
  quantity: number;
  description: string;
  icon: string;
  value: number;
  sexiness?: number;
  isNew?: boolean;
}

export interface HeartParticle {
  id: string;
  x: number;
  y: number;
}

export interface GachaBanner {
  id: string;
  name: string;
  description: string;
  cost: number;
  price: number;
  image: string;
  theme?: string;
  guaranteedRarity?: string;
  bonusMultiplier?: number;
  bgGradient: string;
  featuredItems: GachaItem[];
}

export interface SparkleProps {
  id: string;
  size: number;
  left: string;
  top: string;
  animationDelay: string;
  emoji: string;
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