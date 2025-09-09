"use client";
import * as React from "react";
import { useEffect, useRef, useState } from "react";
import { API_ORIGIN } from '@/lib/unifiedApi';

type EventMsg = { type: string; payload?: any };

interface Props {
  userId: number;
}

export default function NotificationClient({ userId }: Props) {
  const [messages, setMessages] = React.useState([] as EventMsg[]);
  const wsRef = React.useRef(null as WebSocket | null);
  const retryRef = React.useRef(0 as number);

  useEffect(() => {
    let stopped = false;
    const connect = () => {
      try {
        const u = new URL(API_ORIGIN);
        const originHost = `${u.hostname}${u.port ? ':' + u.port : ''}`;
        const proto = u.protocol === 'https:' ? 'wss' : 'ws';
        const ws = new WebSocket(`${proto}://${originHost}/ws/notifications/${userId}`);
        wsRef.current = ws;
        ws.onopen = () => {
          retryRef.current = 0;
          console.log('WS connected');
        };
        ws.onmessage = (event: MessageEvent<string>) => {
          try {
            const msg = JSON.parse(event.data);
            setMessages((prev: EventMsg[]) => [msg, ...prev].slice(0, 50));
            // 전역 이벤트 디스패치(토스트/리액션 등에서 청취)
            try {
              window.dispatchEvent(new CustomEvent('app:notification', { detail: msg }));
            } catch {}
          } catch {
            // plain text
            const payload = { type: 'text', payload: event.data } as EventMsg;
            setMessages((prev: EventMsg[]) => [payload, ...prev].slice(0, 50));
            try {
              window.dispatchEvent(new CustomEvent('app:notification', { detail: payload }));
            } catch {}
          }
        };
        ws.onclose = () => {
          if (stopped) return;
          const backoff = Math.min(1000 * Math.pow(2, retryRef.current++), 10000);
          setTimeout(connect, backoff);
        };
        ws.onerror = () => {
          ws.close();
        };
      } catch (e) {
        const backoff = Math.min(1000 * Math.pow(2, retryRef.current++), 10000);
        setTimeout(connect, backoff);
      }
    };
    connect();
    return () => {
      stopped = true;
      wsRef.current?.close();
    };
  }, [userId]);

  return (
    <div className="fixed right-4 bottom-4 w-80 bg-black/70 text-white border border-cyan-500/40 rounded-lg shadow-lg p-3">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-semibold">Notifications</span>
        <button
          className="text-xs text-cyan-300 hover:text-cyan-200"
          onClick={() => setMessages([])}
        >
          clear
        </button>
      </div>
      <ul className="space-y-1 max-h-64 overflow-auto">
        {messages.map((m: EventMsg, i: number) => (
          <li key={i} className="text-xs bg-cyan-900/20 border border-cyan-500/20 rounded p-2">
            <div className="opacity-70">{m.type}</div>
            <pre className="whitespace-pre-wrap break-words text-[11px]">
              {JSON.stringify(m.payload ?? m, null, 0)}
            </pre>
          </li>
        ))}
        {messages.length === 0 && <li className="text-xs opacity-60">No notifications yet…</li>}
      </ul>
    </div>
  );
}
