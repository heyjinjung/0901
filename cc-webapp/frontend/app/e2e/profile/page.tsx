'use client';

import React from 'react';
import { ProfileScreen } from '@/components/ProfileScreen';

export default function E2EProfilePage() {
  return (
    // 테스트 안정성을 위해 최상위에 고정 data-testid를 부여
    <div data-testid="profile-screen">
      <ProfileScreen
        onBack={() => {}}
        onAddNotification={() => {}}
        retryEnabled={false}
        maxRetries={0}
        retryDelayMs={0}
      />
    </div>
  );
}
