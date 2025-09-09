// 간단한 로컬 스토리지 기반 액세스 토큰 취득 훅 (MVP 임시)
// TODO: 후속 - refresh 토큰 회전/만료 처리 통합
import { useCallback, useRef } from 'react';

interface TokenBundle {
    access_token?: string;
    refresh_token?: string;
    expires_at?: number; // epoch seconds (optional precomputed)
}

interface DecodedJwt { exp?: number;[k: string]: any }

function decodeJwtExp(token?: string): number | undefined {
    if (!token) return undefined;
    try {
        const payload = token.split('.')[1];
        if (!payload) return undefined;
        const json = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')));
        return (json as DecodedJwt).exp;
    } catch { return undefined; }
}

export function useAuthToken() {
    // generic 제한 회피: any ref 후 캐스팅
    const refreshingRef = useRef(null as unknown as Promise<string | undefined> | null);

    const readBundle = useCallback((): TokenBundle | undefined => {
        try {
            if (typeof window === 'undefined') return undefined;
            const raw = localStorage.getItem('cc_auth_tokens');
            if (raw) return JSON.parse(raw) as TokenBundle;
            // 자동 마이그레이션: 이전 단일 키에서 번들 생성 (최소침습)
            const legacyAccess = localStorage.getItem('cc_access_token');
            if (legacyAccess) {
                const bundle: TokenBundle = { access_token: legacyAccess };
                try { localStorage.setItem('cc_auth_tokens', JSON.stringify(bundle)); } catch { /* ignore */ }
                return bundle;
            }
            return undefined;
        } catch { return undefined; }
    }, []);

    const isExpired = useCallback((access?: string): boolean => {
        const exp = decodeJwtExp(access);
        if (!exp) return false; // 못 읽으면 관대 처리
        const now = Math.floor(Date.now() / 1000);
        // 30초 버퍼
        return now >= (exp - 30);
    }, []);

    const getAccessToken = useCallback((): string | undefined => {
        const bundle = readBundle();
        return bundle?.access_token;
    }, [readBundle]);

    const getValidAccessToken = useCallback(async (): Promise<string | undefined> => {
        const bundle = readBundle();
        if (!bundle?.access_token) return undefined;
        if (!isExpired(bundle.access_token)) return bundle.access_token;
        // 만료된 경우 refresh 시도
        if (!bundle.refresh_token) return bundle.access_token; // fallback: 그대로 반환
        if (!refreshingRef.current) {
            refreshingRef.current = (async () => {
                try {
                    // 추후 실제 refresh 엔드포인트 확정 시 fetch 교체
                    const resp = await fetch('/api/auth/refresh', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ refresh_token: bundle.refresh_token })
                    });
                    if (!resp.ok) throw new Error('refresh failed');
                    const data = await resp.json();
                    const next: TokenBundle = {
                        access_token: data.access_token,
                        refresh_token: data.refresh_token || bundle.refresh_token,
                    };
                    // optional: compute expires_at
                    const exp = decodeJwtExp(next.access_token);
                    if (exp) next.expires_at = exp;
                    localStorage.setItem('cc_auth_tokens', JSON.stringify(next));
                    return next.access_token;
                } catch {
                    return bundle.access_token; // 실패 시 기존 유지
                } finally {
                    refreshingRef.current = null;
                }
            })();
        }
        return refreshingRef.current;
    }, [isExpired, readBundle]);

    return { getAccessToken, getValidAccessToken, isExpired };
}

export default useAuthToken;
