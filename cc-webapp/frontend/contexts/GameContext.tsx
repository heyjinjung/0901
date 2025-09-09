'use client';

import React, { createContext, useContext, useReducer, useCallback, useEffect } from 'react';
import { User } from '../types';
import { ensureUserCompatibility, calculateDailyBonus } from '../utils/userUtils';
import { validateUser, sanitizeInput } from '../utils/securityUtils';

interface GameState {
  user: User | null;
  notifications: string[];
  isLoading: boolean;
  error: string | null;
  lastActivity: Date;
  sessionId: string;
}

type GameAction =
  | { type: 'SET_USER'; payload: User }
  | { type: 'UPDATE_USER'; payload: Partial<User> }
  | { type: 'ADD_NOTIFICATION'; payload: string }
  | { type: 'REMOVE_NOTIFICATION'; payload: number }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_NOTIFICATIONS' }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_ACTIVITY' };

const initialState: GameState = {
  user: null,
  notifications: [],
  isLoading: false,
  error: null,
  lastActivity: new Date(),
  sessionId: Date.now().toString()
};

function gameReducer(state: GameState, action: GameAction): GameState {
  switch (action.type) {
    case 'SET_USER':
      return {
        ...state,
        user: action.payload,
        error: null,
        lastActivity: new Date()
      };
    
    case 'UPDATE_USER':
      if (!state.user) return state;
      return {
        ...state,
        user: { ...state.user, ...action.payload },
        lastActivity: new Date()
      };
    
    case 'ADD_NOTIFICATION':
      return {
        ...state,
        notifications: [action.payload, ...state.notifications.slice(0, 4)]
      };
    
    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        notifications: state.notifications.filter((_, index) => index !== action.payload)
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload
      };
    
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        isLoading: false
      };
    
    case 'CLEAR_NOTIFICATIONS':
      return {
        ...state,
        notifications: []
      };
    
    case 'LOGOUT':
      return {
        ...initialState,
        sessionId: Date.now().toString()
      };
    
    case 'UPDATE_ACTIVITY':
      return {
        ...state,
        lastActivity: new Date()
      };
    
    default:
      return state;
  }
}

interface GameContextType extends GameState {
  setUser: (user: User) => void;
  updateUser: (updates: Partial<User>) => void;
  addNotification: (message: string) => void;
  removeNotification: (index: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearNotifications: () => void;
  logout: () => void;
  persistUser: (user: User) => Promise<void>;
  loadUser: () => Promise<User | null>;
}

// React 19 disallows call-site generics on certain helper functions (createContext).
// Use an assertion-style initializer to provide the type without using a call-site generic.
const GameContext = createContext(undefined as unknown as GameContextType | undefined);

interface GameProviderProps {
  children: React.ReactNode;
}

export function GameProvider({ children }: GameProviderProps) {
  const [state, dispatch] = useReducer(gameReducer, initialState);

  // Auto-save user data
  const persistUser = useCallback(async (user: User): Promise<void> => {
    try {
      const validatedUser = validateUser(user);
      const serializedUser = JSON.stringify({
        ...validatedUser,
        lastLogin: validatedUser.lastLogin.toISOString(),
        registrationDate: validatedUser.registrationDate?.toISOString(),
        lastActivity: validatedUser.lastActivity?.toISOString()
      });
      localStorage.setItem('game-user', serializedUser);
    } catch (error) {
      console.error('Failed to persist user:', error);
      dispatch({ type: 'SET_ERROR', payload: '사용자 데이터 저장에 실패했습니다.' });
    }
  }, []);

  // Load user data
  const loadUser = useCallback(async (): Promise<User | null> => {
    try {
      const savedUser = localStorage.getItem('game-user');
      if (!savedUser) return null;

      const userData = JSON.parse(savedUser);
      
      // Convert date strings back to Date objects
      if (userData.lastLogin) userData.lastLogin = new Date(userData.lastLogin);
      if (userData.registrationDate) userData.registrationDate = new Date(userData.registrationDate);
      if (userData.lastActivity) userData.lastActivity = new Date(userData.lastActivity);

      const compatibleUser = ensureUserCompatibility(userData);
      const validatedUser = validateUser(compatibleUser);
      
      return validatedUser;
    } catch (error) {
      console.error('Failed to load user:', error);
      localStorage.removeItem('game-user');
      dispatch({ type: 'SET_ERROR', payload: '사용자 데이터 로드에 실패했습니다.' });
      return null;
    }
  }, []);

  // Actions
  const setUser = useCallback((user: User) => {
    dispatch({ type: 'SET_USER', payload: user });
    persistUser(user);
  }, [persistUser]);

  const updateUser = useCallback((updates: Partial<User>) => {
    dispatch({ type: 'UPDATE_USER', payload: updates });
    if (state.user) {
      const updatedUser = { ...state.user, ...updates };
      persistUser(updatedUser);
    }
  }, [state.user, persistUser]);

  const addNotification = useCallback((message: string) => {
    const sanitizedMessage = sanitizeInput(message);
    dispatch({ type: 'ADD_NOTIFICATION', payload: sanitizedMessage });
    
    // Auto-remove notification
    setTimeout(() => {
      dispatch({ type: 'REMOVE_NOTIFICATION', payload: 0 });
    }, 7000);
  }, []);

  const removeNotification = useCallback((index: number) => {
    dispatch({ type: 'REMOVE_NOTIFICATION', payload: index });
  }, []);

  const setLoading = useCallback((loading: boolean) => {
    dispatch({ type: 'SET_LOADING', payload: loading });
  }, []);

  const setError = useCallback((error: string | null) => {
    dispatch({ type: 'SET_ERROR', payload: error });
  }, []);

  const clearNotifications = useCallback(() => {
    dispatch({ type: 'CLEAR_NOTIFICATIONS' });
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('game-user');
    dispatch({ type: 'LOGOUT' });
  }, []);

  // Activity tracking
  useEffect(() => {
    const activityTimer = setInterval(() => {
      dispatch({ type: 'UPDATE_ACTIVITY' });
    }, 60000); // Update activity every minute

    return () => clearInterval(activityTimer);
  }, []);

  // Auto-load user on mount
  useEffect(() => {
    const initializeUser = async () => {
      const user = await loadUser();
      if (user) {
        dispatch({ type: 'SET_USER', payload: user });
        
        // Check for daily bonus
        const lastLogin = new Date(user.lastLogin);
        const today = new Date();
        const timeDiff = today.getTime() - lastLogin.getTime();
        const daysDiff = Math.floor(timeDiff / (1000 * 3600 * 24));
        
        if (daysDiff >= 1) {
          const { updatedUser, bonusGold } = calculateDailyBonus(user);
          dispatch({ type: 'SET_USER', payload: updatedUser });
          persistUser(updatedUser);
          addNotification(`🎁 일일 로그인 보너스 ${bonusGold.toLocaleString()}G 획득! (연속 ${updatedUser.dailyStreak}일)`);
        }
      }
    };

    initializeUser();
  }, [loadUser, persistUser, addNotification]);

  const contextValue: GameContextType = {
    ...state,
    setUser,
    updateUser,
    addNotification,
    removeNotification,
    setLoading,
    setError,
    clearNotifications,
    logout,
    persistUser,
    loadUser
  };

  return (
    <GameContext.Provider value={contextValue}>
      {children}
    </GameContext.Provider>
  );
}

export function useGame(): GameContextType {
  const context = useContext(GameContext);
  if (context === undefined) {
    throw new Error('useGame must be used within a GameProvider');
  }
  return context;
}