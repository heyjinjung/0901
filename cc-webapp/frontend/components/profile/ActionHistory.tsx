"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { History } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { api as unifiedApi } from '@/lib/unifiedApi';

type GameHistoryItem = {
	id: string | number;
	game_type?: string;
	action_type?: string;
	amount?: number;
	result?: string;
	created_at?: string;
};

type Page = {
	items: GameHistoryItem[];
	total?: number;
};

// 서버 권위 이력 API: GET /api/games/history?limit&offset
async function fetchHistory(limit: number, offset: number): Promise<Page> {
	const data: any = await unifiedApi.get(`games/history?limit=${encodeURIComponent(limit)}&offset=${encodeURIComponent(offset)}`);
	const items: GameHistoryItem[] = Array.isArray(data?.items)
		? data.items
		: Array.isArray(data)
		? data
		: [];
	const total: number | undefined = Number.isFinite(Number(data?.total))
		? Number(data.total)
		: undefined;
	return { items, total };
}

export default function ActionHistory({ pageSize = 10 }: { pageSize?: number }) {
	const [items, setItems] = useState([] as GameHistoryItem[]);
	const [page, setPage] = useState(0); // 0-base
	const [total, setTotal] = useState(undefined as number | undefined);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState(null as string | null);

		const load = useCallback(
		async (p: number) => {
			setLoading(true);
			setError(null);
			try {
				// E2E 전용: 로컬 스텁이 켜져 있으면 네트워크 없이 결정적 페이징 데이터를 렌더링
				try {
					const stubFlag = typeof window !== 'undefined' ? window.localStorage.getItem('E2E_ACTION_HISTORY_STUB') : null;
					if (stubFlag) {
						const stubTotal = 25; // 3페이지(10/10/5)로 고정
						const start = p * pageSize;
						const end = Math.min(start + pageSize, stubTotal);
						const pageItems: GameHistoryItem[] = Array.from({ length: Math.max(0, end - start) }, (_, i) => {
							const id = start + i + 1;
							return {
								id: `stub-${id}`,
								game_type: 'stub-game',
								action_type: 'stub-action',
								amount: (id % 2 === 0 ? 10 : -5),
								result: id % 2 === 0 ? 'win' : 'lose',
								created_at: new Date(Date.now() - id * 1000 * 60).toISOString(),
							};
						});
						setItems(pageItems);
						setTotal(stubTotal);
						setLoading(false);
						return; // 네트워크 호출 우회
					}
				} catch {
					// noop
				}

				const offset = p * pageSize;
				const { items: pageItems, total: t } = await fetchHistory(pageSize, offset);
				// 중복 제거(id 중심)
				const seen = new Set<string | number>();
			const merged = pageItems.filter((it: GameHistoryItem) => {
					const key = it.id ?? `${it.game_type}:${it.action_type}:${it.created_at}`;
					if (seen.has(key)) return false;
					seen.add(key);
					return true;
				});
				setItems(merged);
				if (typeof t === 'number') setTotal(t);
			} catch (e: any) {
				setError(e?.message || '이력을 불러오지 못했습니다');
			} finally {
				setLoading(false);
			}
		},
		[pageSize]
	);

		useEffect(() => {
		load(page);
	}, [load, page]);

	const hasPrev = page > 0;
	const hasNext =
		typeof total === 'number' ? (page + 1) * pageSize < total : items.length === pageSize; // total 미제공 시 휴리스틱

	return (
		<motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
			<Card className="glass-effect p-4 border-border/40">
				<div className="flex items-center justify-between mb-3">
					<div className="flex items-center gap-2">
						<History className="w-4 h-4 text-primary" />
						<h4 className="text-sm font-semibold">최근 액션 이력</h4>
					</div>
					<Badge variant="secondary" className="glass-metal text-xs">
						{typeof total === 'number' ? total : '—'} 전체
					</Badge>
				</div>

				{/* 항상 컨테이너를 렌더링하여 E2E가 안정적으로 찾을 수 있도록 함 */}
				<div className="space-y-2 max-h-64 overflow-auto pr-1" data-testid="action-history-list">
					{loading ? (
						<div className="text-center text-muted-foreground py-6 text-sm">불러오는 중…</div>
					) : error ? (
						<div className="text-center text-red-500 py-6 text-sm">{error}</div>
					) : items.length === 0 ? (
						<div className="text-center text-muted-foreground py-6 text-sm">이력이 없습니다.</div>
					) : (
						items.map((it: GameHistoryItem) => (
							<div
								key={`${it.id}`}
								data-key={`${it.id}`}
								className="flex items-center justify-between p-3 rounded-lg border border-border/30 glass-metal-hover"
							>
								<div className="text-sm">
									<div className="font-medium">
										{it.game_type || it.action_type || '기록'}
									</div>
									<div className="text-xs text-muted-foreground">
										{it.created_at ? new Date(it.created_at).toLocaleString() : ''}
									</div>
								</div>
								<div className="text-right">
									{typeof it.amount === 'number' && (
										<div className={`text-xs ${it.amount >= 0 ? 'text-success' : 'text-error'}`}>
											{it.amount >= 0 ? `+${it.amount}` : it.amount}
										</div>
									)}
									{it.result && (
										<div className="text-[11px] text-muted-foreground">{it.result}</div>
									)}
								</div>
							</div>
						))
					)}
				</div>

				<div className="flex items-center justify-between mt-3">
					<button
						className="text-xs px-2 py-1 rounded border border-border/50 disabled:opacity-50"
						onClick={() => setPage((p: number) => Math.max(0, p - 1))}
						disabled={!hasPrev}
						data-testid="action-prev"
					>
						이전
					</button>
					<div className="text-xs text-muted-foreground">페이지 {page + 1}</div>
					<button
						className="text-xs px-2 py-1 rounded border border-border/50 disabled:opacity-50"
						onClick={() => setPage((p: number) => p + 1)}
						disabled={!hasNext}
						data-testid="action-next"
					>
						다음
					</button>
				</div>
			</Card>
		</motion.div>
	);
}
