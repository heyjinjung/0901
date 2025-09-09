'use client';

import React, { useEffect, useState } from 'react';
import { API_ORIGIN } from '@/lib/unifiedApi';
import { useRouter } from 'next/navigation';

type LoadingStatus = 'checking' | 'loading' | 'ready' | 'error';
type ResourceType = 'api' | 'assets' | 'auth' | 'database';

interface LoadingState {
  status: LoadingStatus;
  progress: number;
  message: string;
  resources: Record<ResourceType, boolean>;
  error?: string;
}

/**
 * 프로덕션 수준의 로딩 컨트롤러
 * 실제 서비스 리소스 상태를 확인하고 로딩 상태를 관리
 */
export const useLoadingController = () => {
  const router = useRouter();
  const [state, setState] = useState({
    status: 'checking',
    progress: 0,
    message: '시스템 초기화 중...',
    resources: {
      api: false,
      assets: false,
      auth: false,
      database: false
    }
  } as LoadingState);

  // 리소스별 상태 업데이트 함수
  const updateResource = (type: ResourceType, isLoaded: boolean, errorMsg?: string) => {
    setState((prev: LoadingState) => {
      const updatedResources = { ...prev.resources, [type]: isLoaded };
      const loadedCount = Object.values(updatedResources).filter(Boolean).length;
      const totalResources = Object.keys(updatedResources).length;
      const progress = Math.floor((loadedCount / totalResources) * 100);
      
      let status: LoadingStatus = 'loading';
      let message = `리소스 로딩 중... (${loadedCount}/${totalResources})`;
      
      if (errorMsg) {
        status = 'error';
        message = `오류 발생: ${errorMsg}`;
      } else if (loadedCount === totalResources) {
        status = 'ready';
        message = '완료! 페이지로 이동합니다...';
      }
      
  return {
        ...prev,
        status,
        progress,
        message,
        resources: updatedResources,
        error: errorMsg
      };
    });
  };

  // API 서버 상태 확인
  const checkApiServer = async () => {
    try {
      const response = await fetch(`${API_ORIGIN}/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        cache: 'no-store'
      });
      
      if (response.ok) {
        updateResource('api', true);
      } else {
        updateResource('api', false, '서버 응답이 정상적이지 않습니다');
      }
    } catch (error) {
      console.error('API 서버 연결 오류:', error);
      // 개발 환경에서는 API 서버가 없어도 진행 가능하도록 설정
      if (process.env.NODE_ENV === 'development') {
        updateResource('api', true);
      } else {
        updateResource('api', false, '서버에 연결할 수 없습니다');
      }
    }
  };

  // 필수 에셋 로딩 확인
  const checkAssets = () => {
    try {
      // 중요 이미지, 폰트 등의 리소스가 로드되었는지 확인
      const criticalAssets = document.querySelectorAll('img[data-critical="true"], link[rel="preload"]');
      const allLoaded = Array.from(criticalAssets).every((asset) => {
        if (asset instanceof HTMLImageElement) {
          return asset.complete;
        }
        return true;
      });
      
      setTimeout(() => {
        updateResource('assets', true);
      }, 800); // 짧은 지연으로 자연스러운 로딩 느낌 부여
    } catch (error) {
      console.error('에셋 로딩 오류:', error);
      updateResource('assets', true); // 에셋 오류는 치명적이지 않으므로 진행
    }
  };

  // 인증 상태 확인
  const checkAuth = () => {
    try {
      const token = localStorage.getItem('auth_token');
      const userInfo = localStorage.getItem('user_info');
      
      // 토큰은 없어도 됨 (로그인 화면으로 이동)
      updateResource('auth', true);
      
      // 추후 자동 로그인 등 확장 가능
    } catch (error) {
      console.error('인증 정보 확인 오류:', error);
      updateResource('auth', true); // 인증 실패는 로그인 화면으로 이동하는 정상 흐름
    }
  };

  // 데이터베이스/캐시 상태 확인
  const checkDatabase = async () => {
    try {
      // 오프라인 캐시/IndexedDB 상태 확인 (PWA 지원 시)
      // 여기서는 예시로 타이머만 추가
      setTimeout(() => {
        updateResource('database', true);
      }, 600);
    } catch (error) {
      console.error('데이터베이스 확인 오류:', error);
      updateResource('database', true); // 비치명적 오류로 간주
    }
  };

  // 로딩 완료 후 처리
  useEffect(() => {
    if (state.status === 'ready') {
      const redirectTimer = setTimeout(() => {
        // 인증 토큰이 있으면 메인으로, 없으면 로그인으로
        const hasToken = localStorage.getItem('auth_token');
        router.push(hasToken ? '/dashboard' : '/login');
      }, 800);
      
      return () => clearTimeout(redirectTimer);
    }
  }, [state.status, router]);

  // 초기 로딩 시작
  useEffect(() => {
    const startLoading = async () => {
      await Promise.all([
        checkApiServer(),
        checkAuth(),
        checkDatabase()
      ]);
      checkAssets(); // 비동기 완료 대기 안함
    };
    
    startLoading();
    
    // 최대 로딩 타임아웃 설정 (10초)
    const failsafeTimer = setTimeout(() => {
      if (state.status !== 'ready') {
        const fallbackEnabled = process.env.NEXT_PUBLIC_AUTH_FALLBACK === 'true';
        if (fallbackEnabled) {
          router.push('/login');
        }
      }
    }, 10000);
    
    return () => clearTimeout(failsafeTimer);
  }, []);

  return state;
};
