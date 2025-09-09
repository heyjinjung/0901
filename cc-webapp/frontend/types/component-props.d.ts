/**
 * 이 파일은 AnimatePresence와 함께 사용되는 컴포넌트의 key prop 문제를 해결합니다.
 * React 컴포넌트 props에 대한 타입 확장을 제공합니다.
 */

import React from 'react';

declare module 'react' {
  interface LoadingScreenProps {
    key?: string;
  }

  interface LoginScreenProps {
    key?: string;
  }

  interface SignupScreenProps {
    key?: string;
  }

  interface AdminLoginProps {
    key?: string;
  }

  interface HomeDashboardProps {
    key?: string;
  }

  interface GameDashboardProps {
    key?: string;
  }

  interface ShopScreenProps {
    key?: string;
  }

  interface InventoryScreenProps {
    key?: string;
  }

  interface ProfileScreenProps {
    key?: string;
  }

  interface SettingsScreenProps {
    key?: string;
  }

  interface AdminPanelProps {
    key?: string;
  }

  interface EventMissionPanelProps {
    key?: string;
  }

  interface NeonSlotGameProps {
    key?: string;
  }

  interface RockPaperScissorsGameProps {
    key?: string;
  }

  interface GachaSystemProps {
    key?: string;
  }

  interface NeonCrashGameProps {
    key?: string;
  }

  interface StreamingScreenProps {
    key?: string;
  }
}
