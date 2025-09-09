// 런타임 플래그 헬퍼: 환경변수 또는 localStorage로 제어
// - STRICT_STATS_PARITY: '1'이면 통계 파리티 스펙을 엄격 모드로 간주
// - E2E_DISABLE_STATS_PARITY: '1'이면 완전히 비활성화

// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const process: any;

export function isStatsParityStrict(): boolean {
    try {
        const env = (typeof process !== 'undefined' ? (process as any).env : undefined) || {};
        if (env.NEXT_PUBLIC_STRICT_STATS_PARITY === '1') return true;
        if (typeof window !== 'undefined') {
            const ls = window.localStorage?.getItem('STRICT_STATS_PARITY');
            if (ls === '1' || (ls && ls.toLowerCase() === 'true')) return true;
        }
    } catch { }
    return false;
}

export function isStatsParityDisabled(): boolean {
    try {
        const env = (typeof process !== 'undefined' ? (process as any).env : undefined) || {};
        if (env.NEXT_PUBLIC_DISABLE_STATS_PARITY === '1') return true;
        if (typeof window !== 'undefined') {
            const ls = window.localStorage?.getItem('E2E_DISABLE_STATS_PARITY');
            if (ls === '1' || (ls && ls.toLowerCase() === 'true')) return true;
        }
    } catch { }
    return false;
}
