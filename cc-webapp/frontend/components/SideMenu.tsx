'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X,
  Settings,
  Shield,
  Calendar,
  LogOut,
  User,
  Award,
  HelpCircle,
  ExternalLink,
  Crown,
  Sparkles,
  Target,
  TrendingUp
} from 'lucide-react';
import { Button } from './ui/button';

interface SideMenuProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigateToAdminPanel: () => void;
  onNavigateToEventMissionPanel: () => void;
  onNavigateToSettings: () => void;
  onLogout: () => void;
  onAddNotification: (message: string) => void;
}

import { useUserSummary, useIsAdmin } from '@/hooks/useSelectors';

export function SideMenu({
  isOpen,
  onClose,
  onNavigateToAdminPanel,
  onNavigateToEventMissionPanel,
  onNavigateToSettings,
  onLogout,
  onAddNotification
}: SideMenuProps) {
  const summary = useUserSummary();
  const isAdmin = useIsAdmin();
  const handleExternalLink = () => {
    window.open('https://md-01.com', '_blank');
    onAddNotification('🌟 프리미엄 모델 페이지로 이동합니다!');
    onClose();
  };

  const menuItems = [
    {
      icon: Calendar,
      label: '이벤트 & 미션',
      description: '특별 이벤트와 일일 미션',
      color: 'text-primary',
      bgColor: 'bg-primary-soft',
      action: onNavigateToEventMissionPanel,
      badge: 'NEW'
    },
    {
      icon: Settings,
      label: '설정',
      description: '앱 설정 및 환경설정',
      color: 'text-info',
      bgColor: 'bg-info-soft',
      action: onNavigateToSettings
    },
    {
      icon: Sparkles,
      label: '프리미엄 모델',
      description: '추가 포인트 획득하기',
      color: 'text-warning',
      bgColor: 'bg-warning-soft',
      action: handleExternalLink,
      isExternal: true,
      badge: '+P'
    },
    {
      icon: HelpCircle,
      label: '도움말',
      description: '게임 가이드 및 FAQ',
      color: 'text-success',
      bgColor: 'bg-success-soft',
      action: () => onAddNotification('📚 도움말 페이지가 준비중입니다.')
    }
  ];

  // 관리자 전용 메뉴 아이템
  if (isAdmin) {
    menuItems.unshift({
      icon: Shield,
      label: '관리자 패널',
      description: '시스템 관리 및 유저 관리',
      color: 'text-error',
      bgColor: 'bg-error-soft',
      action: onNavigateToAdminPanel,
      badge: 'ADMIN'
    });
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40"
            onClick={onClose}
          />
          
          {/* Side Menu */}
          <motion.div
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed left-0 top-0 h-full w-80 bg-background border-r border-border-secondary z-50 glass-effect"
          >
            <div className="flex flex-col h-full">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-border-secondary">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-game rounded-full flex items-center justify-center">
                    <Crown className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg font-bold text-gradient-primary">NEON QUEST</h2>
                    <p className="text-xs text-muted-foreground">게임 메뉴</p>
                  </div>
                </div>
                
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={onClose}
                  className="btn-hover-lift"
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>

              {/* User Info */}
              {summary?.nickname && (
                <div className="p-6 border-b border-border-secondary">
                  <div className="flex items-center gap-3 mb-3">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                      isAdmin ? 'bg-gradient-to-r from-error to-warning' : 'bg-gradient-game'
                    }`}>
                      <User className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-bold text-foreground">{summary.nickname}</h3>
                        {isAdmin && (
                          <div className="bg-error text-white text-xs px-2 py-0.5 rounded-full font-bold">
                            ADMIN
                          </div>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">레벨 {summary.level}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-secondary/30 rounded-lg p-3 text-center">
                      <div className="text-lg font-bold text-gold">{summary.gold.toLocaleString()}G</div>
                      <div className="text-xs text-muted-foreground">골드</div>
                    </div>
                    <div className="bg-secondary/30 rounded-lg p-3 text-center">
                      <div className="text-lg font-bold text-primary">{summary.dailyStreak}일</div>
                      <div className="text-xs text-muted-foreground">연속접속</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Menu Items */}
              <div className="flex-1 p-4 space-y-2">
                {menuItems.map((item, index) => (
                  <motion.button
                    key={item.label}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    onClick={item.action}
                    className="w-full flex items-center gap-4 p-4 rounded-xl hover:bg-secondary/20 transition-all card-hover-float group"
                  >
                    <div className={`w-12 h-12 rounded-lg ${item.bgColor} flex items-center justify-center`}>
                      <item.icon className={`w-6 h-6 ${item.color}`} />
                    </div>
                    
                    <div className="flex-1 text-left">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-foreground group-hover:text-primary transition-colors">
                          {item.label}
                        </span>
                        {item.isExternal && <ExternalLink className="w-3 h-3 text-muted-foreground" />}
                        {item.badge && (
                          <span className={`text-xs px-1.5 py-0.5 rounded-full font-bold ${
                            item.badge === 'ADMIN' ? 'bg-error text-white' :
                            item.badge === 'NEW' ? 'bg-primary text-white' :
                            item.badge === '+P' ? 'bg-warning text-black' :
                            'bg-info text-white'
                          }`}>
                            {item.badge}
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{item.description}</p>
                    </div>
                  </motion.button>
                ))}
              </div>

              {/* Stats Quick View */}
        {summary?.nickname && (
                <div className="p-4 border-t border-border-secondary">
                  <div className="grid grid-cols-3 gap-2 text-center">
                    <div>
          <div className="text-sm font-bold text-success">{summary.totalGamesWon || 0}</div>
                      <div className="text-xs text-muted-foreground">승리</div>
                    </div>
                    <div>
          <div className="text-sm font-bold text-warning">{summary.currentWinStreak || 0}</div>
                      <div className="text-xs text-muted-foreground">연승</div>
                    </div>
                    <div>
          <div className="text-sm font-bold text-info">{summary.totalGamesPlayed || 0}</div>
                      <div className="text-xs text-muted-foreground">게임수</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Footer */}
              <div className="p-4 border-t border-border-secondary">
                <Button
                  onClick={onLogout}
                  variant="outline"
                  className="w-full border-error text-error hover:bg-error hover:text-white btn-hover-lift"
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  로그아웃
                </Button>
                
                <div className="mt-3 text-center">
                  <p className="text-xs text-muted-foreground">NEON QUEST v1.0.0</p>
                  <p className="text-xs text-muted-foreground">© 2024 Game Studio</p>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}