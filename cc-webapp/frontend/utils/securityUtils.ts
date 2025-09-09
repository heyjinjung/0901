import { User } from '../types';

// XSS 방지를 위한 입력 값 정화
export function sanitizeInput(input: string): string {
  if (typeof input !== 'string') return '';
  
  return input
    .replace(/[<>]/g, '') // Remove angle brackets
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+=/gi, '') // Remove event handlers
    .trim()
    .slice(0, 1000); // Limit length
}

// HTML 이스케이프
export function escapeHtml(unsafe: string): string {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// 닉네임 검증
export function validateNickname(nickname: string): { isValid: boolean; error?: string } {
  const sanitized = sanitizeInput(nickname);
  
  if (sanitized.length < 2) {
    return { isValid: false, error: '닉네임은 2자 이상이어야 합니다.' };
  }
  
  if (sanitized.length > 20) {
    return { isValid: false, error: '닉네임은 20자 이하여야 합니다.' };
  }
  
  // 특수문자 제한
  const allowedPattern = /^[a-zA-Z0-9가-힣_-]+$/;
  if (!allowedPattern.test(sanitized)) {
    return { isValid: false, error: '닉네임에는 영문, 숫자, 한글, _, - 만 사용할 수 있습니다.' };
  }
  
  // 금지어 체크
  const bannedWords = ['admin', 'administrator', 'root', 'system', 'null', 'undefined'];
  if (bannedWords.some(word => sanitized.toLowerCase().includes(word))) {
    return { isValid: false, error: '사용할 수 없는 닉네임입니다.' };
  }
  
  return { isValid: true };
}

// 비밀번호 검증
export function validatePassword(password: string): { isValid: boolean; error?: string } {
  if (password.length < 4) {
    return { isValid: false, error: '비밀번호는 4자 이상이어야 합니다.' };
  }
  
  if (password.length > 50) {
    return { isValid: false, error: '비밀번호는 50자 이하여야 합니다.' };
  }
  
  return { isValid: true };
}

// 이메일 검증
export function validateEmail(email: string): { isValid: boolean; error?: string } {
  const sanitized = sanitizeInput(email);
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (!emailPattern.test(sanitized)) {
    return { isValid: false, error: '올바른 이메일 형식이 아닙니다.' };
  }
  
  return { isValid: true };
}

// 사용자 데이터 검증
export function validateUser(user: any): User {
  if (!user || typeof user !== 'object') {
    throw new Error('Invalid user data');
  }
  
  // 필수 필드 검증
  const requiredFields = ['id', 'nickname', 'goldBalance', 'level'];
  for (const field of requiredFields) {
    if (user[field] === undefined || user[field] === null) {
      throw new Error(`Missing required field: ${field}`);
    }
  }
  
  // 타입 검증 및 정화
  const validatedUser: User = {
    id: sanitizeInput(String(user.id)),
    nickname: sanitizeInput(String(user.nickname)),
    goldBalance: Math.max(0, Math.min(999999999, Number(user.goldBalance) || 0)),
    level: Math.max(1, Math.min(999, Number(user.level) || 1)),
    experience: Math.max(0, Number(user.experience) || 0),
    maxExperience: Math.max(1, Number(user.maxExperience) || 1000),
    dailyStreak: Math.max(0, Math.min(365, Number(user.dailyStreak) || 0)),
    achievements: Array.isArray(user.achievements) ? user.achievements.slice(0, 100) : [],
    inventory: Array.isArray(user.inventory) ? user.inventory.slice(0, 1000) : [],
    stats: {
      gamesPlayed: Math.max(0, Number(user.stats?.gamesPlayed) || 0),
      gamesWon: Math.max(0, Number(user.stats?.gamesWon) || 0),
      highestScore: Math.max(0, Number(user.stats?.highestScore) || 0),
      totalEarnings: Math.max(0, Number(user.stats?.totalEarnings) || 0),
      winStreak: Math.max(0, Number(user.stats?.winStreak) || 0),
      favoriteGame: sanitizeInput(String(user.stats?.favoriteGame || ''))
    },
    lastLogin: user.lastLogin instanceof Date ? user.lastLogin : new Date(),
    totalPlayTime: Math.max(0, Number(user.totalPlayTime) || 0),
    gameStats: user.gameStats || {
      slot: { spins: 0, jackpots: 0, biggestWin: 0, totalWinnings: 0 },
      rps: { matches: 0, wins: 0, draws: 0, winStreak: 0 },
      roulette: { spins: 0, wins: 0, biggestWin: 0, favoriteNumber: 7 },
      gacha: { pulls: 0, legendaryCount: 0, epicCount: 0, totalSpent: 0 }
    },
    isAdmin: Boolean(user.isAdmin),
    registrationDate: user.registrationDate instanceof Date ? user.registrationDate : new Date(),
    lastActivity: user.lastActivity instanceof Date ? user.lastActivity : new Date(),
    deviceInfo: sanitizeInput(String(user.deviceInfo || 'Unknown')),
    ipAddress: sanitizeInput(String(user.ipAddress || '127.0.0.1'))
  };
  
  return validatedUser;
}

// 관리자 권한 검증
export function validateAdminAccess(user: User | null): boolean {
  if (!user) return false;
  
  return Boolean(user.isAdmin) && 
         (user.nickname === 'md001' || 
          user.nickname === 'admin' || 
          user.nickname === 'Administrator');
}

// 세션 검증
export function validateSession(sessionId: string, maxAge: number = 24 * 60 * 60 * 1000): boolean {
  try {
    const timestamp = parseInt(sessionId);
    const now = Date.now();
    return (now - timestamp) < maxAge;
  } catch {
    return false;
  }
}

// 숫자 범위 검증
export function validateNumberRange(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

// 입력 길이 제한
export function limitInputLength(input: string, maxLength: number): string {
  return sanitizeInput(input).slice(0, maxLength);
}

// 파일 업로드 검증
export function validateFileUpload(file: File): { isValid: boolean; error?: string } {
  // 파일 크기 제한 (10MB)
  const maxSize = 10 * 1024 * 1024;
  if (file.size > maxSize) {
    return { isValid: false, error: '파일 크기는 10MB 이하여야 합니다.' };
  }
  
  // 허용된 파일 확장자
  const allowedExtensions = ['.xlsx', '.xls', '.csv'];
  const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
  
  if (!allowedExtensions.includes(fileExtension)) {
    return { isValid: false, error: '엑셀 파일(.xlsx, .xls) 또는 CSV 파일만 업로드 가능합니다.' };
  }
  
  return { isValid: true };
}

// 로깅을 위한 안전한 데이터 추출
export function extractSafeLogData(data: any): Record<string, any> {
  const safeData: Record<string, any> = {};
  
  for (const [key, value] of Object.entries(data)) {
    // 민감한 정보 제외
    if (['password', 'token', 'secret', 'key'].some(sensitive => key.toLowerCase().includes(sensitive))) {
      safeData[key] = '[REDACTED]';
    } else if (typeof value === 'string') {
      safeData[key] = sanitizeInput(value);
    } else if (typeof value === 'number') {
      safeData[key] = value;
    } else if (typeof value === 'boolean') {
      safeData[key] = value;
    } else if (value instanceof Date) {
      safeData[key] = value.toISOString();
    } else {
      safeData[key] = '[COMPLEX_OBJECT]';
    }
  }
  
  return safeData;
}