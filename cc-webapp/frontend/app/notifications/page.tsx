'use client';
import React, { useEffect, useState } from 'react';
import NotificationClient from '@/components/NotificationClient';
import RequestPushPermission from '@/components/RequestPushPermission';

type Item = {
  id: number;
  message: string;
  notification_type?: string;
  is_read: boolean;
  created_at?: string;
};

export default function NotificationsPage() {
  const userId = 1; // TODO: derive from auth context
  const [items, setItems] = useState([] as Item[]);
  const [unread, setUnread] = useState(0);
  const [filter, setFilter] = useState('all');

  const fetchList = async () => {
    try {
      const q = new URLSearchParams();
      if (filter !== 'all') q.set('notification_type', filter);
      const res = await fetch(`/api/notification/list?${q.toString()}`, { credentials: 'include' });
      if (!res.ok) return;
      const data = await res.json();
      setItems(data.items || []);
      setUnread(data.unread || 0);
    } catch {}
  };

  const markRead = async (id: number, read = true) => {
    try {
      await fetch(`/api/notification/${id}/read`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ read }),
      });
      fetchList();
    } catch {}
  };

  const markAll = async () => {
    try {
      await fetch(`/api/notification/read-all`, { method: 'POST', credentials: 'include' });
      fetchList();
    } catch {}
  };

  useEffect(() => {
    fetchList();
  }, [filter]);

  return (
    <main className="min-h-screen bg-black text-white p-6">
  <RequestPushPermission />
  <div className="flex items-center justify-between">
        <h1 className="text-2xl mb-4">Notifications</h1>
        <button className="px-3 py-1 rounded bg-zinc-800 border border-zinc-700" onClick={markAll}>
          모두 읽음 처리
        </button>
      </div>
      <div className="flex items-center gap-3 mb-4">
        <p className="opacity-70">Unread: {unread}</p>
        <div className="flex items-center gap-2 text-xs">
          {['all','reward','shop','event','system'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-2 py-1 rounded border ${filter===f? 'bg-cyan-900/40 border-cyan-500/50':'bg-zinc-900/40 border-zinc-700'}`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <section className="bg-zinc-900 p-4 rounded border border-zinc-800">
          <h2 className="font-semibold mb-2">Center</h2>
          {items.length === 0 && <div className="opacity-60 text-sm">No notifications.</div>}
          <ul className="space-y-2">
            {items.map((it: Item) => (
              <li
                key={it.id}
                className="p-3 rounded bg-zinc-950 border border-zinc-800 flex items-start justify-between"
              >
                <div>
                  <div className="text-sm opacity-70">{it.notification_type || 'info'}</div>
                  <div className="font-medium">{it.message}</div>
                  <div className="text-xs opacity-60">
                    {it.created_at ? new Date(it.created_at).toLocaleString() : ''}
                  </div>
                </div>
                <button
                  className={`ml-4 px-2 py-1 rounded text-xs ${it.is_read ? 'bg-zinc-800' : 'bg-blue-600'}`}
                  onClick={() => markRead(it.id, !it.is_read)}
                >
                  {it.is_read ? '읽음 취소' : '읽음'}
                </button>
              </li>
            ))}
          </ul>
        </section>

        <section className="bg-zinc-900 p-4 rounded border border-zinc-800">
          <h2 className="font-semibold mb-2">Real-time (WS)</h2>
          <p className="opacity-70 mb-2">This opens a WebSocket for user {userId}.</p>
          <NotificationClient userId={userId} />
          <div className="mt-4 text-xs opacity-70">
            Dev send: POST /api/notifications/{'{'}user_id{'}'}/send
          </div>
        </section>
      </div>
    </main>
  );
}
