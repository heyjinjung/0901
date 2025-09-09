// Jest mock for useRealtimeData hooks to avoid provider requirements in unit tests
export const useRealtimePurchaseBadge = () => ({ pendingCount: 0 });
export const useRealtimeNotifications = () => ({ notify: () => { } });
export default { useRealtimePurchaseBadge, useRealtimeNotifications };
