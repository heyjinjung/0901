'use client';

import React from 'react';
import { useRealtimePurchaseBadge } from '@/hooks/useRealtimeData';
import { motion } from 'framer-motion';
import { 
  Home, 
  Gamepad2, 
  ShoppingBag, 
  Sparkles, 
  User,
  Crown,
  ExternalLink,
  Video
} from 'lucide-react';

interface BottomNavigationProps {
  currentScreen: string;
  onNavigate: (screen: string) => void;
}

import { useUserGold, useUserLevel } from '@/hooks/useSelectors';

export function BottomNavigation({ currentScreen, onNavigate }: BottomNavigationProps) {
  const { pendingCount } = useRealtimePurchaseBadge();
  const gold = useUserGold();
  // null-safe numeric level 보장
  const level = Number(useUserLevel() ?? 1);
  const handleModelNavigation = () => {
    // 본사 사이트로 리다이렉트
    window.open('https://md-01.com', '_blank');
  };

  const navItems = [
    {
      id: 'home-dashboard',
      label: '홈',
      icon: Home,
      activeColor: 'text-primary',
      inactiveColor: 'text-muted-foreground',
      action: () => onNavigate('home-dashboard') // 🔧 직접 전달
    },
    {
      id: 'game-dashboard', 
      label: '게임',
      icon: Gamepad2,
      activeColor: 'text-success',
      inactiveColor: 'text-muted-foreground',
      action: () => onNavigate('game-dashboard') // 🔧 직접 전달
    },
    {
      id: 'shop',
      label: '상점',
      icon: ShoppingBag,
      activeColor: 'text-gold',
      inactiveColor: 'text-muted-foreground',
      action: () => onNavigate('shop')
    },
    {
      id: 'models',
      label: '모델',
      icon: Sparkles,
      activeColor: 'text-warning',
      inactiveColor: 'text-muted-foreground',
      action: handleModelNavigation,
      isExternal: true
    },
    {
      id: 'profile',
      label: '프로필',
      icon: User,
      activeColor: 'text-info',
      inactiveColor: 'text-muted-foreground',
      action: () => onNavigate('profile')
    }
  ];

  return (
    <motion.div
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.3 }}
      className="fixed bottom-0 left-0 right-0 z-50 bg-black/95 backdrop-blur-lg border-t border-primary/20"
      data-testid="bottom-navigation"
    >
      {/* VIP Status Bar */}
  {level >= 10 && (
        <div className="bg-gradient-gold text-black text-center py-1 text-xs font-bold">
          <Crown className="w-3 h-3 inline mr-1" />
          VIP 회원 • 특별 혜택 적용중
        </div>
      )}
      
      <div className="flex items-center justify-around px-2 py-3 max-w-md mx-auto">
        {navItems.map((item, index) => {
          const isActive = currentScreen === item.id;
          const Icon = item.icon;
          
          return (
            <motion.button
              key={item.id}
              whileTap={{ scale: 0.95 }}
              onClick={item.action}
              className="flex flex-col items-center justify-center p-2 rounded-lg relative min-w-[60px] btn-hover-lift"
              data-testid={`nav-${item.id}`}
            >
              {/* Active indicator */}
              {isActive && !item.isExternal && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute inset-0 bg-primary-soft rounded-lg"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                />
              )}
              
              {/* Icon with notification badge */}
              <div className="relative">
                <motion.div
                  animate={isActive && !item.isExternal ? { scale: [1, 1.1, 1] } : {}}
                  transition={{ duration: 0.3, type: 'tween', ease: 'easeOut' }}
                  className="relative"
                >
                  <Icon 
                    className={`w-6 h-6 transition-colors duration-200 ${
                      isActive && !item.isExternal ? item.activeColor : item.inactiveColor
                    }`}
                  />
                  {/* External link indicator */}
                  {item.isExternal && (
                    <ExternalLink className="w-3 h-3 absolute -top-1 -right-1 text-warning" />
                  )}
                </motion.div>
                
                {/* Notification badges */}
        {item.id === 'shop' && pendingCount > 0 && (
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 2, repeat: Infinity, type: 'tween' }}
                    className="absolute -top-2 -right-2 w-4 h-4 bg-gradient-to-r from-error to-warning rounded-full flex items-center justify-center"
                  >
          <span className="text-white text-[10px] font-bold">{pendingCount > 9 ? '9+' : String(pendingCount)}</span>
                  </motion.div>
                )}
                
                {false && (
                  <div className="absolute -top-2 -right-2 w-4 h-4 bg-warning rounded-full flex items-center justify-center">
                    <span className="text-black text-xs">🔥</span>
                  </div>
                )}

                {/* 모델 페이지 포인트 획득 표시 */}
                {item.id === 'models' && (
                  <div className="absolute -top-2 -right-2 w-4 h-4 bg-success rounded-full flex items-center justify-center animate-pulse">
                    <span className="text-white text-xs font-bold">P</span>
                  </div>
                )}
              </div>
              
              {/* Label */}
              <span 
                className={`text-xs font-medium mt-1 transition-colors duration-200 ${
                  isActive && !item.isExternal ? item.activeColor : item.inactiveColor
                }`}
              >
                {item.label}
              </span>
              
              {/* Subtle active glow effect */}
              {isActive && !item.isExternal && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="absolute inset-0 rounded-lg soft-glow"
                />
              )}
            </motion.button>
          );
        })}
      </div>

  {/* Gold balance quick view */}
    {gold > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
      className="absolute top-1 right-2 bg-gradient-gold text-black px-2 py-1 rounded text-xs font-bold"
      data-testid="gold-quick"
        >
      {gold.toLocaleString()}G
        </motion.div>
      )}
      
      {/* Level indicator */}
  {level > 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="absolute top-1 left-2 bg-gradient-game text-white px-2 py-1 rounded text-xs font-bold"
        >
      LV.{level}
        </motion.div>
      )}
    </motion.div>
  );
}