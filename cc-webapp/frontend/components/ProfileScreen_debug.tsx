'use client';

import React, { useState, useEffect } from 'react';
import { ArrowLeft } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';
import { api as unifiedApi } from '@/lib/unifiedApi';
import { getTokens, setTokens } from '../utils/tokenStorage';

interface ProfileScreenProps {
  onBack: () => void;
  onAddNotification: (message: string) => void;
}

// NOTE: 디버그 전용 컴포넌트 – 실제 화면(ProfileScreen)과 이름 충돌 방지를 위해 별도 이름 사용
export function ProfileScreenDebug({ onBack, onAddNotification }: ProfileScreenProps) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const checkAuthAndFetchData = async () => {
      try {
        setLoading(true);
        console.log('[ProfileScreen] 인증 상태 확인 시작');

        // 1. 토큰 확인
        const tokens = getTokens();
        console.log('[ProfileScreen] 현재 토큰:', tokens ? '있음' : '없음');
        
        if (!tokens?.access_token) {
          console.log('[ProfileScreen] 토큰이 없음, DEV 자동 로그인 시도');
          
          // DEV 자동 로그인 시도
          try {
            const loginResponse = await unifiedApi.post('auth/login', {
              site_id: 'test123',
              password: 'password123'
            }, { auth: false });
            
            console.log('[ProfileScreen] DEV 로그인 응답:', loginResponse);
            
            if (loginResponse?.access_token) {
              setTokens({
                access_token: loginResponse.access_token,
                refresh_token: loginResponse.refresh_token || loginResponse.access_token
              });
              console.log('[ProfileScreen] DEV 로그인 성공, 토큰 저장됨');
              onAddNotification('DEV 자동 로그인 완료');
            } else {
              throw new Error('로그인 응답에 토큰이 없음');
            }
          } catch (loginError) {
            console.error('[ProfileScreen] DEV 로그인 실패:', loginError);
            setError('로그인이 필요합니다.');
            onAddNotification('로그인이 필요합니다.');
            setLoading(false);
            return;
          }
        }

        // 2. 프로필 데이터 가져오기
        console.log('[ProfileScreen] 프로필 데이터 요청 시작');
  const profileResponse = await unifiedApi.get('auth/me');
        console.log('[ProfileScreen] 프로필 응답:', profileResponse);
        
        setUser(profileResponse);
        onAddNotification('프로필 로드 완료');
        
      } catch (err: any) {
        console.error('[ProfileScreen] 오류:', err);
        setError(err.message || '프로필을 불러올 수 없습니다.');
        onAddNotification('프로필 로드 실패: ' + (err.message || '알 수 없는 오류'));
      } finally {
        setLoading(false);
      }
    };

    checkAuthAndFetchData();
  }, [onAddNotification]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-black/95 to-primary/5">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-lg text-muted-foreground">프로필을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error && !user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-black/95 to-primary/5 p-4">
        <Card className="max-w-md mx-auto mt-20 p-8 text-center">
          <h2 className="text-xl font-bold mb-4">인증 오류</h2>
          <p className="text-muted-foreground mb-6">{error}</p>
          <div className="space-y-3">
            <Button onClick={onBack} className="w-full">
              <ArrowLeft className="w-4 h-4 mr-2" />
              홈으로 돌아가기
            </Button>
            <Button
              variant="default"
              className="w-full"
              onClick={async () => {
                try {
                  const loginResponse = await unifiedApi.post('auth/login', {
                    site_id: 'test123',
                    password: 'password123'
                  }, { auth: false });
                  
                  if (loginResponse?.access_token) {
                    setTokens({
                      access_token: loginResponse.access_token,
                      refresh_token: loginResponse.refresh_token || loginResponse.access_token
                    });
                    onAddNotification('테스트 로그인 성공!');
                    window.location.reload();
                  }
                } catch (err: any) {
                  onAddNotification('로그인 실패: ' + err.message);
                }
              }}
            >
              테스트 로그인 (test123)
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-black/95 to-primary/5 p-4">
      <div className="max-w-4xl mx-auto">
        {/* 헤더 */}
        <div className="flex items-center justify-between mb-6">
          <Button 
            variant="ghost" 
            onClick={onBack}
            className="glass-effect hover:bg-primary/10"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            뒤로
          </Button>
          <h1 className="text-2xl font-bold text-gradient-primary">프로필</h1>
          <div></div>
        </div>

        {/* 프로필 정보 */}
        <Card className="glass-effect p-6 border-border-secondary/50">
          <h2 className="text-xl font-bold mb-4">사용자 정보</h2>
          {user ? (
            <div className="space-y-2">
              <p><strong>ID:</strong> {user.id}</p>
              <p><strong>사이트 ID:</strong> {user.site_id}</p>
              <p><strong>닉네임:</strong> {user.nickname}</p>
              <p><strong>전화번호:</strong> {user.phone_number}</p>
              <p><strong>등급:</strong> {user.rank}</p>
              <p><strong>토큰 잔액:</strong> {user.cyber_token_balance}</p>
              <p><strong>활성 상태:</strong> {user.is_active ? '활성' : '비활성'}</p>
              <p><strong>관리자:</strong> {user.is_admin ? '예' : '아니오'}</p>
              <p><strong>생성일:</strong> {new Date(user.created_at).toLocaleString()}</p>
            </div>
          ) : (
            <p>사용자 정보를 불러올 수 없습니다.</p>
          )}
        </Card>

        {/* 디버그 정보 */}
        <Card className="glass-effect p-6 border-border-secondary/50 mt-4">
          <h2 className="text-xl font-bold mb-4">디버그 정보</h2>
          <div className="space-y-2 text-sm">
            <p><strong>현재 토큰:</strong> {getTokens() ? '있음' : '없음'}</p>
            <p><strong>API Origin:</strong> {process.env.NEXT_PUBLIC_API_ORIGIN || '기본값'}</p>
            <p><strong>환경:</strong> {process.env.NODE_ENV}</p>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default ProfileScreenDebug;
