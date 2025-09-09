'use client';

import React from 'react';
import { AdminDashboard } from './AdminDashboard';

interface AdminPanelProps {
  user?: any;
  onBack?: () => void;
  onUpdateUser?: (user: any) => void;
  onAddNotification?: (notification: any) => void;
}

export function AdminPanel({ user, onBack, onUpdateUser, onAddNotification }: AdminPanelProps) {
  const handleRefresh = () => {
    // 새로고침 로직
    if (onAddNotification) {
      onAddNotification('관리자 데이터를 새로고침했습니다.');
    }
  };

  return (
    <AdminDashboard 
      onRefresh={handleRefresh}
    />
  );
}

export default AdminPanel;
