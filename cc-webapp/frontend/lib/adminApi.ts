import { api } from '@/lib/unifiedApi';

// 관리자 관련 API thin wrapper
// 백엔드 실제 엔드포인트는 /api/admin/stats (core-stats 아님)
export const adminApi = {
  getCoreStats: () => api.get('admin/stats'),
  listUsers: (params?: { page?: number; size?: number }) => api.get(`admin/users${params?.page!==undefined||params?.size!==undefined?`?${new URLSearchParams({ page: String(params?.page ?? ''), size: String(params?.size ?? '') }).toString()}`:''}`),
};
