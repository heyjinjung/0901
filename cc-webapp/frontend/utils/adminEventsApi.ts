import { api } from '../lib/unifiedApi';

// 관리자 이벤트 관리 API 클라이언트
export const adminEventsApi = {
  list: async () => api.get('api/admin/events'),
  create: async (payload: any) => api.post('api/admin/events', payload),
  update: async (id: number, payload: any) => api.put(`api/admin/events/${id}`, payload),
  deactivate: async (id: number) => api.post(`api/admin/events/${id}/deactivate`, {}),
  participations: async (id: number) => api.get(`api/admin/events/${id}/participations`),
  forceClaim: async (id: number, userId: number) => api.post(`api/admin/events/${id}/force-claim/${userId}`, {}),
  seedModelIndex: async () => api.post('api/admin/events/seed/model-index', {}),
};

export default adminEventsApi;
