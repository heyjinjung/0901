'use client';
import React, { useEffect, useState } from 'react';

async function getVapidPublicKey(): Promise<string | null> {
  try {
    const r = await fetch('/api/notification/push/vapid-public');
    if (!r.ok) return null;
    const j = await r.json();
    return (j && j.publicKey) || null;
  } catch {
    return null;
  }
}

async function registerServiceWorker() {
  if (!('serviceWorker' in navigator)) return null;
  try {
    const reg = await navigator.serviceWorker.register('/sw.js');
    await navigator.serviceWorker.ready;
    return reg;
  } catch {
    return null;
  }
}

async function subscribePush() {
  try {
    const reg = await registerServiceWorker();
    if (!reg || !('pushManager' in reg)) return false;
    const vapid = await getVapidPublicKey();
    const appServerKey = vapid ? urlBase64ToUint8Array(vapid) : undefined;
    const sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: appServerKey,
    });
    const json = (sub && sub.toJSON && sub.toJSON()) || null;
    if (!json) return false;
    const body = { endpoint: json.endpoint, p256dh: json.keys?.p256dh, auth: json.keys?.auth };
    await fetch('/api/notification/push/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    return true;
  } catch {
    return false;
  }
}

function urlBase64ToUint8Array(base64String: string) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData =
    typeof window !== 'undefined'
      ? window.atob(base64)
      : Buffer.from(base64, 'base64').toString('binary');
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) outputArray[i] = rawData.charCodeAt(i);
  return outputArray;
}

export default function RequestPushPermission() {
  const [state, setState] = useState('default' as 'default' | 'denied' | 'granted' | 'unsupported');

  useEffect(() => {
    if (typeof window === 'undefined' || !('Notification' in window)) {
      setState('unsupported');
      return;
    }
    setState(Notification.permission as any);
  }, []);

  const onAllow = async () => {
    if (!('Notification' in window)) return;
    try {
      const result = await Notification.requestPermission();
      setState(result as any);
      if (result === 'granted') {
        try {
          await subscribePush();
        } catch {}
      }
    } catch {}
  };

  if (state !== 'default') return null;
  return (
    <div className="mb-4 p-3 rounded border border-cyan-500/30 bg-cyan-900/10 text-cyan-100">
      <div className="text-sm font-medium mb-1">브라우저 푸시 알림을 허용하시겠어요?</div>
      <div className="text-xs opacity-80 mb-2">
        알림을 허용하면 중요한 이벤트/보상 알림을 실시간으로 받을 수 있어요.
      </div>
      <button
        className="px-2 py-1 rounded bg-cyan-700 hover:bg-cyan-600 text-white text-xs"
        onClick={onAllow}
      >
        권한 요청
      </button>
    </div>
  );
}
