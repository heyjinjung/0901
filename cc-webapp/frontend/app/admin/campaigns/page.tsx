"use client";
import React from 'react';

const API = 'http://127.0.0.1:8000/api';

type NewCampaign = {
  title: string;
  message: string;
  targeting_type: 'all'|'segment'|'user_ids';
  target_segment?: string;
  user_ids?: string;
  scheduled_at?: string;
}

export default function AdminCampaignsPage() {
  const [msg, setMsg] = React.useState('');
  const [title, setTitle] = React.useState('Hello');
  const [target, setTarget] = React.useState('all' as 'all'|'segment'|'user_ids');
  const [segment, setSegment] = React.useState('');
  const [userIds, setUserIds] = React.useState('');
  const [result, setResult] = React.useState('');

  const create = async () => {
    const token = localStorage.getItem('access_token');
    const payload: any = { title, message: msg, targeting_type: target };
    if (target === 'segment') payload.target_segment = segment;
  if (target === 'user_ids') payload.user_ids = userIds.split(',').map((s: string)=>parseInt(s.trim(),10));
    const r = await fetch(`${API}/admin/campaigns`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(token?{Authorization:`Bearer ${token}`}:{}) },
      body: JSON.stringify(payload)
    });
    const j = await r.json();
    if (!r.ok) throw new Error(j.detail||'failed');
    setResult(`Created campaign id=${j.id}`);
  }

  return (
    <div className="p-6 text-pink-200">
      <h1 className="text-2xl mb-4">Admin Campaigns</h1>
      <div className="space-y-2 max-w-xl">
        <input
          className="w-full bg-black/20 p-2"
          placeholder="Title"
          value={title}
          onChange={(e: InputChangeEvent) => setTitle(e.target.value)}
        />
        <textarea
          className="w-full bg-black/20 p-2"
          placeholder="Message"
          value={msg}
          onChange={(e: TextareaChangeEvent) => setMsg(e.target.value)}
        />
        <select
          className="w-full bg-black/20 p-2"
          value={target}
          onChange={(e: SelectChangeEvent) => setTarget(e.target.value as 'all'|'segment'|'user_ids')}
        >
          <option value="all">All</option>
          <option value="segment">Segment</option>
          <option value="user_ids">User Ids</option>
        </select>
        {target==='segment' && (
          <input
            className="w-full bg-black/20 p-2"
            placeholder="Segment label (e.g., VIP)"
            value={segment}
            onChange={(e: InputChangeEvent) => setSegment(e.target.value)}
          />
        )}
        {target==='user_ids' && (
          <input
            className="w-full bg-black/20 p-2"
            placeholder="Comma-separated user IDs"
            value={userIds}
            onChange={(e: InputChangeEvent) => setUserIds(e.target.value)}
          />
        )}
        <button onClick={create} className="px-3 py-2 bg-pink-600 rounded">Create Campaign</button>
        {result && <div className="text-green-300">{result}</div>}
      </div>
    </div>
  )
}
