import { useState, useCallback } from 'react';
import { api } from '@/lib/unifiedApi';

type RpsHand = 'rock' | 'paper' | 'scissors';
interface RpsPlayResponse { result: 'win' | 'lose' | 'draw'; player_hand: RpsHand; opponent_hand: RpsHand; delta_coin: number; }

export function useRpsPlay(authToken: string | null) {
  const [last, setLast] = useState(null as RpsPlayResponse | null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null as string | null);

  const play = useCallback(async (hand: RpsHand) => {
    setLoading(true); setError(null);
    try {
    const res = await api.post<RpsPlayResponse>('games/rps/play', { hand });
      setLast(res);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  }, []);

  return { play, last, loading, error };
}
