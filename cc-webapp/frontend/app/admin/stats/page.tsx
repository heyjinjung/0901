"use client";
import React from 'react';
import { apiLogger } from '../../../utils/api';

const API = 'http://127.0.0.1:8000/api';

export default function AdminStatsPage() {
  const [data, setData] = React.useState(null as any);
  const [error, setError] = React.useState(null as string | null);

  React.useEffect(() => {
    const token = localStorage.getItem('access_token');
    fetch(`${API}/admin/stats`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then(async (r) => {
        const j = await r.json();
        apiLogger.response('GET', '/admin/stats', r.status, j, 0);
        if (!r.ok) throw new Error(j.detail || 'failed');
        setData(j);
      })
      .catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="p-6 text-pink-200">
      <h1 className="text-2xl mb-4">Admin Stats</h1>
      {error && <div className="text-red-400">{error}</div>}
      {data ? (
        <ul className="space-y-2">
          <li>Total Users: {data.total_users}</li>
          <li>Active Users: {data.active_users}</li>
          <li>Total Games Played: {data.total_games_played}</li>
          <li>Total Tokens: {data.total_tokens_in_circulation}</li>
        </ul>
      ) : (
        <div>Loading…</div>
      )}
    </div>
  );
}
