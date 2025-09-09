'use client';

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { api } from '@/lib/unifiedApi';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Switch } from '../ui/switch';
import { Label } from '../ui/Label';
import { Badge } from '../ui/badge';

type UserSummary = {
  id: number;
  site_id: string;
  nickname: string;
  is_active: boolean;
  is_admin: boolean;
  user_rank?: string | null;
  created_at: string;
};

type UserDetail = UserSummary & {
  cyber_token_balance: number;
  last_login?: string | null;
};

type AdminLog = {
  id: number;
  user_id: number;
  action_type: string;
  created_at: string;
  details?: string | null;
};

interface UsersManagerProps {
  onAddNotification: (msg: string) => void;
}

export function UsersManager({ onAddNotification }: UsersManagerProps) {
  const [items, setItems] = useState([] as UserSummary[]);
  const [search, setSearch] = useState('');
  const [skip, setSkip] = useState(0);
  const [limit] = useState(20);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(null as UserDetail | null);
  const [logs, setLogs] = useState([] as AdminLog[]);
  const [rankInput, setRankInput] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const q = new URLSearchParams();
      q.set('skip', String(skip));
      q.set('limit', String(limit));
      if (search.trim()) q.set('search', search.trim());
  const list = (await api.get(`admin/users?${q.toString()}`)) as UserSummary[];
  setItems(list || []);
    } catch (e: any) {
      onAddNotification(`사용자 목록 로드 실패: ${e?.message || e}`);
    } finally {
      setLoading(false);
    }
  }, [skip, limit, search, onAddNotification]);

  useEffect(() => { load(); }, [load]);

  const selectUser = useCallback(async (u: UserSummary) => {
    try {
  const d = (await api.get(`admin/users/${u.id}`)) as UserDetail;
      setSelected(d);
      setRankInput(d.user_rank || '');
      try {
  const lg = (await api.get(`admin/users/${u.id}/logs?limit=50`)) as AdminLog[];
  setLogs(lg || []);
      } catch { setLogs([]); }
    } catch (e: any) {
      onAddNotification(`사용자 상세 로드 실패: ${e?.message || e}`);
    }
  }, [onAddNotification]);

  const toggleActive = useCallback(async () => {
    if (!selected) return;
    try {
      await api.put(`admin/users/${selected.id}`, { is_active: !selected.is_active });
      onAddNotification(`계정 ${selected.is_active ? '비활성화' : '활성화'} 처리되었습니다.`);
      await selectUser(selected);
      await load();
    } catch (e: any) {
      onAddNotification(`상태 변경 실패: ${e?.message || e}`);
    }
  }, [selected, selectUser, load, onAddNotification]);

  const toggleAdmin = useCallback(async () => {
    if (!selected) return;
    try {
      await api.put(`admin/users/${selected.id}`, { is_admin: !selected.is_admin });
      onAddNotification(`관리자 권한이 ${selected.is_admin ? '해제' : '부여'}되었습니다.`);
      await selectUser(selected);
      await load();
    } catch (e: any) {
      onAddNotification(`권한 변경 실패: ${e?.message || e}`);
    }
  }, [selected, selectUser, load, onAddNotification]);

  const updateRank = useCallback(async () => {
    if (!selected) return;
    const newRank = (rankInput || '').trim();
    try {
      await api.put(`admin/users/${selected.id}`, { user_rank: newRank || null });
      onAddNotification('등급이 업데이트되었습니다.');
      await selectUser(selected);
      await load();
    } catch (e: any) {
      onAddNotification(`등급 업데이트 실패: ${e?.message || e}`);
    }
  }, [selected, rankInput, selectUser, load, onAddNotification]);

  const hasPrev = useMemo(() => skip > 0, [skip]);
  const hasNext = useMemo(() => items.length === limit, [items.length, limit]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-end">
        <div className="flex-1">
          <Label htmlFor="search">검색</Label>
          <Input id="search" placeholder="site_id, nickname..." value={search} onChange={(e:any)=>setSearch((e.target as HTMLInputElement).value)} />
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={()=>{ setSkip(0); load(); }} disabled={loading}>검색</Button>
          <Button variant="outline" onClick={()=>{ setSearch(''); setSkip(0); load(); }} disabled={loading}>초기화</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>사용자 목록</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {items.map((u: UserSummary) => (
                <button key={u.id} onClick={()=>selectUser(u)} className={`w-full text-left p-3 rounded border border-border-secondary hover:bg-secondary/30 ${selected?.id===u.id ? 'bg-secondary/40' : ''}`}>
                  <div className="flex items-center justify-between">
                    <div className="font-medium text-foreground">{u.nickname} <span className="text-muted-foreground">({u.site_id})</span></div>
                    <div className="flex gap-2">
                      <Badge variant="outline" className={u.is_active ? 'text-emerald-400' : 'text-red-400'}>{u.is_active ? 'active' : 'inactive'}</Badge>
                      {u.is_admin && <Badge variant="outline" className="text-amber-300">admin</Badge>}
                      {u.user_rank && <Badge variant="outline">{u.user_rank}</Badge>}
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">가입: {new Date(u.created_at).toLocaleString()}</div>
                </button>
              ))}
            </div>
            <div className="flex justify-between items-center mt-4">
              <Button variant="outline" disabled={!hasPrev || loading} onClick={()=> setSkip(Math.max(0, skip - limit))}>이전</Button>
              <div className="text-xs text-muted-foreground">{skip + 1} - {skip + items.length}</div>
              <Button variant="outline" disabled={!hasNext || loading} onClick={()=> setSkip(skip + limit)}>다음</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>상세/관리</CardTitle>
          </CardHeader>
          <CardContent>
            {!selected ? (
              <div className="text-sm text-muted-foreground">왼쪽 목록에서 사용자를 선택하세요.</div>
            ) : (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-lg text-foreground">{selected.nickname} <span className="text-muted-foreground">({selected.site_id})</span></div>
                    <div className="text-xs text-muted-foreground">ID: {selected.id}</div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2"><span className="text-xs text-muted-foreground">활성</span><Switch checked={selected.is_active} onCheckedChange={toggleActive} /></div>
                    <div className="flex items-center gap-2"><span className="text-xs text-muted-foreground">관리자</span><Switch checked={selected.is_admin} onCheckedChange={toggleAdmin} /></div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 rounded border border-border-secondary">
                    <div className="text-xs text-muted-foreground">보유 골드</div>
                    <div className="text-foreground font-semibold">{(selected.cyber_token_balance ?? 0).toLocaleString()} G</div>
                  </div>
                  <div className="p-3 rounded border border-border-secondary">
                    <div className="text-xs text-muted-foreground">마지막 로그인</div>
                    <div className="text-foreground font-semibold">{selected.last_login ? new Date(selected.last_login).toLocaleString() : '-'}</div>
                  </div>
                </div>

                <div className="flex items-end gap-2">
                  <div className="flex-1">
                    <Label htmlFor="rank">등급</Label>
                    <Input id="rank" placeholder="STANDARD|VIP 등" value={rankInput} onChange={(e:any)=>setRankInput((e.target as HTMLInputElement).value)} />
                  </div>
                  <Button variant="outline" onClick={updateRank}>등급 저장</Button>
                </div>

                <div className="flex gap-2">
                  <Button variant="outline" onClick={()=> window.open(`/admin/points`, '_blank')}>골드 지급</Button>
                </div>

                <div>
                  <div className="text-sm text-muted-foreground mb-2">최근 활동 로그</div>
                  <div className="max-h-56 overflow-auto rounded border border-border-secondary divide-y divide-border-secondary">
                    {logs.length === 0 && (
                      <div className="text-xs text-muted-foreground p-3">기록 없음</div>
                    )}
                    {logs.map((l: AdminLog) => (
                      <div key={l.id} className="p-3 text-xs">
                        <div className="text-foreground">{l.action_type}</div>
                        <div className="text-muted-foreground">{new Date(l.created_at).toLocaleString()}</div>
                        {l.details && <pre className="mt-1 text-[10px] text-muted-foreground whitespace-pre-wrap break-all">{String(l.details)}</pre>}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default UsersManager;
