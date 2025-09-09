"use client";
import React from 'react';
import { UsersManager } from '@/components/admin/UsersManager';

export default function AdminUsersPage() {
  return (
    <div className="min-h-screen p-4">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-xl font-semibold mb-4">👥 사용자 관리</h1>
        <UsersManager onAddNotification={(m:string)=>console.log(m)} />
      </div>
    </div>
  );
}
