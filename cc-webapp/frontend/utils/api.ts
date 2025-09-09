"use client";

/**
 * API 클라이언트 
 * 백엔드와의 통신을 처리하는 함수들
 */

// 개발 기본값: IPv4 루프백을 사용하여 호스트의 IPv6 문제 회피
const API_BASE_URL = 'http://127.0.0.1:8000'; // 백엔드 API 주소 (필요에 따라 수정)

// 개발 모드 여부 확인
const IS_DEV = process.env.NODE_ENV === 'development';
 /**
  * DEPRECATION NOTICE (통합 예정)
  * 이 파일은 unifiedApi(../lib/unifiedApi.ts) 도입으로 단계적 제거 예정입니다.
  * - /api prefix 자동 처리 없음 → 신규 코드에서는 사용 금지
  * - 토큰 스토리지 중복 발생 → tokenStorage + unifiedApi 사용
  * 제거 목표: 2025-09-15
  */
/**
 * API 로깅 유틸리티
 * 개발 단계에서만 동작하며, 프로덕션 빌드에서는 자동으로 제거됨
 */
export const apiLogger = {
  /**
   * API 요청 시작 로깅
   * @param method HTTP 메소드
   * @param endpoint API 엔드포인트
   * @param data 요청 데이터
   */
  request: (method: string, endpoint: string, data?: any): void => {
    if (IS_DEV) {
      const timestamp = new Date().toLocaleTimeString('ko-KR');
      console.group(`%c🚀 API 요청 [${timestamp}]`, 'color: #e6005e; font-weight: bold;');
      console.log(`%c📍 ${method} ${endpoint}`, 'color: #ff69b4;');
      if (data) console.log('%c📦 요청 데이터:', 'color: #666;', data);
      console.groupEnd();
    }
  },

  /**
   * API 응답 로깅
   * @param method HTTP 메소드
   * @param endpoint API 엔드포인트
   * @param status HTTP 상태 코드
   * @param data 응답 데이터
   * @param duration 요청-응답 소요 시간(ms)
   */
  response: (method: string, endpoint: string, status: number, data: any, duration: number): void => {
    if (IS_DEV) {
      const timestamp = new Date().toLocaleTimeString('ko-KR');
      const isSuccess = status >= 200 && status < 400;
      
      console.group(
        `%c${isSuccess ? '✅' : '❌'} API 응답 [${timestamp}]`, 
        `color: ${isSuccess ? '#4CAF50' : '#F44336'}; font-weight: bold;`
      );
      console.log(`%c📍 ${method} ${endpoint}`, 'color: #ff69b4;');
      console.log(`%c📊 상태: ${status}`, `color: ${isSuccess ? '#4CAF50' : '#F44336'};`);
      console.log(`%c⏱️ 소요 시간: ${duration}ms`, 'color: #666;');
      console.log('%c📦 응답 데이터:', 'color: #666;', data);
      console.groupEnd();
    }
  },

  /**
   * API 에러 로깅
   * @param method HTTP 메소드
   * @param endpoint API 엔드포인트
   * @param error 에러 객체
   */
  error: (method: string, endpoint: string, error: any): void => {
    if (IS_DEV) {
      const timestamp = new Date().toLocaleTimeString('ko-KR');
      
      console.group('%c❌ API 에러 [' + timestamp + ']', 'color: #F44336; font-weight: bold;');
      console.log(`%c📍 ${method} ${endpoint}`, 'color: #ff69b4;');
      console.error('%c💥 에러 내용:', 'color: #F44336;', error);
      console.groupEnd();
    }
  }
};

// 토큰 관리
export const getTokens = () => {
  const accessToken = localStorage.getItem('access_token');
  const refreshToken = localStorage.getItem('refresh_token');
  return { accessToken, refreshToken };
};

export const setTokens = (accessToken: string, refreshToken: string) => {
  localStorage.setItem('access_token', accessToken);
  localStorage.setItem('refresh_token', refreshToken);
};

