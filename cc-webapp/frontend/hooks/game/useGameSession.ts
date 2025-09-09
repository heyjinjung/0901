import { useState, useCallback } from 'react';
import { api } from '@/lib/unifiedApi';

interface GameSession {
  session_id: string;
  started_at: string;
  active: boolean;
}

export function useGameSession(authToken: string | null) {
  const [session, setSession] = useState(null as GameSession | null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null as string | null);

  const start = useCallback(async () => {
    setLoading(true); setError(null);
    try {
    const s = await api.post<GameSession>('games/session/start', {});
      setSession(s);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  }, []);

  const end = useCallback(async () => {
    if (!session) return;
    setLoading(true); setError(null);
    try {
    await api.post('games/session/end', {});
      setSession(null);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  }, [session]);

  return { session, start, end, loading, error };
}
