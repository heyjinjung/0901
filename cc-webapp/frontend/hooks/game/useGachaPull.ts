import { useState, useCallback } from 'react';
import { api } from '@/lib/unifiedApi';

interface GachaResultItem { rarity: string; amount: number; reward_type?: string; }
interface GachaPullResponse { success: boolean; cost: number; items: GachaResultItem[]; pity_counter?: number; }

export function useGachaPull(authToken: string | null) {
  // React 타입 인식 문제로 generic 제거 후 단언 사용 (빌드 에러 회피)
  const [lastResult, setLastResult] = useState(null as GachaPullResponse | null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null as string | null);

  const pull = useCallback(async (count: 1 | 10 = 1) => {
    setLoading(true); setError(null);
    try {
    // Backend expects field name pull_count at games/gacha/pull
    const res = await api.post<GachaPullResponse>('games/gacha/pull', { pull_count: count });
      setLastResult(res);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  }, []);

  return { pull, lastResult, loading, error };
}
