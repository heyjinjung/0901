'use client';
import React, { useEffect, useState } from 'react';

const KEY = 'app.notification.settings.v1';

type Settings = {
  toastEnabled: boolean;
  types: { reward: boolean; event: boolean; system: boolean; shop: boolean };
  sound: boolean;
  dnd: { enabled: boolean; start: string; end: string };
};

const defaults: Settings = {
  toastEnabled: true,
  types: { reward: true, event: true, system: true, shop: true },
  sound: false,
  dnd: { enabled: false, start: '22:00', end: '07:00' },
};

export default function NotificationSettingsPage() {
  const [s, setS] = useState({ ...defaults } as Settings);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(KEY);
      if (raw) setS({ ...defaults, ...JSON.parse(raw) });
    } catch {}
  }, []);

  useEffect(() => {
    try {
      localStorage.setItem(KEY, JSON.stringify(s));
    } catch {}
  }, [s]);

  return (
    <main className="min-h-screen bg-black text-white p-6">
      <h1 className="text-2xl mb-4">알림 설정</h1>

      <section className="bg-zinc-900 p-4 rounded border border-zinc-800 mb-4">
        <h2 className="font-semibold mb-2">토스트</h2>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={s.toastEnabled} onChange={(e: any) => setS({ ...s, toastEnabled: e.target.checked })} />
          토스트 알림 표시
        </label>
      </section>

      <section className="bg-zinc-900 p-4 rounded border border-zinc-800 mb-4">
        <h2 className="font-semibold mb-2">유형별 표시</h2>
        {(['reward','event','system','shop'] as const).map((k) => (
          <label key={k} className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={s.types[k]}
              onChange={(e: any) => setS({ ...s, types: { ...s.types, [k]: e.target.checked } })}
            />
            {k}
          </label>
        ))}
      </section>

      <section className="bg-zinc-900 p-4 rounded border border-zinc-800 mb-4">
        <h2 className="font-semibold mb-2">사운드</h2>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={s.sound} onChange={(e: any) => setS({ ...s, sound: e.target.checked })} />
          토스트에 소리 재생
        </label>
      </section>

      <section className="bg-zinc-900 p-4 rounded border border-zinc-800">
        <h2 className="font-semibold mb-2">방해 금지(DND)</h2>
        <label className="flex items-center gap-2 text-sm mb-2">
          <input type="checkbox" checked={s.dnd.enabled} onChange={(e: any) => setS({ ...s, dnd: { ...s.dnd, enabled: e.target.checked } })} />
          DND 활성화
        </label>
        <div className="flex items-center gap-3 text-sm">
          <div>
            <div className="opacity-70 text-xs mb-1">시작</div>
            <input className="bg-zinc-800 rounded px-2 py-1" type="time" value={s.dnd.start} onChange={(e: any) => setS({ ...s, dnd: { ...s.dnd, start: e.target.value } })} />
          </div>
          <div>
            <div className="opacity-70 text-xs mb-1">종료</div>
            <input className="bg-zinc-800 rounded px-2 py-1" type="time" value={s.dnd.end} onChange={(e: any) => setS({ ...s, dnd: { ...s.dnd, end: e.target.value } })} />
          </div>
        </div>
      </section>
    </main>
  );
}
