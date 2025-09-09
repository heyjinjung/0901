'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiLogTry, apiLogSuccess, apiLogFail } from '../utils/apiLogger';
import { 
  User, 
  Lock, 
  Eye, 
  EyeOff, 
  UserPlus,
  ArrowLeft,
  Mail,
  Phone,
  Gift,
  Gamepad2,
  AlertCircle,
  CheckCircle,
  Star
} from 'lucide-react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/Label';

interface SignupFormData {
  userId: string;
  nickname: string;
  phoneNumber: string;
  password: string;
  confirmPassword: string;
  inviteCode: string;
}

interface SignupScreenProps {
  onSignup?: (data: SignupFormData) => Promise<boolean>;
  onBackToLogin?: () => void;
  isLoading?: boolean;
}

export function SignupScreen({ 
  onSignup, 
  onBackToLogin,
  isLoading = false 
}: SignupScreenProps) {
  const [formData, setFormData] = useState({
    userId: '',
    nickname: '',
    phoneNumber: '',
    password: '',
    confirmPassword: '',
    inviteCode: ''
  } as SignupFormData);
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({} as Partial<SignupFormData>);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);

  const validateForm = (): boolean => {
    const newErrors: Partial<SignupFormData> = {};

    // User ID validation
    if (!formData.userId.trim()) {
      newErrors.userId = 'ID를 입력해주세요.';
    } else if (formData.userId.length < 4) {
      newErrors.userId = 'ID는 4자 이상이어야 합니다.';
    } else if (!/^[a-zA-Z0-9_]+$/.test(formData.userId)) {
      newErrors.userId = 'ID는 영문, 숫자, _만 사용할 수 있습니다.';
    }

    // Nickname validation
    if (!formData.nickname.trim()) {
      newErrors.nickname = '닉네임을 입력해주세요.';
    } else if (formData.nickname.length < 2) {
      newErrors.nickname = '닉네임은 2자 이상이어야 합니다.';
    }

    // Phone number validation
    if (!formData.phoneNumber.trim()) {
      newErrors.phoneNumber = '전화번호를 입력해주세요.';
    } else if (!/^[0-9-]+$/.test(formData.phoneNumber)) {
      newErrors.phoneNumber = '올바른 전화번호 형식이 아닙니다.';
    }

    // Password validation
    if (!formData.password.trim()) {
      newErrors.password = '비밀번호를 입력해주세요.';
    } else if (formData.password.length < 6) {
      newErrors.password = '비밀번호는 6자 이상이어야 합니다.';
    }

    // Confirm password validation
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = '비밀번호가 일치하지 않습니다.';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    apiLogTry('회원가입');
    if (!validateForm()) {
      apiLogFail('POST /api/auth/signup', '폼 검증 실패');
      return;
    }
    setIsSubmitting(true);
    try {
      const success = (await onSignup?.(formData)) ?? true;
      if (success) {
        apiLogSuccess('POST /api/auth/signup');
      } else {
        apiLogFail('POST /api/auth/signup', '잘못된 정보');
        setErrors({ userId: '회원가입 중 오류가 발생했습니다.' });
      }
    } catch (err) {
      apiLogFail('POST /api/auth/signup', err);
      setErrors({ userId: '회원가입 중 오류가 발생했습니다.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: keyof SignupFormData) => (
    e: any
  ) => {
    setFormData((prev: SignupFormData) => ({ ...prev, [field]: e.target.value }));
    if (errors[field]) {
      setErrors((prev: Partial<SignupFormData>) => ({ ...prev, [field]: undefined }));
    }
  };

  const nextStep = () => {
    if (currentStep === 1) {
      // Validate first step
      const step1Fields = ['userId', 'nickname', 'phoneNumber'];
      const hasErrors = step1Fields.some(field => {
        const key = field as keyof SignupFormData;
        if (!formData[key].trim()) {
          setErrors((prev: Partial<SignupFormData>) => ({ ...prev, [key]: '필수 입력 항목입니다.' }));
          return true;
        }
        return false;
      });
      
      if (!hasErrors) {
        setCurrentStep(2);
      }
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center mb-6">
      {[1, 2].map((step) => (
        <React.Fragment key={step}>
          <motion.div
            initial={false}
            animate={{
              backgroundColor: currentStep >= step ? '#ff006e' : '#2d2d3a',
              scale: currentStep === step ? 1.2 : 1
            }}
            className="w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium"
          >
            {currentStep > step ? <CheckCircle className="w-4 h-4" /> : step}
          </motion.div>
          {step < 2 && (
            <motion.div
              initial={false}
              animate={{
                backgroundColor: currentStep > step ? '#ff006e' : '#2d2d3a'
              }}
              className="w-16 h-1 mx-2"
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );

  const renderStep1 = () => (
    <motion.div
      key="step1"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-4"
    >
      {/* User ID */}
      <div className="space-y-2">
        <Label htmlFor="userId" className="text-foreground">
          사용자 ID *
        </Label>
        <div className="relative">
          <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <Input
            id="userId"
            type="text"
            value={formData.userId}
            onChange={handleInputChange('userId')}
            placeholder="영문, 숫자, _ 사용 가능"
            className={`pl-10 bg-input-background border-input-border focus:border-primary focus:ring-primary/20 text-foreground ${
              errors.userId ? 'border-error focus:border-error' : ''
            }`}
          />
        </div>
        {errors.userId && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-error text-sm flex items-center gap-1"
          >
            <AlertCircle className="w-3 h-3" />
            {errors.userId}
          </motion.p>
        )}
      </div>

      {/* Nickname */}
      <div className="space-y-2">
        <Label htmlFor="nickname" className="text-foreground">
          닉네임 *
        </Label>
        <div className="relative">
          <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <Input
            id="nickname"
            type="text"
            value={formData.nickname}
            onChange={handleInputChange('nickname')}
            placeholder="게임에서 사용할 닉네임"
            className={`pl-10 bg-input-background border-input-border focus:border-primary focus:ring-primary/20 text-foreground ${
              errors.nickname ? 'border-error focus:border-error' : ''
            }`}
          />
        </div>
        {errors.nickname && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-error text-sm flex items-center gap-1"
          >
            <AlertCircle className="w-3 h-3" />
            {errors.nickname}
          </motion.p>
        )}
      </div>

      {/* Phone Number */}
      <div className="space-y-2">
        <Label htmlFor="phoneNumber" className="text-foreground">
          전화번호 *
        </Label>
        <div className="relative">
          <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <Input
            id="phoneNumber"
            type="tel"
            value={formData.phoneNumber}
            onChange={handleInputChange('phoneNumber')}
            placeholder="010-1234-5678"
            className={`pl-10 bg-input-background border-input-border focus:border-primary focus:ring-primary/20 text-foreground ${
              errors.phoneNumber ? 'border-error focus:border-error' : ''
            }`}
          />
        </div>
        {errors.phoneNumber && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-error text-sm flex items-center gap-1"
          >
            <AlertCircle className="w-3 h-3" />
            {errors.phoneNumber}
          </motion.p>
        )}
      </div>

      <Button
        type="button"
        onClick={nextStep}
        className="w-full bg-gradient-game hover:opacity-90 text-white py-3 rounded-lg font-medium transition-all duration-200"
      >
        다음 단계
      </Button>
    </motion.div>
  );

  const renderStep2 = () => (
    <motion.div
      key="step2"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-4"
    >
      {/* Password */}
      <div className="space-y-2">
        <Label htmlFor="password" className="text-foreground">
          비밀번호 *
        </Label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <Input
            id="password"
            type={showPassword ? 'text' : 'password'}
            value={formData.password}
            onChange={handleInputChange('password')}
            placeholder="6자 이상의 비밀번호"
            className={`pl-10 pr-10 bg-input-background border-input-border focus:border-primary focus:ring-primary/20 text-foreground ${
              errors.password ? 'border-error focus:border-error' : ''
            }`}
          />
          <button
            aria-label={showPassword ? '비밀번호 숨기기' : '비밀번호 보이기'}
            title={showPassword ? '비밀번호 숨기기' : '비밀번호 보이기'}
            aria-pressed={showPassword}
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>
        {errors.password && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-error text-sm flex items-center gap-1"
          >
            <AlertCircle className="w-3 h-3" />
            {errors.password}
          </motion.p>
        )}
      </div>

      {/* Confirm Password */}
      <div className="space-y-2">
        <Label htmlFor="confirmPassword" className="text-foreground">
          비밀번호 확인 *
        </Label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <Input
            id="confirmPassword"
            type={showConfirmPassword ? 'text' : 'password'}
            value={formData.confirmPassword}
            onChange={handleInputChange('confirmPassword')}
            placeholder="비밀번호를 다시 입력하세요"
            className={`pl-10 pr-10 bg-input-background border-input-border focus:border-primary focus:ring-primary/20 text-foreground ${
              errors.confirmPassword ? 'border-error focus:border-error' : ''
            }`}
          />
          <button
            aria-label={showConfirmPassword ? '비밀번호 숨기기' : '비밀번호 보이기'}
            title={showConfirmPassword ? '비밀번호 숨기기' : '비밀번호 보이기'}
            aria-pressed={showConfirmPassword}
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
          >
            {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>
        {errors.confirmPassword && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-error text-sm flex items-center gap-1"
          >
            <AlertCircle className="w-3 h-3" />
            {errors.confirmPassword}
          </motion.p>
        )}
      </div>

      {/* Invite Code */}
      <div className="space-y-2">
        <Label htmlFor="inviteCode" className="text-foreground">
          초대코드 (선택사항)
        </Label>
        <div className="relative">
          <Gift className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          <Input
            id="inviteCode"
            type="text"
            value={formData.inviteCode}
            onChange={handleInputChange('inviteCode')}
            placeholder="초대코드가 있다면 입력하세요"
            className="pl-10 bg-input-background border-input-border focus:border-primary focus:ring-primary/20 text-foreground"
          />
        </div>
        <p className="text-xs text-muted-foreground">
          초대코드 입력 시 보너스 골드를 받을 수 있습니다!
        </p>
      </div>

      <div className="flex gap-3">
        <Button
          type="button"
          variant="outline"
          onClick={prevStep}
          className="flex-1 border-border-secondary hover:border-primary hover:bg-primary/10 text-foreground"
        >
          이전
        </Button>
        <Button
          type="submit"
          disabled={isSubmitting || isLoading}
          className="flex-2 bg-gradient-game hover:opacity-90 text-white py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 shadow-game"
        >
          {isSubmitting || isLoading ? (
            <>
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
              />
              회원가입 중...
            </>
          ) : (
            <>
              <UserPlus className="w-5 h-5" />
              회원가입 완료
            </>
          )}
        </Button>
      </div>
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-black to-primary/10 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0">
        {[...Array(12)].map((_, i) => (
          <motion.div
            key={i}
            initial={{ 
              opacity: 0,
              x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1920),
              y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 1080)
            }}
            animate={{ 
              opacity: [0, 0.2, 0],
              scale: [0, 1.5, 0],
              rotate: 360
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              delay: i * 0.8,
              ease: "easeInOut"
            }}
            className="absolute w-2 h-2 bg-gold rounded-full"
          />
        ))}
      </div>

      {/* Main Signup Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.6, type: "spring", stiffness: 100 }}
        className="w-full max-w-md"
      >
        <div className="glass-effect rounded-2xl p-8 shadow-game relative">
          {/* Back Button */}
          <motion.button
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            onClick={onBackToLogin}
            className="absolute top-4 left-4 p-2 text-muted-foreground hover:text-foreground transition-colors rounded-lg hover:bg-secondary/20"
            disabled={isSubmitting || isLoading}
          >
            <ArrowLeft className="w-5 h-5" />
          </motion.button>

          {/* Header */}
          <div className="text-center mb-8">
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: 0.2, duration: 0.8, type: "spring", stiffness: 120 }}
              className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-gold mb-4"
            >
              <Gamepad2 className="w-8 h-8 text-black" />
            </motion.div>
            
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-2xl font-bold text-gradient-gold mb-2"
            >
              회원가입
            </motion.h1>
          </div>

          {/* Step Indicator */}
          {renderStepIndicator()}

          {/* Form */}
          <form onSubmit={handleSubmit}>
            <AnimatePresence mode="wait">
              {currentStep === 1 ? renderStep1() : renderStep2()}
            </AnimatePresence>
          </form>

          {/* Decorative Elements */}
          <div className="absolute -top-2 -right-2">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
            >
              <Star className="w-6 h-6 text-primary/30" />
            </motion.div>
          </div>
          
          <div className="absolute -bottom-2 -left-2">
            <motion.div
              animate={{ rotate: -360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            >
              <Star className="w-4 h-4 text-gold/30" />
            </motion.div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}