export const clearTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

// 기본 API 요청 함수
const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const method = options.method || 'GET';
  const requestData = options.body ? JSON.parse(options.body as string) : undefined;
  const startTime = Date.now();
  
  try {
    // 요청 로깅
    apiLogger.request(method, endpoint, requestData);
    
    const { accessToken } = getTokens();
    
    const headers = {
      'Content-Type': 'application/json',
      ...(accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}),
      ...(options.headers || {})
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers
    });

    // 401 에러 시 토큰 리프레시 시도
    if (response.status === 401) {
      apiLogger.error(method, endpoint, '인증 토큰이 만료되었습니다. 토큰 갱신 시도 중...');
      
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        apiLogger.request(method, endpoint, requestData);
        return apiRequest(endpoint, options); // 토큰 갱신 후 원래 요청 재시도
      } else {
        clearTokens(); // 리프레시 실패 시 토큰 제거
        throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.');
      }
    }

    const data = await response.json();
    const duration = Date.now() - startTime;
    
    // 응답 로깅
    apiLogger.response(method, endpoint, response.status, data, duration);
    
    if (!response.ok) {
      throw new Error(data.detail || '요청 처리 중 오류가 발생했습니다.');
    }
    
    return data;
  } catch (error) {
    // 에러 로깅
    apiLogger.error(method, endpoint, error);
    throw error;
  }
};

// 토큰 갱신 함수
export const refreshAccessToken = async (): Promise<boolean> => {
  const startTime = Date.now();
  const endpoint = '/auth/refresh';
  const method = 'POST';
  
  try {
    apiLogger.request(method, endpoint, { message: '토큰 갱신 시도 중...' });
    
    const { refreshToken } = getTokens();
    if (!refreshToken) {
      apiLogger.error(method, endpoint, '리프레시 토큰이 없습니다.');
      return false;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken })
    });

    const data = await response.json();
    const duration = Date.now() - startTime;
    
    if (!response.ok) {
      apiLogger.error(method, endpoint, '토큰 갱신 실패: 서버 응답 에러');
      return false;
    }

    apiLogger.response(method, endpoint, response.status, { message: '토큰 갱신 성공' }, duration);
    
    setTokens(data.access_token, refreshToken); // 리프레시 토큰은 유지
    return true;
  } catch (error) {
    apiLogger.error(method, endpoint, error);
    return false;
  }
};

// 인증 관련 API 함수들
export const authApi = {
  // 로그인
  login: async (siteId: string, password: string, deviceInfo?: string) => {
    return await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ site_id: siteId, password, device_info: deviceInfo })
    });
  },
  
  // 회원가입
  register: async (inviteCode: string, nickname: string, siteId: string, phoneNumber: string, password: string) => {
    return await apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ 
        invite_code: inviteCode,
        nickname, 
        site_id: siteId, 
        phone_number: phoneNumber, 
        password 
      })
    });
  },

  // 현재 사용자 정보 조회
  getCurrentUser: async () => {
    return await apiRequest('/auth/me');
  },

  // 로그아웃
  logout: async () => {
    return await apiRequest('/auth/logout', { method: 'POST' });
  },

  // 모든 세션 로그아웃
  logoutAll: async () => {
    return await apiRequest('/auth/logout-all', { method: 'POST' });
  },

  // 초대코드 확인
  checkInviteCode: async (code: string) => {
    return await apiRequest(`/auth/check-invite/${code}`);
  },

  // 초대코드 생성 (관리자 전용)
  createInviteCodes: async (count: number = 1) => {
    return await apiRequest('/auth/admin/create-invite', {
      method: 'POST',
      body: JSON.stringify({ count })
    });
  },

  // 인증 시스템 헬스 체크
  healthCheck: async () => {
    return await apiRequest('/auth/health');
  }
};

export default apiRequest;
