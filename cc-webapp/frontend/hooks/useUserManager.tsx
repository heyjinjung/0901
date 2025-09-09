import { useState, useCallback, useMemo } from 'react';
import { User } from '../types';
import { 
  ensureUserCompatibility, 
  calculateDailyBonus, 
  createDefaultGameStats 
} from '../utils/userUtils';
import { ADMIN_ACCOUNTS, GAME_DEFAULTS, DEFAULT_ITEMS, NOTIFICATION_MESSAGES } from '../constants/appConstants';

export function useUserManager() {
  const [user, setUser] = useState(null as User | null);

  // 📱 사용자 데이터 업데이트 (메모이제이션)
  const updateUser = useCallback((updatedUser: User) => {
    setUser(updatedUser);
    localStorage.setItem('game-user', JSON.stringify(updatedUser));
  }, []);

  // 🔐 관리자 확인 로직 (메모이제이션)
  const isAdminAccount = useCallback((nickname: string, password: string): boolean => {
    return ADMIN_ACCOUNTS.some(admin => 
      (admin.id === nickname && admin.password === password) ||
      nickname === 'Administrator'
    );
  }, []);

  // 👤 사용자 데이터 생성 (안정한 참조)
  const createUserData = useCallback((
    nickname: string, 
    password: string, 
    isSignup: boolean = false,
    inviteCode?: string
  ): User => {
    const isAdmin = isAdminAccount(nickname, password);
    // 레벨을 안전하게 보장: 숫자가 아니거나 1 미만일 경우 기본값 1 사용
    const rawLevel = isAdmin
      ? GAME_DEFAULTS.ADMIN_LEVEL
      : Math.floor(Math.random() * GAME_DEFAULTS.RANDOM_LEVEL_RANGE) + 1;
    const safeLevel = Number.isFinite(rawLevel) && rawLevel >= 1 ? rawLevel : 1;

    return {
      id: Date.now().toString(),
      nickname,
      goldBalance: isAdmin 
        ? GAME_DEFAULTS.ADMIN_GOLD 
        : isSignup 
          ? (inviteCode ? GAME_DEFAULTS.INVITE_BONUS : GAME_DEFAULTS.SIGNUP_BONUS)
          : GAME_DEFAULTS.BASIC_GOLD + Math.floor(Math.random() * GAME_DEFAULTS.RANDOM_GOLD_RANGE),
      level: safeLevel,
      experience: Math.floor(Math.random() * GAME_DEFAULTS.RANDOM_EXP_RANGE),
      maxExperience: GAME_DEFAULTS.BASE_MAX_EXP,
      dailyStreak: isSignup ? 1 : Math.floor(Math.random() * GAME_DEFAULTS.RANDOM_STREAK_RANGE),
      achievements: isSignup ? ['newcomer'] : ['first_login', 'level_5'],
      inventory: [isSignup ? DEFAULT_ITEMS.NEWCOMER : DEFAULT_ITEMS.BEGINNER],
      stats: {
        gamesPlayed: isSignup ? 0 : Math.floor(Math.random() * GAME_DEFAULTS.RANDOM_GAMES_RANGE),
        gamesWon: isSignup ? 0 : Math.floor(Math.random() * GAME_DEFAULTS.RANDOM_WINS_RANGE),
        highestScore: isSignup ? 0 : Math.floor(Math.random() * GAME_DEFAULTS.RANDOM_SCORE_RANGE),
        totalEarnings: isSignup ? 0 : Math.floor(Math.random() * GAME_DEFAULTS.RANDOM_EARNINGS_RANGE),
        winStreak: isSignup ? 0 : Math.floor(Math.random() * GAME_DEFAULTS.RANDOM_WIN_STREAK_RANGE),
        favoriteGame: isSignup ? '' : 'slot'
      },
      gameStats: createDefaultGameStats(),
      lastLogin: new Date(),
      totalPlayTime: isSignup ? 0 : Math.floor(Math.random() * GAME_DEFAULTS.RANDOM_PLAYTIME_RANGE) * 3600,
      isAdmin,
      registrationDate: new Date(),
      lastActivity: new Date(),
      deviceInfo: 'Web Browser',
      ipAddress: '192.168.1.1'
    };
  }, [isAdminAccount]);

  // 💾 저장된 사용자 복원 (안정한 참조)
  const restoreSavedUser = useCallback(() => {
    const savedUser = localStorage.getItem('game-user');
    if (!savedUser) return null;

    try {
      const userData = JSON.parse(savedUser);
      return ensureUserCompatibility(userData);
    } catch (error) {
      console.error('Failed to parse saved user data:', error);
      localStorage.removeItem('game-user');
      return null;
    }
  }, []);

  // 🎁 일일 보너스 처리 (안정한 참조)
  const processDailyBonus = useCallback((userData: User): { updatedUser: User; bonusGold: number } => {
    return calculateDailyBonus(userData);
  }, []);

  // 🔥 로그아웃 (안정한 참조)
  const logout = useCallback(() => {
    setUser(null);
    localStorage.removeItem('game-user');
  }, []);

  // 📊 공용 사용자 정보 (메모이제이션)
  const userInfo = useMemo(() => ({
    isLoggedIn: !!user,
    isAdmin: user?.isAdmin ?? false,
    goldBalance: user?.goldBalance ?? 0,
    level: user?.level ?? 1,
    nickname: user?.nickname ?? ''
  }), [user]);

  return {
    user,
    setUser,
    updateUser,
    isAdminAccount,
    createUserData,
    restoreSavedUser,
    processDailyBonus,
    logout,
    userInfo
  };
}