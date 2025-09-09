/**
 * DEPRECATED (2025-08-17)
 * ---------------------------------------------------------------------------
 * 이 훅은 초기 프론트엔드 로컬 상태 기반 인증 시뮬레이션을 위해 사용되었으며
 * 실제 백엔드 JWT 흐름이 구축됨에 따라 더 이상 사용을 권장하지 않습니다.
 * 신규 코드는 반드시 `useAuth` 훅 (frontend/hooks/useAuth.ts)을 사용하여
 * /api/auth/signup, /api/auth/login, /api/auth/refresh 엔드포인트와 통신하십시오.
 *
 * 향후 제거 예정: (예정) 2025-09 이후.
 * 마이그레이션 가이드:
 *   1) handleLogin/handleSignup 호출부를 useAuth().login / useAuth().signup 으로 교체
 *   2) 사용자 상태(user)와 로딩 상태(loading)는 useAuth 리턴값 활용
 *   3) 알림/네비게이션 로직은 인증 성공 Promise resolve 이후 후처리로 이동
 */
import { useCallback } from 'react';
import { APP_CONFIG, ADMIN_SECURITY_CODE, NOTIFICATION_MESSAGES } from '../constants/appConstants';
import { User } from '../types';

interface AuthHandlersProps {
  setIsLoading: (loading: boolean) => void;
  isAdminAccount: (nickname: string, password: string) => boolean;
  createUserData: (
    nickname: string,
    password: string,
    isSignup?: boolean,
    inviteCode?: string
  ) => User;
  updateUser: (user: User) => void;
  navigationHandlers: any;
  addNotification: (message: string) => void;
  logout: () => void;
  closeSideMenu: () => void;
}

export function useAuthHandlers({
  setIsLoading,
  isAdminAccount,
  createUserData,
  updateUser,
  navigationHandlers,
  addNotification,
  logout,
  closeSideMenu,
}: AuthHandlersProps) {
  // 🔐 로그인 처리
  const handleLogin = useCallback(
    async (nickname: string, password: string): Promise<boolean> => {
      setIsLoading(true);
      await new Promise((resolve) => setTimeout(resolve, APP_CONFIG.LOGIN_DELAY));

      if (nickname.length >= 2 && password.length >= 4) {
        const userData = createUserData(nickname, password, false);
        const isAdmin = isAdminAccount(nickname, password);

        updateUser(userData);
        navigationHandlers.toHome();
        addNotification(NOTIFICATION_MESSAGES.LOGIN_SUCCESS(nickname, isAdmin));
        setIsLoading(false);
        return true;
      }

      setIsLoading(false);
      return false;
    },
    [createUserData, isAdminAccount, updateUser, navigationHandlers, addNotification, setIsLoading]
  );

  // 📝 회원가입 처리
  const handleSignup = useCallback(
    async (formData: any): Promise<boolean> => {
      setIsLoading(true);
      await new Promise((resolve) => setTimeout(resolve, APP_CONFIG.SIGNUP_DELAY));

      const userData = createUserData(formData.nickname, '', true, formData.inviteCode);
      updateUser(userData);
      navigationHandlers.toHome();
      addNotification(NOTIFICATION_MESSAGES.SIGNUP_SUCCESS(userData.goldBalance));
      setIsLoading(false);
      return true;
    },
    [createUserData, updateUser, navigationHandlers, addNotification, setIsLoading]
  );

  // 🔐 관리자 로그인 처리
  const handleAdminLogin = useCallback(
    async (adminId: string, password: string): Promise<boolean> => {
      setIsLoading(true);
      await new Promise((resolve) => setTimeout(resolve, APP_CONFIG.ADMIN_LOGIN_DELAY));

      const isValidAdmin = isAdminAccount(adminId, password);

      if (isValidAdmin) {
        // 🔧 관리자 사용자 데이터 생성 및 설정
        const adminUserData = createUserData(adminId, password, false);
        updateUser(adminUserData);

        addNotification(NOTIFICATION_MESSAGES.ADMIN_LOGIN_SUCCESS);
        navigationHandlers.toAdminPanel(); // 🔧 수정: 관리자 패널로 직접 이동
        setIsLoading(false);
        return true;
      }

      setIsLoading(false);
      return false;
    },
    [isAdminAccount, createUserData, updateUser, navigationHandlers, addNotification, setIsLoading]
  );

  // 🚪 로그아웃 처리
  const handleLogout = useCallback(() => {
    logout();
    closeSideMenu();
    navigationHandlers.toLogin();
    addNotification(NOTIFICATION_MESSAGES.LOGOUT_SUCCESS);
  }, [logout, closeSideMenu, navigationHandlers, addNotification]);

  return {
    handleLogin,
    handleSignup,
    handleAdminLogin,
    handleLogout,
  };
}
