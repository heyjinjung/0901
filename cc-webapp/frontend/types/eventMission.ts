// types/eventMission.ts
import { User } from './index';

// 이벤트 타입 정의 확장
export interface EventBackend {
  id: number;
  title: string;
  description: string | null;
  event_type: string;
  start_date: string;
  end_date: string;
  rewards: {
    gold?: number;
    gems?: number;
    items?: any[];
    [key: string]: any;
  } | null;
  requirements: {
    min_level?: number;
    games_played?: number;
    [key: string]: any;
  } | null;
  image_url: string | null;
  is_active: boolean;
  priority: number;
  created_at: string;
  participation_count?: number; // backend injected participant count
  user_participation?: {
    joined: boolean;
    progress: any;
    completed: boolean;
    claimed: boolean;
  }
}

// 이벤트 참여 타입
export interface EventParticipation {
  id: number;
  user_id: number;
  event_id: number;
  progress: any;
  completed: boolean;
  claimed_rewards: boolean;
  joined_at: string;
  completed_at: string | null;
}

// 미션 타입 정의
export interface MissionBackend {
  id: number;
  title: string;
  description: string | null;
  mission_type: string;
  category: string | null;
  target_value: number;
  target_type: string;
  rewards: {
    gold?: number;
    exp?: number;
    [key: string]: any;
  } | null;
  requirements: {
    min_level?: number;
    [key: string]: any;
  } | null;
  reset_period: string | null;
  icon: string | null;
  is_active: boolean;
  sort_order: number;
  created_at: string;
}

// 사용자 미션 타입
export interface UserMissionBackend {
  id: number;
  user_id: number;
  mission_id: number;
  mission: MissionBackend;
  current_progress: number;
  completed: boolean;
  claimed: boolean;
  started_at: string;
  completed_at: string | null;
  claimed_at: string | null;
  reset_at: string | null;
}

// 보상 응답 타입
export interface ClaimRewardResponse {
  success: boolean;
  rewards: {
    gold?: number;
    gems?: number;
    exp?: number;
    items?: any[];
    [key: string]: any;
  };
  message: string;
}
