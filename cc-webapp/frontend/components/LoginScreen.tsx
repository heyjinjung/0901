'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiLogTry, apiLogSuccess, apiLogFail } from '../utils/apiLogger';
import { 
  User, 
  Lock, 
  Eye, 
  EyeOff, 
  LogIn, 
  UserPlus,
  Gamepad2,
  Shield,
  Star,
  AlertCircle
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/Label';

interface LoginScreenProps {
  onLogin?: (nickname: string, password: string) => Promise<boolean>;
  onSwitchToSignup?: () => void;
  onAdminAccess?: () => void;
  isLoading?: boolean;
}

export function LoginScreen({ 
  onLogin, 
  onSwitchToSignup, 
  onAdminAccess,
  isLoading = false 
}: LoginScreenProps) {
  const [formData, setFormData] = useState({
    nickname: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 🎯 디버깅용 로그
  React.useEffect(() => {
    console.log('[LoginScreen] 🔧 DEBUG - props 타입 확인:', {
      onSwitchToSignup: typeof onSwitchToSignup,
      onAdminAccess: typeof onAdminAccess,
      isOnSwitchToSignupFunction: typeof onSwitchToSignup === 'function',
      isOnAdminAccessFunction: typeof onAdminAccess === 'function'
    });
    console.log('[LoginScreen] 상태 업데이트:', {
      isLoading,
      isSubmitting,
      hasOnSwitchToSignup: !!onSwitchToSignup,
      hasOnAdminAccess: !!onAdminAccess,
      disabled: isSubmitting || isLoading
    });
  }, [isLoading, isSubmitting, onSwitchToSignup, onAdminAccess]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    console.log('[LoginScreen] handleLogin 시작, onLogin 함수:', !!onLogin);
    apiLogTry('POST /api/auth/login');

    const { nickname, password } = formData;
    console.log('[LoginScreen] 입력값:', { nickname, password: '***' });

    if (!nickname || !password) {
      setError('모든 필드를 입력해주세요.');
      apiLogFail('POST /api/auth/login', '필드 누락');
      return;
    }

    setIsSubmitting(true);
    try {
      console.log('[LoginScreen] onLogin 호출 직전');
      const success = onLogin ? await onLogin(nickname, password) : false;
      console.log('[LoginScreen] onLogin 결과:', success);
      if (success) {
        apiLogSuccess('POST /api/auth/login');
      } else {
        apiLogFail('POST /api/auth/login', '잘못된 정보 또는 서버 거부');
        setError('로그인 실패: 자격 증명이 올바르지 않거나 서버에서 거부되었습니다.');
      }
    } catch (err: any) {
      apiLogFail('POST /api/auth/login', err?.message || err);
      setError('로그인 중 시스템 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange =
    (field: keyof typeof formData) => (e: { target: { value: string } }) => {
      setFormData((prev: typeof formData) => ({ ...prev, [field]: e.target.value }));
      if (error) setError('');
    };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-black to-primary/10 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0">
        {[...Array(15)].map((_, i) => {
          // SSR에서는 고정값, CSR에서는 useEffect로 랜덤 위치 적용
          const [pos, setPos] = useState({ x: 0, y: 0 });
          useEffect(() => {
            if (typeof window !== 'undefined') {
              setPos({
                x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1920),
                y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 1080),
              });
            }
          }, []);
          return (
            <motion.div
              key={i}
              initial={{
                opacity: 0,
                x: pos.x,
                y: pos.y,
              }}
              animate={{
                opacity: [0, 0.3, 0],
                scale: [0, 1, 0],
                rotate: 360,
              }}
              transition={{
                duration: 8,
                repeat: Infinity,
                delay: i * 0.5,
                ease: 'easeInOut',
              }}
              className="absolute w-32 h-32 bg-primary/10 rounded-full blur-2xl"
            />
          );
        })}
      </div>

      {/* Main Login Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.6, type: 'spring', stiffness: 100 }}
        className="w-full max-w-md"
      >
        <div className="glass-effect rounded-2xl p-8 shadow-game relative">
          {/* Header */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.2, duration: 0.8, type: 'spring', stiffness: 120 }}
              className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-game mb-4"
            >
              <Gamepad2 className="w-8 h-8 text-white" />
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-2xl font-bold text-gradient-primary mb-2"
            >
              로그인
            </motion.h1>
          </div>

          {/* Error Message */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-6 p-3 bg-error/10 border border-error/20 rounded-lg flex items-center gap-2 text-error text-sm"
              >
                <AlertCircle className="w-4 h-4 shrink-0" />
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Login Form */}
          <motion.form
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            onSubmit={handleLogin}
            className="space-y-6"
          >
            {/* Nickname Field */}
            <div className="space-y-2">
              <Label htmlFor="nickname" className="text-foreground">
                사용자 ID
              </Label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  id="nickname"
                  type="text"
                  value={formData.nickname}
                  onChange={handleInputChange('nickname')}
                  placeholder="user001, admin 등 사용자 ID를 입력하세요"
                  className="pl-10 bg-input-background border-input-border focus:border-primary focus:ring-primary/20 text-foreground"
                  disabled={isSubmitting || isLoading}
                />
              </div>
              <p className="text-xs text-muted-foreground">
                💡 테스트 계정: admin/123456, user001-004/123455
              </p>
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <Label htmlFor="password" className="text-foreground">
                비밀번호
              </Label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleInputChange('password')}
                  placeholder="비밀번호를 입력하세요"
                  className="pl-10 pr-10 bg-input-background border-input-border focus:border-primary focus:ring-primary/20 text-foreground"
                  disabled={isSubmitting || isLoading}
                />
                <button
                  aria-label={showPassword ? '비밀번호 숨기기' : '비밀번호 보이기'}
                  title={showPassword ? '비밀번호 숨기기' : '비밀번호 보이기'}
                  aria-pressed={showPassword}
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  disabled={isSubmitting || isLoading}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Login Button */}
            <Button
              type="submit"
              disabled={isSubmitting || isLoading}
              className="w-full bg-gradient-game hover:opacity-90 text-white py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 shadow-game"
            >
              {isSubmitting || isLoading ? (
                <>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                  />
                  로그인 중...
                </>
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  로그인
                </>
              )}
            </Button>
          </motion.form>

          {/* Divider */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1 }}
            className="relative my-6"
          >
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border-secondary" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-card text-muted-foreground">또는</span>
            </div>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2 }}
            className="space-y-3"
          >
            {/* Signup Button */}
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                console.log('[LoginScreen] 회원가입 버튼 클릭됨, onSwitchToSignup 함수:', !!onSwitchToSignup);
                onSwitchToSignup?.();
              }}
              className="w-full border-border-secondary hover:border-primary hover:bg-primary/10 text-foreground flex items-center justify-center gap-2"
              disabled={isSubmitting || isLoading}
            >
              <UserPlus className="w-5 h-5" />
              회원가입
            </Button>

            {/* Admin Access Button */}
            <button
              type="button"
              onClick={() => {
                console.log('[LoginScreen] 관리자 로그인 버튼 클릭됨, onAdminAccess 함수:', !!onAdminAccess);
                onAdminAccess?.();
              }}
              className="w-full p-2 text-xs text-muted-foreground hover:text-primary transition-colors flex items-center justify-center gap-1"
              disabled={isSubmitting || isLoading}
            >
              <Shield className="w-3 h-3" />
              관리자 로그인
            </button>
          </motion.div>

          {/* Decorative Elements */}
          <div className="absolute -top-2 -right-2">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
            >
              <Star className="w-6 h-6 text-gold/30" />
            </motion.div>
          </div>

          <div className="absolute -bottom-2 -left-2">
            <motion.div
              animate={{ rotate: -360 }}
              transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
            >
              <Star className="w-4 h-4 text-primary/30" />
            </motion.div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}