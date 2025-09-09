'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Users,
  Activity,
  DollarSign,
  AlertTriangle,
  Clock,
  TrendingUp,
  CheckCircle,
  XCircle,
  Wifi,
  Bell,
  RefreshCw,
} from 'lucide-react';

interface CoreStatsDto {
  total_users: number;
  active_users: number;
  online_users: number;
  total_revenue: number;
  today_revenue: number;
  critical_alerts: number;
  pending_actions: number;
}

interface AdminDashboardProps {
  coreStats?: CoreStatsDto;
  loadingStats?: boolean;
  statsError?: string | null;
  onRefresh: () => void;
}

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<any>;
  trend?: number;
  color: string;
  description?: string;
  isLoading?: boolean;
}

function StatCard({ title, value, icon: Icon, trend, color, description, isLoading }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative overflow-hidden rounded-xl border border-neutral-800 bg-gradient-to-br from-neutral-900 to-neutral-950 p-6 ${color} shadow-lg`}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-400">{title}</p>
          {isLoading ? (
            <div className="mt-2 h-8 w-24 animate-pulse rounded bg-neutral-700" />
          ) : (
            <p className="mt-2 text-3xl font-bold text-white">
              {typeof value === 'number' ? value.toLocaleString() : value}
            </p>
          )}
          {description && (
            <p className="mt-1 text-xs text-gray-500">{description}</p>
          )}
          {trend !== undefined && (
            <div className={`mt-2 flex items-center text-xs ${trend >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              <TrendingUp className={`mr-1 h-3 w-3 ${trend < 0 ? 'rotate-180' : ''}`} />
              {Math.abs(trend)}% {trend >= 0 ? '증가' : '감소'}
            </div>
          )}
        </div>
        <div className="rounded-lg bg-white bg-opacity-10 p-3">
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
    </motion.div>
  );
}

function SystemHealthIndicator({ health }: { health: 'healthy' | 'warning' | 'critical' }) {
  const config = {
    healthy: {
      color: 'text-green-400',
      bgColor: 'bg-green-400/20',
      icon: CheckCircle,
      label: '정상',
    },
    warning: {
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-400/20',
      icon: AlertTriangle,
      label: '주의',
    },
    critical: {
      color: 'text-red-400',
      bgColor: 'bg-red-400/20',
      icon: XCircle,
      label: '위험',
    },
  };

  const { color, bgColor, icon: Icon, label } = config[health];

  return (
    <div className={`flex items-center space-x-2 rounded-lg px-3 py-2 ${bgColor}`}>
      <Icon className={`h-4 w-4 ${color}`} />
      <span className={`text-sm font-medium ${color}`}>시스템 상태: {label}</span>
    </div>
  );
}

