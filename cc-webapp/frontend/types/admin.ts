// 관리자 전용 타입 정의
export interface ShopItem {
  id: string;
  name: string;
  description: string;
  price: number;
  category: 'skin' | 'powerup' | 'currency' | 'collectible' | 'character' | 'weapon';
  rarity: 'common' | 'rare' | 'epic' | 'legendary' | 'mythic';
  isActive: boolean;
  stock?: number;
  discount?: number;
  icon: string;
  previewImage?: string;
  createdAt: Date;
  updatedAt: Date;
  sales: number;
  tags: string[];
}

export interface AdminLog {
  id: string;
  adminId: string;
  adminName: string;
  action: string;
  target: string;
  details: string;
  timestamp: Date;
  ipAddress: string;
  userAgent: string;
}

export interface SystemBackup {
  id: string;
  name: string;
  description: string;
  size: number;
  createdAt: Date;
  type: 'full' | 'users' | 'shop' | 'logs';
  status: 'creating' | 'completed' | 'failed';
}

export interface PushNotification {
  id: string;
  title: string;
  message: string;
  type: 'general' | 'event' | 'maintenance' | 'promotion';
  targetUsers: 'all' | 'active' | 'specific';
  userIds?: string[];
  scheduledAt?: Date;
  sentAt?: Date;
  isRead: boolean;
  clickCount: number;
}

export interface UserImportData {
  nickname: string;
  email?: string;
  goldBalance?: number;
  level?: number;
  isAdmin?: boolean;
}

export interface AdminDashboardStats {
  totalRevenue: number;
  todayRevenue: number;
  totalUsers: number;
  activeUsers: number;
  newUsersToday: number;
  totalShopItems: number;
  topSellingItems: Array<{
    item: ShopItem;
    sales: number;
    revenue: number;
  }>;
  recentActivity: AdminLog[];
}

export interface GameConfiguration {
  id: string;
  key: string;
  value: any;
  description: string;
  type: 'string' | 'number' | 'boolean' | 'json';
  category: 'game' | 'economy' | 'ui' | 'security';
  updatedAt: Date;
  updatedBy: string;
}