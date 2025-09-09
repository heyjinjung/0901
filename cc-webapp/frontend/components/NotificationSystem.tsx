'use client';

import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Notification } from '../types';
import { 
  VIP_NOTIFICATION_KEYWORDS, 
  NOTIFICATION_CONFIG, 
  NOTIFICATION_STYLES 
} from '../constants/notificationConstants';

interface NotificationSystemProps {
  children?: React.ReactNode;
}

export function NotificationSystem({ children }: NotificationSystemProps) {
  const [notifications, setNotifications] = useState([] as Notification[]);

  // 🔧 고유 ID 생성기
  const generateNotificationId = useCallback(() => {
    const id = `notification-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
    return id;
  }, []);

  // 📱 🎯 VIP 알림만 (중요한 것만)
  const addNotification = useCallback((message: string) => {
    // 특정 키워드가 포함된 중요한 알림만 표시
    const shouldShow = VIP_NOTIFICATION_KEYWORDS.some(keyword => message.includes(keyword));
    
    if (shouldShow) {
      const newNotification: Notification = {
        id: generateNotificationId(),
        message,
        timestamp: Date.now()
      };
      
  setNotifications((prev: Notification[]) => [newNotification, ...prev.slice(0, NOTIFICATION_CONFIG.MAX_COUNT - 1)]);
      
      setTimeout(() => {
        setNotifications((prev: Notification[]) => prev.filter((n: Notification) => n.id !== newNotification.id));
      }, NOTIFICATION_CONFIG.DURATION);
    }
  }, [generateNotificationId]);

  // 알림 시스템을 children에게 전달하기 위한 렌더 프롭 패턴
  const childrenWithNotifications = React.Children.map(children, (child: React.ReactNode) => {
    if (React.isValidElement(child)) {
      if (React.isValidElement(child)) {
        return React.cloneElement(child, { addNotification });
      }
      return child;
    }
    return child;
  });

  return (
    <>
      {/* 📱 🎯 VIP 알림 시스템 (중요한 것만) - 고유 키 사용 */}
      <div className={NOTIFICATION_STYLES.CONTAINER}>
        <AnimatePresence>
          {notifications.map((notification: Notification) => (
            <motion.div
              key={notification.id}
              initial={NOTIFICATION_STYLES.ANIMATION.INITIAL}
              animate={NOTIFICATION_STYLES.ANIMATION.ANIMATE}
              exit={NOTIFICATION_STYLES.ANIMATION.EXIT}
              className={NOTIFICATION_STYLES.ITEM}
            >
              {notification.message}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {childrenWithNotifications}
    </>
  );
}

// Export the hook for external use
export function useNotificationSystem() {
  const [notifications, setNotifications] = useState([] as Notification[]);

  const generateNotificationId = useCallback(() => {
    const id = `notification-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
    return id;
  }, []);

  const addNotification = useCallback((message: string) => {
    const shouldShow = VIP_NOTIFICATION_KEYWORDS.some(keyword => message.includes(keyword));
    
    if (shouldShow) {
      const newNotification: Notification = {
        id: generateNotificationId(),
        message,
        timestamp: Date.now()
      };
      
  setNotifications((prev: Notification[]) => [newNotification, ...prev.slice(0, NOTIFICATION_CONFIG.MAX_COUNT - 1)]);
      
      setTimeout(() => {
        setNotifications((prev: Notification[]) => prev.filter((n: Notification) => n.id !== newNotification.id));
      }, NOTIFICATION_CONFIG.DURATION);
    }
  }, [generateNotificationId]);

  return {
    notifications,
    addNotification
  };
}