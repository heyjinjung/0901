// Re-export project-wide frontend types so imports from '../types/user' work.
// This file intentionally re-exports from index.ts to provide a stable
// module surface for components that import specific user-related types.

export * from './index';

// Import types locally so we can create aliases without TS name errors
import type { GameStats } from './index';

// Provide compatibility aliases expected by some components.
// These map to the more general types in index.ts or provide a minimal shape
// for responses coming from the backend.
export type UserStats = GameStats;

export interface UserBalance {
	cyber_token_balance?: number;
	[key: string]: any;
}

