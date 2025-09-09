'use client';

import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { LoadingScreen } from '../components/LoadingScreen';
import { LoginScreen } from '../components/LoginScreen';
import { SignupScreen } from '../components/SignupScreen';
import { AdminLoginScreen } from '../components/AdminLoginScreen';
import { HomeDashboard } from '../components/HomeDashboard';
import { GameDashboard } from '../components/GameDashboard';

import { SettingsScreen } from '../components/SettingsScreen';
import { ShopScreen } from '../components/ShopScreen';
import { InventoryScreen } from '../components/InventoryScreen';
import { ProfileScreen } from '../components/ProfileScreen';
import { SideMenu } from '../components/SideMenu';
import { AdminPanel } from '../components/AdminPanel';
import { EventMissionPanel } from '../components/EventMissionPanel';
import { BottomNavigation } from '../components/BottomNavigation';
import { NeonSlotGame } from '../components/games/NeonSlotGame';
import { RockPaperScissorsGame } from '../components/games/RockPaperScissorsGame';
import { GachaSystem } from '../components/games/GachaSystem';
import { NeonCrashGame } from '../components/games/NeonCrashGame';
import { StreamingScreen } from '../components/StreamingScreen';
import { useNotificationSystem } from '../components/NotificationSystem';
import { useUserManager } from '../hooks/useUserManager';
import { useAppNavigation } from '../hooks/useAppNavigation';
// NOTE: Deprecated useAuthHandlers (local simulation) removed – now using real backend auth via useAuth
import { useAuth } from '../hooks/useAuth';
// 전역 Provider는 app/layout.tsx의 <Providers>에서 래핑됨
import { useGlobalStore, setProfile } from '../store/globalStore';
import DailyRewardClaimedDialog from '../components/rewards/DailyRewardClaimedDialog';
import {
  APP_CONFIG,
  SCREENS_WITH_BOTTOM_NAV,
  NOTIFICATION_MESSAGES,
} from '../constants/appConstants';
import { NOTIFICATION_STYLES } from '../constants/notificationConstants';

type NotificationItem = { id: string | number; message: React.ReactNode };

type AppProps = {
  isAuthenticated?: boolean;
};

