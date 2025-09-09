'use client';
import React, { createContext, useCallback, useMemo, useRef, useState } from 'react';
import { Trophy, Star, AlertTriangle, Info, Sparkles, Zap } from 'lucide-react';
import styles from '../components/feedback/FeedbackToast.module.css';

interface EnqueueInput {
  code: string;
  severity?: 'info' | 'success' | 'warn' | 'error';
  message?: string;
  animation?: string | null;
  meta?: Record<string, any>;
  streak?: number | null;
}

export interface InternalToast extends EnqueueInput {
  id: string;
  createdAt: number;
}
export interface FeedbackContextShape {
  enqueue: (f: EnqueueInput) => void;
}
// 타입 빌드 환경(레거시 설정) 제네릭 제한 회피: any 캐스팅 후 훅 내부에서 좁혀 사용
export const FeedbackContext = createContext(null as any as FeedbackContextShape | null);

interface ProviderProps {
  children?: React.ReactNode;
  max?: number;
  ttlMs?: number;
}

export function FeedbackProvider({ children, max = 4, ttlMs = 4000 }: ProviderProps) {
  const [items, setItems] = useState([] as InternalToast[]);
  const timersRef = useRef({} as Record<string, any>);

  const remove = useCallback((id: string) => {
    setItems((prev: InternalToast[]) => prev.filter((i: InternalToast) => i.id !== id));
    if (timersRef.current[id]) {
      clearTimeout(timersRef.current[id]);
      delete timersRef.current[id];
    }
  }, []);

  const enqueue = useCallback(
    (f: EnqueueInput) => {
      if (typeof window === 'undefined') return; // SSR 안전
      // code/severity 기반 icon & animation default 매핑
      const mapping = resolveFeedbackVisuals(f);
      setItems((prev: InternalToast[]) =>
        [
          ...prev,
          {
            id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
            createdAt: Date.now(),
            ...f,
            animation: f.animation || mapping.animation,
            meta: { ...(f.meta || {}), icon: mapping.iconName },
          },
        ].slice(-max)
      );
    },
    [max]
  );

  React.useEffect(() => {
    if (items.length === 0) return;
    items.forEach((item: InternalToast) => {
      if (!timersRef.current[item.id])
        timersRef.current[item.id] = setTimeout(() => remove(item.id), ttlMs);
    });
  }, [items, ttlMs, remove]);

  React.useEffect(() => {
    if (items.length === 0 || typeof window === 'undefined') return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setItems([]);
        Object.values(timersRef.current).forEach((t: any) => clearTimeout(t));
        timersRef.current = {};
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [items]);

  const value = useMemo(() => ({ enqueue }), [enqueue]);

  return (
    <FeedbackContext.Provider value={value}>
      {children}
      <div aria-live="polite" className="sr-only" data-feedback-live-region />
      {items.length > 0 && (
        <div className={styles.container} role="status" aria-label="게임 피드백 알림 영역">
          {items.map((i: InternalToast) => {
            const IconCmp = iconComponent(i.meta?.icon);
            return (
              <div
                key={i.id}
                className={styles.toast + ' ' + (styles[i.severity || 'info'] || '')}
                data-anim={i.animation || undefined}
                onClick={() => remove(i.id)}
                role="alert"
              >
                <div className={styles.row}>
                  {IconCmp && <IconCmp className={styles.icon} size={16} />}
                  <div className={styles.code}>{i.code}</div>
                </div>
                {i.message && <div className={styles.msg}>{i.message}</div>}
              </div>
            );
          })}
        </div>
      )}
    </FeedbackContext.Provider>
  );
}

// ---------------- Visual Mapping Helpers ----------------
interface VisualMapping {
  iconName: string | null;
  animation?: string | null;
}

export function resolveFeedbackVisuals(f: EnqueueInput): VisualMapping {
  const { code, severity } = f;
  // domain.event[.qualifier]
  if (code.startsWith('slot.jackpot')) return { iconName: 'trophy', animation: 'jackpot' };
  if (code.startsWith('slot.win')) return { iconName: 'star', animation: 'pulse' };
  if (code.startsWith('slot.lose')) return { iconName: 'alert', animation: null };
  if (code.startsWith('gacha.pity')) return { iconName: 'sparkles', animation: 'pity' };
  if (code.startsWith('gacha.near_miss')) return { iconName: 'zap', animation: 'near_miss' };
  if (code.startsWith('gacha.win.legendary')) return { iconName: 'trophy', animation: 'legendary' };
  if (code.startsWith('gacha.win.epic')) return { iconName: 'star', animation: 'epic' };
  switch (severity) {
    case 'success':
      return { iconName: 'star', animation: 'pulse' };
    case 'warn':
      return { iconName: 'alert', animation: null };
    case 'error':
      return { iconName: 'alert', animation: 'shake' };
    default:
      return { iconName: 'info', animation: null };
  }
}

function iconComponent(name?: string | null) {
  switch (name) {
    case 'trophy':
      return Trophy;
    case 'star':
      return Star;
    case 'alert':
      return AlertTriangle;
    case 'sparkles':
      return Sparkles;
    case 'zap':
      return Zap;
    case 'info':
      return Info;
    default:
      return null;
  }
}

export default FeedbackProvider;
