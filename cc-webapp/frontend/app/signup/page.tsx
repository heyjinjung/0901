'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { LoginScreen } from '../../components/LoginScreen';
import { api } from '../../lib/unifiedApi';
import { setTokens } from '../../utils/tokenStorage';

// Static metadata - moved to layout or use generateMetadata for client components
// export const metadata = {
//   title: 'Login - Casino-Club F2P',
//   description: 'Sign in to Casino-Club F2P and continue your play.',
// };

export default function LoginPage() {
  const router = useRouter();

  const handleLogin = async (nickname: string, password: string): Promise<boolean> => {
    try {
      console.log('[LoginPage] 로그인 시도:', { nickname, password: '***' });
      
      const response = await api.post('auth/login', {
        site_id: nickname,  // nickname을 site_id로 전송
        password,
      }, {
        auth: false  // 로그인 요청은 인증이 필요하지 않음
      });

      console.log('[LoginPage] 로그인 응답:', response);

      if (response.access_token) {
        // 토큰 저장 (localStorage)
        setTokens({
          access_token: response.access_token,
          refresh_token: response.refresh_token || null,
        });

        console.log('[LoginPage] 토큰 저장 완료, 쿠키 설정 중...');
        
        // 쿠키에도 토큰 저장 (미들웨어용) - 더 안전한 방법
        try {
          // 브라우저 환경에서만 쿠키 설정
          if (typeof document !== 'undefined') {
            // HttpOnly는 클라이언트에서 설정 불가능하므로 제거
            const cookieString = `auth_token=${response.access_token}; path=/; max-age=86400; SameSite=Lax`;
            document.cookie = cookieString;
            console.log('[LoginPage] 쿠키 설정 완료:', cookieString);
            
            // 설정 확인 (짧은 지연 후)
            setTimeout(() => {
              const allCookies = document.cookie;
              console.log('[LoginPage] 설정 후 모든 쿠키:', allCookies);
              const hasAuthToken = allCookies.includes('auth_token=');
              console.log('[LoginPage] auth_token 쿠키 존재:', hasAuthToken);
            }, 100);
          }
        } catch (error) {
          console.error('[LoginPage] 쿠키 설정 실패:', error);
        }

        // 로그인 성공 후 충분한 지연 시간 확보 (쿠키 설정 완료 대기)
        setTimeout(() => {
          console.log('[LoginPage] 페이지 이동 시작 - 쿠키 재확인:', document.cookie.includes('auth_token='));
          
          // 관리자 계정이면 관리자 페이지로, 아니면 메인 페이지로
          if (nickname === 'admin') {
            console.log('[LoginPage] 관리자 페이지로 이동: /admin');
            window.location.href = '/admin'; // 강제 새로고침으로 미들웨어 재실행
          } else {
            console.log('[LoginPage] 메인 페이지로 이동: /');
            window.location.href = '/'; // 강제 새로고침으로 미들웨어 재실행
          }
        }, 500); // 충분한 지연 시간 확보
        
        return true;
      }

      return false;
    } catch (error) {
      console.error('[LoginPage] 로그인 에러:', error);
      return false;
    }
  };

  return <LoginScreen onLogin={handleLogin} />;
}
