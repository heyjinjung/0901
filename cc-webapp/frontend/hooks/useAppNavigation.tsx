import { useState, useCallback } from 'react';
import { AppScreen } from '../types';

export function useAppNavigation() {
  // E2E: 초기 화면을 로컬 스토리지 플래그로 강제 가능
  const initialScreen = (() => {
    try {
      if (typeof window !== 'undefined') {
        const forced = window.localStorage.getItem('E2E_FORCE_SCREEN');
        if (forced) return forced as AppScreen;
      }
    } catch {/* noop */}
    return 'loading' as AppScreen;
  })();

  const [currentScreen, setCurrentScreen] = useState(initialScreen);
  const [isSideMenuOpen, setIsSideMenuOpen] = useState(false);

  // 🎯 네비게이션 핸들러
  const navigate = useCallback((screen: AppScreen) => {
    setCurrentScreen(screen);
    setIsSideMenuOpen(false);
  }, []);

  const navigationHandlers = {
    // 기본 네비게이션
    navigate,
    toLogin: () => navigate('login'),
    toSignup: () => navigate('signup'),
    toAdminLogin: () => navigate('admin-login'),
    toHome: () => navigate('home-dashboard'),
    toGames: () => navigate('game-dashboard'),
    toShop: () => navigate('shop'),
    toInventory: () => navigate('inventory'),
    toProfile: () => navigate('profile'),
    toSettings: () => navigate('settings'),
    toAdminPanel: () => navigate('admin-panel'),
    toEventMissionPanel: () => navigate('event-mission-panel'),
    toStreaming: () => navigate('streaming'),

    // 게임 네비게이션
    toSlot: () => navigate('neon-slot'),
    toRPS: () => navigate('rock-paper-scissors'),
    toGacha: () => navigate('gacha-system'),
    toCrash: () => navigate('neon-crash'), // 🚀 크래시 게임 추가

    // 뒤로가기 네비게이션
    backToHome: () => navigate('home-dashboard'),
    backToGames: () => navigate('game-dashboard'),
  };

  // 사이드 메뉴 핸들러
  const toggleSideMenu = useCallback(() => {
    setIsSideMenuOpen((prev: boolean) => !prev);
  }, []);

  const closeSideMenu = useCallback(() => {
    setIsSideMenuOpen(false);
  }, []);

  // 하단 네비게이션 핸들러 - 수정됨
  const handleBottomNavigation = useCallback((screen: string) => {
    switch (screen) {
      case 'home-dashboard': // 🔧 수정: 'home' → 'home-dashboard'
        navigate('home-dashboard');
        break;
      case 'game-dashboard': // 🔧 수정: 'games' → 'game-dashboard'
        navigate('game-dashboard');
        break;
      case 'shop':
        navigate('shop');
        break;
      case 'profile':
        navigate('profile');
        break;
      default:
        break;
    }
  }, [navigate]);

  return {
    currentScreen,
    isSideMenuOpen,
    navigationHandlers,
    toggleSideMenu,
    closeSideMenu,
    handleBottomNavigation,
  };
}