export default function App({ isAuthenticated }: AppProps) {
  // 모든 hooks는 최상단에서 항상 호출되어야 함 - 조건부 return 전에 모두 선언
  const [isLoading, setIsLoading] = useState(false);
  const [hasInitialized, setHasInitialized] = useState(false);
  const [isClient, setIsClient] = useState(false);
  const externalNavRef = useRef(false);

  // 🎯 커스텀 훅으로 상태 관리 분리 - 항상 호출
  const {
    user,
    updateUser,
    isAdminAccount,
    createUserData,
    restoreSavedUser,
    processDailyBonus,
    logout,
  } = useUserManager();

  const {
    currentScreen,
    isSideMenuOpen,
    navigationHandlers,
    toggleSideMenu,
    closeSideMenu,
    handleBottomNavigation,
  } = useAppNavigation();

  // 📱 알림 시스템
  const { notifications, addNotification } = useNotificationSystem();

  // 🌐 전역 스토어
  const { dispatch } = useGlobalStore();

  // 🔐 실제 백엔드 인증 훅 (JWT 토큰 저장 & 프로필 fetch)
  const auth = useAuth();
  
  // 클라이언트 렌더링 확인
  useEffect(() => {
    setIsClient(true);
  }, []);

  //  useAuth 사용자 변경 감지 - 백엔드 인증 상태가 변경되면 UI 상태 동기화
  useEffect(() => {
    if (auth.user && !auth.loading) {
      console.log('[App] useAuth 사용자 변경 감지:', auth.user.nickname);
      
      // 현재 UI 사용자가 GUEST이고 백엔드에 인증된 사용자가 있다면 업데이트
      if (user?.nickname === 'GUEST' || user?.nickname === 'E2E') {
        console.log('[App] GUEST → 인증된 사용자로 UI 상태 업데이트');
        const authUserData = createUserData(
          auth.user.nickname || 'USER',
          '',
          false
        );
        if (auth.user.goldBalance !== undefined) {
          authUserData.goldBalance = auth.user.goldBalance;
        }
        updateUser(authUserData);
      }
    }
  }, [auth.user, auth.loading, user?.nickname, createUserData, updateUser]);

  // 🔄 앱 초기화 - 한 번만 실행되도록 개선
  useEffect(() => {
    if (hasInitialized) return;

    const initializeApp = async () => {
      try {
        // 테스트 전용 강제 화면 플래그 우선 확인
        let forced: string | null = null;
        try {
          forced = localStorage.getItem('E2E_FORCE_SCREEN');
        } catch {}

        const savedUser = restoreSavedUser();
        
        console.log('[App] 초기화 상태:', {
          savedUser: savedUser?.nickname,
          authUser: auth.user?.nickname,
          hasAuthUser: !!auth.user
        });
        
        // 백엔드 인증 상태 확인 - 이미 로그인된 상태라면 사용자 정보 복원
        if (!savedUser && auth.user) {
          console.log('[App] 백엔드 인증 사용자로 UI 상태 업데이트:', auth.user.nickname);
          // 백엔드에서 인증된 사용자가 있다면 UI 상태에 반영
          const authUserData = createUserData(
            auth.user.nickname || 'USER',
            '',
            false
          );
          if (auth.user.goldBalance !== undefined) {
            authUserData.goldBalance = auth.user.goldBalance;
          }
          updateUser(authUserData);
        } else if (savedUser) {
          console.log('[App] 저장된 사용자 복원:', savedUser.nickname);
          updateUser(savedUser);
        } else {
          // production 환경에서는 절대 게스트 스텁 유저 생성 금지
          // 그리고 이미 인증된 사용자가 있다면 스텁 생성하지 않음
          let allowStub = false;
          const isAlreadyAuthenticated = !!auth.user;
          
          try {
            const env = (process as any)?.env?.NODE_ENV;
            if (env && String(env) === 'production') {
              allowStub = false;
            } else if (!isAlreadyAuthenticated) {
              // 개발/테스트 환경에서만 허용하고, 인증되지 않은 경우에만
              const stubEnv = (process as any)?.env?.NEXT_PUBLIC_ALLOW_STUB_USER;
              if (stubEnv && (String(stubEnv) === '1' || String(stubEnv).toLowerCase() === 'true')) allowStub = true;
              if (!allowStub && typeof window !== 'undefined') {
                allowStub = window.localStorage.getItem('E2E_ALLOW_STUB') === '1';
              }
              if (!allowStub) allowStub = true; // 개발 기본 허용
            }
          } catch {}
          
          if ((forced || allowStub) && String((process as any)?.env?.NODE_ENV) !== 'production' && !isAlreadyAuthenticated && forced) {
            // 강제로 요청된 경우에만 스텁 유저 생성 (일반적인 경우에는 생성하지 않음)
            const stub = createUserData(forced ? 'E2E' : 'GUEST', '', false);
            updateUser(stub);
          }
        }

        // 네비게이션 결정: 강제 화면 우선 → 인증 상태에 따른 화면 결정 (단, 외부 네비게이션이 이미 개입했으면 건드리지 않음)
        if (!externalNavRef.current) {
          if (forced && typeof forced === 'string') {
            navigationHandlers.navigate(forced as any);
          } else if (savedUser || auth.user) {
            // 인증된 사용자만 홈으로 이동
            navigationHandlers.toHome();
          } else {
            // 비인증 사용자는 로그인 화면으로 이동
            navigationHandlers.toLogin();
          }
        }

        // 저장 유저가 있는 경우에만 일일 보너스 체크 수행
        if (savedUser) {
          const lastLogin = new Date(savedUser.lastLogin);
          const today = new Date();
          const timeDiff = today.getTime() - lastLogin.getTime();
          const daysDiff = Math.floor(timeDiff / (1000 * 3600 * 24));

          if (daysDiff >= 1) {
            const { updatedUser, bonusGold } = processDailyBonus(savedUser);
            updateUser(updatedUser);
            addNotification(NOTIFICATION_MESSAGES.DAILY_BONUS(bonusGold, updatedUser.dailyStreak));
          }
        }

        setHasInitialized(true);
      } catch (error) {
        console.error('App initialization failed:', error);
        setHasInitialized(true);
      }
    };

    initializeApp();
  }, [
    hasInitialized,
    restoreSavedUser,
    updateUser,
    navigationHandlers,
    processDailyBonus,
    addNotification,
    auth.user,
    createUserData
  ]);

  // E2E 전용 전역 헬퍼 노출: 테스트에서 직접 화면 전환/유저 시드 가능
  useEffect(() => {
    try {
      // 화면 전환
      (window as any).__E2E_NAV = (screen: string) => {
        try { externalNavRef.current = true; } catch {}
        navigationHandlers.navigate(screen as any);
      };
      // 유저 주입 (미지정 시 기본 스텁)
      (window as any).__E2E_SET_USER = (stub?: any) => {
        const u = stub || createUserData('E2E', '', false);
        updateUser(u as any);
      };
    } catch {
      // noop
    }
  }, [navigationHandlers, updateUser, createUserData]);

  // 개발/테스트 편의: 게임 화면 진입 시 유저가 없으면 안전 스텁 자동 주입
  useEffect(() => {
    const isGameScreen = (
      currentScreen === 'game-dashboard' ||
      currentScreen === 'neon-slot' ||
      currentScreen === 'rock-paper-scissors' ||
      currentScreen === 'gacha-system' ||
      currentScreen === 'neon-crash'
    );
    if (!isGameScreen || user) return;
    // production 환경에서는 절대 게스트 스텁 유저 생성 금지
    let allow = false;
    try {
      const env = (process as any)?.env?.NODE_ENV;
      if (env && String(env) === 'production') {
        allow = false;
      } else {
        // 개발/테스트 환경에서만 허용
        const stubEnv = (process as any)?.env?.NEXT_PUBLIC_ALLOW_STUB_USER;
        if (stubEnv && (String(stubEnv) === '1' || String(stubEnv).toLowerCase() === 'true')) allow = true;
        if (!allow && typeof window !== 'undefined') {
          allow = window.localStorage.getItem('E2E_ALLOW_STUB') === '1';
        }
        if (!allow) allow = true; // 개발 기본 허용
      }
    } catch {/* ignore */}
    if (allow && String((process as any)?.env?.NODE_ENV) !== 'production') {
      const stub = createUserData('GUEST', '', false);
      updateUser(stub);
    }
  }, [currentScreen, user, createUserData, updateUser]);

  // 🏠 하단 네비게이션 표시 여부 결정 (메모이제이션)
  const showBottomNavigation = useMemo(() => {
    return SCREENS_WITH_BOTTOM_NAV.includes(currentScreen as any) && user;
  }, [currentScreen, user]);

  // ---------------------------------------------------------------------------
  // Daily Reward Claimed Dialog 상태 
  // ---------------------------------------------------------------------------
  const [isDailyRewardClaimedOpen, setDailyRewardClaimedOpen] = useState(false);

  // 모든 콜백 함수들 정의
  const handleLogin = React.useCallback(
    async (nickname: string, password: string): Promise<boolean> => {
      setIsLoading(true);
      try {
        // 🚫 관리자 계정은 일반 로그인 차단
        if (isAdminAccount(nickname, password)) {
          console.log('[App] 관리자 계정 일반 로그인 차단:', nickname);
          addNotification({
            id: Date.now().toString(),
            message: '관리자 계정은 관리자 로그인을 사용해주세요.',
            type: 'error',
            duration: 5000
          });
          return false;
        }

        // backend login 은 site_id 를 요구 – 현재 UI 입력 nickname 을 site_id 로 간주
        const authUser = await auth.login(nickname, password); // 실패 시 throw, 성공 시 AuthUser 반환
        
        console.log('[App] 로그인 성공, 백엔드 사용자 정보:', authUser);
        
        // 백엔드에서 받은 실제 사용자 정보로 UI 상태 업데이트
        const userData = createUserData(
          authUser.nickname || nickname, // 백엔드에서 받은 nickname 사용, fallback으로 입력된 nickname
          password, 
          false
        );
        
        console.log('[App] 생성된 UI 사용자 데이터:', userData);
        
        // 백엔드에서 받은 골드 잔액 정보가 있다면 반영
        if (authUser.goldBalance !== undefined) {
          userData.goldBalance = authUser.goldBalance;
        }
        
        updateUser(userData);
        navigationHandlers.toHome();
        addNotification(
          NOTIFICATION_MESSAGES.LOGIN_SUCCESS(authUser.nickname || nickname, false) // 관리자가 아니므로 false
        );
        return true;
      } catch (e) {
        console.error('[App] 로그인 실패:', e);
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [
      auth,
      setIsLoading,
      createUserData,
      updateUser,
      navigationHandlers,
      addNotification,
      isAdminAccount,
    ]
  );

  const handleSignup = React.useCallback(
    async (formData: any): Promise<boolean> => {
      setIsLoading(true);
      try {
        // formData: { userId, nickname, phoneNumber, password, confirmPassword, inviteCode }
        await auth.signup({
          site_id: formData.userId,
          nickname: formData.nickname,
          phone_number: formData.phoneNumber,
          password: formData.password,
          invite_code: formData.inviteCode || '',
        });
        const userData = createUserData(formData.nickname, '', true, formData.inviteCode);
        updateUser(userData);
        navigationHandlers.toHome();
        addNotification(NOTIFICATION_MESSAGES.SIGNUP_SUCCESS(userData.goldBalance));
        return true;
      } catch (e) {
        console.error('[App] 회원가입 실패:', e);
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [auth, setIsLoading, createUserData, updateUser, navigationHandlers, addNotification]
  );

  const handleAdminLogin = React.useCallback(
    async (adminId: string, password: string): Promise<boolean> => {
      setIsLoading(true);
      try {
        // 백엔드 관리자 로그인 수행 - AuthUser 객체 반환
        const authUser = await auth.adminLogin(adminId, password);
        
        // 🎯 백엔드에서 받은 실제 관리자 정보로 UI 상태 업데이트
        const adminUser = createUserData(
          authUser.nickname || adminId, // 백엔드에서 받은 nickname 사용, fallback으로 입력된 adminId
          password, 
          false
        );
        
        // 🔑 백엔드에서 받은 관리자 정보를 직접 반영
        adminUser.isAdmin = true; // 관리자 상태 강제 설정
        
        // 백엔드에서 받은 데이터 반영
        if (authUser.gold_balance !== undefined) {
          adminUser.goldBalance = authUser.gold_balance;
        }
        if (authUser.goldBalance !== undefined) {
          adminUser.goldBalance = authUser.goldBalance;
        }
        if (authUser.level !== undefined) {
          adminUser.level = authUser.level;
        }
        if (authUser.experience !== undefined) {
          adminUser.experience = authUser.experience;
        }
        
        console.log('[App] 관리자 로그인 성공, 사용자 정보:', adminUser);
        
        // 🌐 전역 상태에도 관리자 정보 설정
        const globalProfile = {
          id: authUser.id || adminUser.id,
          nickname: authUser.nickname || adminUser.nickname,
          goldBalance: authUser.gold_balance || authUser.goldBalance || adminUser.goldBalance,
          level: authUser.level || adminUser.level,
          experience_points: authUser.experience_points || authUser.experience || adminUser.experience,
          total_games_played: authUser.total_games_played || 0,
          total_games_won: authUser.total_games_won || 0,
          total_games_lost: authUser.total_games_lost || 0,
          daily_streak: authUser.daily_streak || adminUser.dailyStreak,
          isAdmin: true, // 🔑 전역 상태에도 관리자 정보 설정
          is_admin: true, // 백엔드 필드명도 설정
          updatedAt: new Date().toISOString()
        };
        
        setProfile(dispatch, globalProfile);
        console.log('[App] 전역 상태에 관리자 프로필 설정:', globalProfile);
        
        updateUser(adminUser);
        addNotification(NOTIFICATION_MESSAGES.ADMIN_LOGIN_SUCCESS);
        navigationHandlers.toAdminPanel();
        return true;
      } catch (e) {
        console.error('[App] 관리자 로그인 실패:', e);
        return false;
      } finally {
        setIsLoading(false);
      }
    },
    [auth, setIsLoading, createUserData, updateUser, navigationHandlers, addNotification, dispatch]
  );

  const handleLogout = React.useCallback(() => {
    try {
      auth.logout();
    } catch {
      /* ignore */
    }
    logout(); // UI user state
    closeSideMenu();
    navigationHandlers.toLogin();
    addNotification(NOTIFICATION_MESSAGES.LOGOUT_SUCCESS);
  }, [auth, logout, closeSideMenu, navigationHandlers, addNotification]);

  const openDailyRewardClaimed = useCallback(() => setDailyRewardClaimedOpen(true), []);
  const closeDailyRewardClaimed = useCallback(() => setDailyRewardClaimedOpen(false), []);

  // 내일 알림 받기 (추후 서비스 워커/푸시 연동 예정) - 현재는 토스트로 스텁
  const handleScheduleDailyRewardReminder = useCallback(() => {
    addNotification(
      <span className="text-amber-300">내일 00:00 리셋 알림이 예약(가상)되었습니다.</span>
    );
  }, [addNotification]);

  // 다른 게임 하기 버튼 -> 게임 대시보드 이동
  const handleNavigateToGamesFromDialog = useCallback(() => {
    navigationHandlers.toGames();
  }, [navigationHandlers]);

  // SSR에서 인증되지 않은 경우 또는 클라이언트 렌더링 전에는 로딩 화면 표시
  if (isAuthenticated === false || !isClient) {
    return <LoadingScreen />;
  }

  return (
    <div className="dark">
            {/* 📱 🎯 VIP 알림 시스템 */}
            <div className={NOTIFICATION_STYLES.CONTAINER}>
              <AnimatePresence>
                {notifications.map((notification: NotificationItem) => (
                  <motion.div
                    key={notification.id}
                    initial={NOTIFICATION_STYLES.ANIMATION.INITIAL}
                    animate={NOTIFICATION_STYLES.ANIMATION.ANIMATE}
                    exit={NOTIFICATION_STYLES.ANIMATION.EXIT}
                    className={NOTIFICATION_STYLES.ITEM}
                  >
                    {notification.message}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            {/* 🔧 사이드 메뉴 */}
            <SideMenu
              isOpen={isSideMenuOpen}
              onClose={closeSideMenu}
              onNavigateToAdminPanel={navigationHandlers.toAdminPanel}
              onNavigateToEventMissionPanel={navigationHandlers.toEventMissionPanel}
              onNavigateToSettings={navigationHandlers.toSettings}
              onLogout={handleLogout}
              onAddNotification={addNotification}
            />

            {/* 📱 메인 화면들 */}
            <AnimatePresence mode="wait">
              {currentScreen === 'loading' && (
                <React.Fragment key="loading">
                  <LoadingScreen
                    onComplete={navigationHandlers.toLogin}
                    gameTitle={APP_CONFIG.GAME_TITLE}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'login' && (
                <React.Fragment key="login">
                  {/* 🔧 navigationHandlers 최종 진단 */}
                  {console.log('[App] LoginScreen 렌더링 직전 navigationHandlers:', navigationHandlers)}
                  <LoginScreen
                    onLogin={handleLogin}
                    onSwitchToSignup={navigationHandlers?.toSignup || (() => console.warn('[App] toSignup 핸들러 없음'))}
                    onAdminAccess={navigationHandlers?.toAdminLogin || (() => console.warn('[App] toAdminLogin 핸들러 없음'))}
                    isLoading={isLoading}
                  />
                  {!navigationHandlers && (
                    <div style={{color:'red', position:'fixed', top:'10px', left:'10px', zIndex:9999}}>
                      [App] 경고: navigationHandlers가 undefined입니다!
                    </div>
                  )}
                </React.Fragment>
              )}

              {currentScreen === 'signup' && (
                <React.Fragment key="signup">
                  <SignupScreen
                    onSignup={handleSignup}
                    onBackToLogin={navigationHandlers.toLogin}
                    isLoading={isLoading}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'admin-login' && (
                <React.Fragment key="admin-login">
                  <AdminLoginScreen
                    onAdminLogin={handleAdminLogin}
                    onBackToLogin={navigationHandlers.toLogin}
                    isLoading={isLoading}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'admin' && user && (
                <React.Fragment key="admin">
                  <AdminPanel
                    user={user}
                    onBack={navigationHandlers.toLogin}
                    onUpdateUser={updateUser}
                    onAddNotification={addNotification}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'home-dashboard' && user && (
                <React.Fragment key="home-dashboard">
                  <HomeDashboard
                    user={user}
                    onLogout={handleLogout}
                    onNavigateToGames={navigationHandlers.toGames}
                    onNavigateToShop={navigationHandlers.toShop}
                    onNavigateToSettings={navigationHandlers.toSettings}
                    onNavigateToStreaming={navigationHandlers.toStreaming}
                    onUpdateUser={updateUser}
                    onAddNotification={addNotification}
                    onToggleSideMenu={toggleSideMenu}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'game-dashboard' && user && (
                <React.Fragment key="game-dashboard">
                  <GameDashboard
                    user={user}
                    onNavigateToHome={navigationHandlers.backToHome}
                    onNavigateToSlot={navigationHandlers.toSlot}
                    onNavigateToRPS={navigationHandlers.toRPS}
                    onNavigateToGacha={navigationHandlers.toGacha}
                    onNavigateToCrash={navigationHandlers.toCrash}
                    onUpdateUser={updateUser}
                    onAddNotification={addNotification}
                    onToggleSideMenu={toggleSideMenu}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'shop' && user && (
                <React.Fragment key="shop">
                  <ShopScreen
                    user={user}
                    onBack={navigationHandlers.backToHome}
                    onNavigateToInventory={navigationHandlers.toInventory}
                    onNavigateToProfile={navigationHandlers.toProfile}
                    onUpdateUser={updateUser}
                    onAddNotification={addNotification}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'inventory' && user && (
                <React.Fragment key="inventory">
                  <InventoryScreen
                    user={user}
                    onBack={navigationHandlers.backToHome}
                    onUpdateUser={updateUser}
                    onAddNotification={addNotification}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'profile' && (
                <React.Fragment key="profile">
                  <ProfileScreen
                    onBack={navigationHandlers.backToHome}
                    onAddNotification={addNotification}
                    sharedUser={user}
                    onUpdateUser={updateUser}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'settings' && user && (
                <React.Fragment key="settings">
                  <SettingsScreen
                    user={user}
                    onBack={navigationHandlers.backToHome}
                    onUpdateUser={updateUser}
                    onAddNotification={addNotification}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'admin-panel' && user && (
                <React.Fragment key="admin-panel">
                  <AdminPanel
                    user={user}
                    onBack={navigationHandlers.backToHome}
                    onUpdateUser={updateUser}
                    onAddNotification={addNotification}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'event-mission-panel' && user && (
                <React.Fragment key="event-mission-panel">
                  <EventMissionPanel
                    user={user}
                    onBack={navigationHandlers.backToHome}
                    onUpdateUser={updateUser}
                    onAddNotification={addNotification}
                  />
                </React.Fragment>
              )}

              {/* 🎮 게임들 */}
              {currentScreen === 'neon-slot' && user && (
                <React.Fragment key="neon-slot">
                  <NeonSlotGame
                    user={user}
                    onBack={navigationHandlers.backToGames}
                    onUpdateUser={updateUser}
                    onAddNotification={addNotification}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'rock-paper-scissors' && user && (
                <React.Fragment key="rock-paper-scissors">
                  <RockPaperScissorsGame
                    user={user}
                    onBack={navigationHandlers.backToGames}
                    onUpdateUser={updateUser}
                    onAddNotification={addNotification}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'gacha-system' && user && (
                <React.Fragment key="gacha-system">
                  <GachaSystem
                    user={user}
                    onBack={navigationHandlers.backToGames}
                    onUpdateUser={updateUser}
                    onAddNotification={addNotification}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'neon-crash' && user && (
                <React.Fragment key="neon-crash">
                  <NeonCrashGame
                    user={user}
                    onBack={navigationHandlers.backToGames}
                    onUpdateUser={updateUser}
                    onAddNotification={addNotification}
                  />
                </React.Fragment>
              )}

              {currentScreen === 'streaming' && user && (
                <React.Fragment key="streaming">
                  <StreamingScreen
                    user={user}
                    onBack={navigationHandlers.backToHome}
                    onUpdateUser={updateUser}
                    onAddNotification={addNotification}
                  />
                </React.Fragment>
              )}
            </AnimatePresence>

            {/* 📱 하단 네비게이션 */}
            {showBottomNavigation && (
              <BottomNavigation
                currentScreen={currentScreen}
                onNavigate={handleBottomNavigation}
              />
            )}

            {/* 일일 보상 이미 수령 다이얼로그 */}
            <DailyRewardClaimedDialog
              open={isDailyRewardClaimedOpen}
              onClose={closeDailyRewardClaimed}
              onNavigateGame={handleNavigateToGamesFromDialog}
              onScheduleReminder={handleScheduleDailyRewardReminder}
            />
    </div>
  );
}
