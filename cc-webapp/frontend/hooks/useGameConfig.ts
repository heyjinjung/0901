import { useState, useEffect } from 'react';
import { api } from '../lib/unifiedApi';
import { hasAccessToken } from '@/lib/unifiedApi';

export interface GachaConfig {
  rarity_table: [string, number][];
  reward_pool: Record<string, any>;
  legacy_cost_mode: boolean;
  cost_single: number;
  cost_ten: number;
}

export interface ShopItem {
  id: number;
  sku: string;
  name: string;
  price_cents: number;
  discounted_price_cents: number;
  gold: number;
  discount_percent: number;
  discount_ends_at: string | null;
  min_rank: string | null;
}

export interface StreakConfig {
  action_type: string;
  count: number;
  ttl_seconds: number | null;
  next_reward: string;
}

export interface GameConfig {
  gacha: GachaConfig | null;
  shop: ShopItem[] | null;
  streak: StreakConfig | null;
  
  // 계산된 값들 (하드코딩 대체용)
  dailyBonusBase: number;
  dailyBonusPerStreak: number;
  levelUpBonusPerLevel: number;
  levelUpExpPerLevel: number;
  slotGameCost: number;
}

const DEFAULT_CONFIG: Omit<GameConfig, 'gacha' | 'shop' | 'streak'> = {
  // 기존 하드코딩된 값들을 기본값으로 유지 (서버에서 설정 못 가져올 때 fallback)
  dailyBonusBase: 1000,
  dailyBonusPerStreak: 200,
  levelUpBonusPerLevel: 500,
  levelUpExpPerLevel: 100,
  slotGameCost: 100, // 기본 슬롯 게임 비용
};

export function useGameConfig() {
  const [config, setConfig] = useState({
    gacha: null,
    shop: null,
    streak: null,
    ...DEFAULT_CONFIG
  } as GameConfig);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null as string | null);

  const fetchConfig = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('[useGameConfig] 게임 설정 로딩 중...');
      // 비로그인 상태면 서버 호출 생략 (기본값 유지)
      if (!hasAccessToken()) {
        console.warn('[useGameConfig] 비인증 상태 → 서버 설정 호출을 건너뜀');
        setConfig((prev: GameConfig)=>({ ...prev, ...DEFAULT_CONFIG }));
        return;
      }
      
      // 병렬로 모든 설정 가져오기
      const [gachaRes, shopRes, streakRes] = await Promise.allSettled([
        api.get('games/gacha/config'),
        api.get('shop/catalog'),
        api.get('streak/status')
      ]);

      const newConfig: GameConfig = { ...DEFAULT_CONFIG, gacha: null, shop: null, streak: null };

      // 가챠 설정 처리
      if (gachaRes.status === 'fulfilled') {
        newConfig.gacha = gachaRes.value;
        // 가챠 비용이 있으면 슬롯 게임 비용으로 사용
        if (gachaRes.value.cost_single) {
          newConfig.slotGameCost = Math.min(gachaRes.value.cost_single, 1000); // 슬롯은 가챠보다 저렴하게
        }
        console.log('[useGameConfig] 가챠 설정 로드됨:', gachaRes.value);
      } else {
        console.warn('[useGameConfig] 가챠 설정 로드 실패:', gachaRes.reason);
      }

      // 상점 설정 처리
      if (shopRes.status === 'fulfilled') {
        newConfig.shop = shopRes.value;
        console.log('[useGameConfig] 상점 설정 로드됨:', shopRes.value.length, '개 상품');
      } else {
        console.warn('[useGameConfig] 상점 설정 로드 실패:', shopRes.reason);
      }

      // 연속 로그인 설정 처리
      if (streakRes.status === 'fulfilled') {
        newConfig.streak = streakRes.value;
        console.log('[useGameConfig] 연속 로그인 설정 로드됨:', streakRes.value);
      } else {
        console.warn('[useGameConfig] 연속 로그인 설정 로드 실패:', streakRes.reason);
      }

      setConfig(newConfig);
      console.log('[useGameConfig] 전체 게임 설정 로드 완료');
      
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      setError(errorMsg);
      console.error('[useGameConfig] 설정 로드 오류:', err);
      
      // 오류 시에도 기본 설정은 사용 가능하도록
      setConfig({
        gacha: null,
        shop: null,
        streak: null,
        ...DEFAULT_CONFIG
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  return {
    config,
    loading,
    error,
    refetch: fetchConfig
  };
}
