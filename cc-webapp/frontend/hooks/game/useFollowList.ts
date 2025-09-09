import React, { useState, useCallback } from 'react';
import { api } from '@/lib/unifiedApi';

interface FollowItem { user_id: number; nickname: string; followed_at: string; }
interface FollowListResponse { total: number; items: FollowItem[]; limit: number; offset: number; }
interface FollowActionResponse { success: boolean; following: boolean; target_user_id: number; follower_count: number; following_count: number; }

export function useFollowList(authToken: string | null) {
  const [list, setList] = useState(null as any);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null as any);

  const refresh = useCallback(async (limit = 20, offset = 0) => {
    setLoading(true); setError(null);
    try {
    const res = await api.get<FollowListResponse>(`games/follow/list?limit=${limit}&offset=${offset}`);
      setList(res);
    } catch (e: any) { setError(e.message); }
    finally { setLoading(false); }
  }, []);

  const follow = useCallback(async (targetUserId: number) => {
    try {
    await api.post<FollowActionResponse>(`games/follow/${targetUserId}`, {});
      await refresh();
    } catch (e: any) { setError(e.message); }
  }, [refresh]);

  const unfollow = useCallback(async (targetUserId: number) => {
    try {
    await api.del<FollowActionResponse>(`games/follow/${targetUserId}`);
      await refresh();
    } catch (e: any) { setError(e.message); }
  }, [refresh]);

  return { list, refresh, follow, unfollow, loading, error };
}