export function AdminDashboard({ coreStats, loadingStats, statsError, onRefresh }: AdminDashboardProps) {
  const [lastUpdated, setLastUpdated] = useState(Date.now());
  
  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdated(Date.now());
    }, 30000); // 30초마다 업데이트 시간 갱신
    
    return () => clearInterval(interval);
  }, []);

  const systemHealth: 'healthy' | 'warning' | 'critical' = 
    coreStats?.critical_alerts && coreStats.critical_alerts > 5 ? 'critical' :
    coreStats?.critical_alerts && coreStats.critical_alerts > 0 ? 'warning' : 'healthy';

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('ko-KR');
  };

  if (statsError) {
    return (
      <div className="flex flex-col items-center justify-center space-y-4 rounded-xl border border-red-800 bg-red-950/20 p-8">
        <XCircle className="h-12 w-12 text-red-400" />
        <div className="text-center">
          <h3 className="text-lg font-semibold text-red-400">통계 로드 실패</h3>
          <p className="mt-2 text-sm text-gray-400">{statsError}</p>
        </div>
        <button
          onClick={onRefresh}
          className="flex items-center space-x-2 rounded-lg bg-red-600 px-4 py-2 text-white hover:bg-red-700"
        >
          <RefreshCw className="h-4 w-4" />
          <span>다시 시도</span>
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-cyan-400 bg-clip-text text-transparent">
            실시간 대시보드
          </h2>
          <p className="mt-1 text-sm text-gray-400">
            마지막 업데이트: {formatTime(lastUpdated)}
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <SystemHealthIndicator health={systemHealth} />
          <button
            onClick={onRefresh}
            className="flex items-center space-x-2 rounded-lg bg-neutral-800 px-3 py-2 text-sm text-gray-300 hover:bg-neutral-700"
          >
            <RefreshCw className="h-4 w-4" />
            <span>새로고침</span>
          </button>
        </div>
      </div>

      {/* 핵심 통계 카드 */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="총 사용자"
          value={coreStats?.total_users ?? 0}
          icon={Users}
          color="border-l-4 border-l-blue-500"
          description="가입된 전체 사용자"
          isLoading={loadingStats}
        />
        
        <StatCard
          title="활성 사용자"
          value={coreStats?.active_users ?? 0}
          icon={Activity}
          color="border-l-4 border-l-green-500"
          description="최근 활동한 사용자"
          isLoading={loadingStats}
        />
        
        <StatCard
          title="온라인 사용자"
          value={coreStats?.online_users ?? 0}
          icon={Wifi}
          color="border-l-4 border-l-purple-500"
          description="현재 접속 중인 사용자"
          isLoading={loadingStats}
        />
        
        <StatCard
          title="오늘 매출"
          value={formatCurrency(coreStats?.today_revenue ?? 0)}
          icon={DollarSign}
          color="border-l-4 border-l-yellow-500"
          description="금일 총 매출액"
          isLoading={loadingStats}
        />
      </div>

      {/* 상세 통계 카드 */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <StatCard
          title="총 매출"
          value={formatCurrency(coreStats?.total_revenue ?? 0)}
          icon={TrendingUp}
          color="border-l-4 border-l-emerald-500"
          description="누적 총 매출액"
          isLoading={loadingStats}
        />
        
        <StatCard
          title="대기 중인 작업"
          value={coreStats?.pending_actions ?? 0}
          icon={Clock}
          color="border-l-4 border-l-orange-500"
          description="처리 대기 중인 작업"
          isLoading={loadingStats}
        />
        
        <StatCard
          title="중요 알림"
          value={coreStats?.critical_alerts ?? 0}
          icon={Bell}
          color="border-l-4 border-l-red-500"
          description="확인이 필요한 알림"
          isLoading={loadingStats}
        />
      </div>

      {/* 🎯 관리자 CRUD 기능 섹션 추가 */}
      <div className="rounded-xl border border-neutral-800 bg-neutral-900/50 p-6">
        <h3 className="mb-4 text-lg font-semibold text-white">⚙️ 관리 기능</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <button
            onClick={() => window.location.href = '/admin/users'}
            className="flex items-center space-x-3 rounded-lg border border-neutral-700 bg-neutral-800 p-4 text-left transition-colors hover:bg-neutral-700"
          >
            <Users className="h-5 w-5 text-blue-400" />
            <div>
              <div className="font-medium text-white">사용자 관리</div>
              <div className="text-xs text-gray-400">사용자 조회, 권한 관리</div>
            </div>
          </button>

          <button
            onClick={() => window.location.href = '/admin/shop'}
            className="flex items-center space-x-3 rounded-lg border border-neutral-700 bg-neutral-800 p-4 text-left transition-colors hover:bg-neutral-700"
          >
            <DollarSign className="h-5 w-5 text-green-400" />
            <div>
              <div className="font-medium text-white">상점 관리</div>
              <div className="text-xs text-gray-400">상품 CRUD, 가격 설정</div>
            </div>
          </button>

          <button
            onClick={() => window.location.href = '/admin/events'}
            className="flex items-center space-x-3 rounded-lg border border-neutral-700 bg-neutral-800 p-4 text-left transition-colors hover:bg-neutral-700"
          >
            <Activity className="h-5 w-5 text-purple-400" />
            <div>
              <div className="font-medium text-white">이벤트 관리</div>
              <div className="text-xs text-gray-400">이벤트 생성, 참여자 관리</div>
            </div>
          </button>

          <button
            onClick={() => window.location.href = '/admin/points'}
            className="flex items-center space-x-3 rounded-lg border border-neutral-700 bg-neutral-800 p-4 text-left transition-colors hover:bg-neutral-700"
          >
            <TrendingUp className="h-5 w-5 text-yellow-400" />
            <div>
              <div className="font-medium text-white">포인트 관리</div>
              <div className="text-xs text-gray-400">포인트 지급, 차감</div>
            </div>
          </button>

          <button
            onClick={() => window.location.href = '/admin/campaigns'}
            className="flex items-center space-x-3 rounded-lg border border-neutral-700 bg-neutral-800 p-4 text-left transition-colors hover:bg-neutral-700"
          >
            <Bell className="h-5 w-5 text-orange-400" />
            <div>
              <div className="font-medium text-white">캠페인 관리</div>
              <div className="text-xs text-gray-400">캠페인 생성, 성과 분석</div>
            </div>
          </button>

          <button
            onClick={() => window.location.href = '/admin/stats'}
            className="flex items-center space-x-3 rounded-lg border border-neutral-700 bg-neutral-800 p-4 text-left transition-colors hover:bg-neutral-700"
          >
            <CheckCircle className="h-5 w-5 text-cyan-400" />
            <div>
              <div className="font-medium text-white">통계 분석</div>
              <div className="text-xs text-gray-400">상세 통계, 리포트</div>
            </div>
          </button>
        </div>
      </div>

      {/* 추가 정보 섹션 */}
      <div className="rounded-xl border border-neutral-800 bg-neutral-900/50 p-6">
        <h3 className="mb-4 text-lg font-semibold text-white">시스템 개요</h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-400">활성화율:</span>
              <span className="text-white">
                {coreStats?.total_users ? 
                  `${((coreStats.active_users / coreStats.total_users) * 100).toFixed(1)}%` : 
                  '0%'
                }
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">온라인율:</span>
              <span className="text-white">
                {coreStats?.total_users ? 
                  `${((coreStats.online_users / coreStats.total_users) * 100).toFixed(1)}%` : 
                  '0%'
                }
              </span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-400">일 평균 매출:</span>
              <span className="text-white">
                {formatCurrency((coreStats?.total_revenue ?? 0) / Math.max(1, new Date().getDate()))}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">사용자당 매출:</span>
              <span className="text-white">
                {formatCurrency((coreStats?.total_revenue ?? 0) / Math.max(1, coreStats?.total_users ?? 1))}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
