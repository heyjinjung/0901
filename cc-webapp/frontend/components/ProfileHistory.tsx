'use client';
import React, { useState } from 'react';
import { api as unifiedApi, UnifiedRequestOptions } from '@/lib/unifiedApi';

type Tx = {
  product_id?: number | string;
  kind?: string;
  quantity?: number;
  unit_price?: number;
  amount?: number;
  status?: string;
  payment_method?: string;
  receipt_code?: string;
  created_at?: string | null;
};

export default function ProfileHistory() {
  const [items, setItems] = useState([] as Tx[]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null as string | null);
  const [limit] = useState(20);
  const [nextCursor, setNextCursor] = useState(null as number | null);
  const [mergeMode, setMergeMode] = useState(true); // true: merge(append), false: replace

  async function loadPage() {
    setLoading(true);
    setError(null);
    try {
      // backend supports GET /api/shop/transactions?limit=20
      // we emulate cursor by using last known receipt_code or id if available.
      // build query string for GET request (unifiedApi expects path-only)
      const qs = new URLSearchParams();
      qs.set('limit', String(limit));
      if (nextCursor) qs.set('after_id', String(nextCursor));
      const path = `shop/transactions?${qs.toString()}`;
      // call API; response shape may be Tx[] or { transactions: Tx[] }
  const raw = await unifiedApi.get<unknown>(path, { parseJson: true, auth: true });
      let txs: Tx[] = [];
      if (Array.isArray(raw)) {
        txs = raw as Tx[];
      } else if (raw && typeof raw === 'object') {
        const r = raw as Record<string, unknown>;
        if (Array.isArray(r.transactions)) {
          txs = r.transactions as Tx[];
        }
      }

      if (mergeMode) {
  setItems((prev: Tx[]) => [...prev, ...txs]);
      } else {
        setItems(txs);
      }

      // determine next cursor from last item (assuming descending order)
      if (txs.length > 0) {
        const last = txs[txs.length - 1];
        // use created_at fallback if no numeric id; unified API may expose receipt_code only
        // keep it simple: if created_at present, convert to timestamp
        const cursor = last && last.created_at ? Date.parse(last.created_at) : null;
        setNextCursor(cursor);
      } else {
        setNextCursor(null);
      }
    } catch (e: unknown) {
      if (e instanceof Error) setError(e.message);
      else setError(String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-4 bg-slate-800 text-white rounded">
      <h3 className="text-lg font-bold mb-2">거래 내역</h3>
      <div className="mb-2">
        <label className="mr-2">모드:</label>
        <label className="mr-2">
          <input type="radio" checked={mergeMode} onChange={() => setMergeMode(true)} /> 누적(merge)
        </label>
        <label>
          <input type="radio" checked={!mergeMode} onChange={() => setMergeMode(false)} />{' '}
          대체(replace)
        </label>
      </div>

      {error && <div className="text-red-400 mb-2">에러: {error}</div>}

      <ul className="space-y-2 mb-4">
        {items.map((t: Tx, i: number) => (
          <li key={`${t.receipt_code ?? i}`} className="bg-slate-700 p-2 rounded">
            <div className="text-sm">제품: {String(t.product_id ?? '-')}</div>
            <div className="text-xs text-slate-300">
              금액: {t.amount ?? '-'} | 상태: {t.status ?? '-'}
            </div>
            <div className="text-xs text-slate-400">일시: {t.created_at ?? '-'}</div>
          </li>
        ))}
      </ul>

      <div className="flex items-center gap-2">
        <button className="px-3 py-1 bg-indigo-600 rounded" onClick={loadPage} disabled={loading}>
          {loading ? '로딩...' : '더 불러오기'}
        </button>
        <button
          className="px-3 py-1 bg-gray-600 rounded"
          onClick={() => {
            setItems([]);
            setNextCursor(null);
          }}
        >
          초기화
        </button>
      </div>
      <div className="mt-2 text-xs text-slate-400">
        설명: limit 기반 페이지네이션 (merge/replace 선택 가능)
      </div>
    </div>
  );
}
