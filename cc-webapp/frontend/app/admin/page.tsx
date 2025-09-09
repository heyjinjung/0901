'use client';
import React, { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/unifiedApi';
import { AdminDashboard } from '@/components/AdminDashboard';
import { motion } from 'framer-motion';
import { ArrowLeft, Settings, Users, ShoppingCart, BarChart3, Calendar } from 'lucide-react';

interface ProfileMe {
  id: number;
  nickname: string;
  vip_points: number;
  is_admin: boolean;
}

interface CoreStatsDto {
  total_users: number;
  active_users: number;
  online_users: number;
  total_revenue: number;
  today_revenue: number;
  critical_alerts: number;
  pending_actions: number;
}

export default function AdminPage() {
  const router = useRouter();
  const [me, setMe] = useState(null as any as ProfileMe | null);
  const [coreStats, setCoreStats] = useState(null as any as CoreStatsDto | null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null as any as string | null);

  const load = useCallback(async () => {
    setLoading(true); setError(null);
    try {
      const profile = await api.get<ProfileMe>('auth/me');
      if (!profile.is_admin) {
        router.replace('/');
        return;
      }
      setMe(profile);
      try {
        // 백엔드 확장 통계 (/api/admin/stats) : 모든 필드 서버 계산/캐시 5s
        const stats = await api.get<any>('admin/stats');
        setCoreStats({
          total_users: stats.total_users ?? stats.totalUsers ?? 0,
          active_users: stats.active_users ?? stats.activeUsers ?? 0,
          online_users: stats.online_users ?? stats.onlineUsers ?? 0,
          total_revenue: stats.total_revenue ?? stats.totalRevenue ?? 0,
          today_revenue: stats.today_revenue ?? stats.todayRevenue ?? 0,
          critical_alerts: stats.critical_alerts ?? stats.criticalAlerts ?? 0,
          pending_actions: stats.pending_actions ?? stats.pendingActions ?? 0,
        });
      } catch (e:any) {
        setCoreStats({
          total_users: 0,
          active_users: 0,
          online_users: 0,
          total_revenue: 0,
          today_revenue: 0,
          critical_alerts: 0,
          pending_actions: 0,
        });
      }
    } catch (e:any) {
      setError(e.message || '로드 실패');
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => { load(); }, [load]);

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-sm text-gray-400">Loading admin...</div>;
  }
  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-red-400">관리자 페이지 로드 오류: {error}</p>
        <button onClick={load} className="px-3 py-2 rounded bg-neutral-800 hover:bg-neutral-700 text-sm">재시도</button>
      </div>
    );
  }
  if (!me) return null;

  return (
    <motion.div initial={{opacity:0}} animate={{opacity:1}} className="min-h-screen bg-gradient-to-b from-black via-neutral-950 to-black text-gray-100 p-4">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <header className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-4">
            <button onClick={()=>router.push('/')} className="p-2 rounded-lg bg-neutral-800 hover:bg-neutral-700 transition-colors">
              <ArrowLeft className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
                Casino-Club 관리자 센터
              </h1>
              <p className="text-sm text-gray-400 mt-1">로그인: {me?.nickname} (관리자)</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button onClick={load} className="px-4 py-2 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-sm transition-colors">
              새로고침
            </button>
          </div>
        </header>

        {/* 빠른 네비게이션 */}
        <div className="mb-8 grid grid-cols-2 md:grid-cols-4 gap-4">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => router.push('/admin/users')}
            className="flex items-center space-x-3 p-4 rounded-xl bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 transition-all"
          >
            <Users className="h-6 w-6" />
            <span className="font-medium">사용자 관리</span>
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => router.push('/admin/shop')}
            className="flex items-center space-x-3 p-4 rounded-xl bg-gradient-to-r from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 transition-all"
          >
            <ShoppingCart className="h-6 w-6" />
            <span className="font-medium">상점 관리</span>
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => router.push('/admin/stats')}
            className="flex items-center space-x-3 p-4 rounded-xl bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-500 hover:to-purple-600 transition-all"
          >
            <BarChart3 className="h-6 w-6" />
            <span className="font-medium">통계 분석</span>
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => router.push('/admin/events')}
            className="flex items-center space-x-3 p-4 rounded-xl bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-500 hover:to-orange-600 transition-all"
          >
            <Calendar className="h-6 w-6" />
            <span className="font-medium">이벤트 관리</span>
          </motion.button>
        </div>

        {/* 대시보드 */}
        <AdminDashboard
          coreStats={coreStats || undefined}
          loadingStats={loading}
          statsError={error}
          onRefresh={load}
        />
      </div>
    </motion.div>
  );
}
