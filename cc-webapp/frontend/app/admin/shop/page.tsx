"use client";
import React from 'react';
import { ShopManager } from '@/components/admin/ShopManager';
import { useToast } from '@/components/NotificationToast';

export default function AdminShopPage() {
  const { push } = useToast();
  return (
    <div className="p-6">
      <h1 className="text-2xl mb-4 text-foreground">🛍️ 상점 관리</h1>
      <ShopManager onAddNotification={(m: string) => push(m, 'shop')} />
    </div>
  );
}
