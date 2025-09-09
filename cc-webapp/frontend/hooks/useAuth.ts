import { useCallback, useEffect, useRef, useState } from 'react';
import { api } from '@/lib/unifiedApi';

interface AuthUser {
    id: number;
    site_id: string;
    nickname: string;
    cyber_token_balance: number;
    vip_tier?: string;
    created_at?: string;
    // 단일 통화 시스템 - 골드
    gold_balance?: number;
    battlepass_level?: number; // level
    experience?: number; // current exp
    max_experience?: number; // cap
}

interface SignupPayload {
    site_id: string;
    nickname: string;
    phone_number: string;
    password: string;
    invite_code: string;
}

// Backend may also supply refresh_token (optional) – include for future refresh support
interface Tokens { access_token: string; token_type: string; expires_in?: number | null; refresh_token?: string | null }

// Backend actually returns flat structure: { access_token, token_type, user, refresh_token }
interface SignupResponse extends Tokens { user: AuthUser }

// Canonical combined storage key used elsewhere (tokenStorage.js / useAuthToken.ts)
const LEGACY_ACCESS_KEY = 'cc_access_token'; // retained for backward compat (will deprecate)
const LEGACY_EXP_KEY = 'cc_access_exp';
const BUNDLE_KEY = 'cc_auth_tokens';

import { setTokens } from '../utils/tokenStorage';
function writeBundle(access: string, refresh?: string | null, expSeconds?: number | null | undefined) {
    // Unified bundle structure consumed by existing tokenStorage.js & useAuthToken.ts
    const bundle: Record<string, any> = { access_token: access };
    if (refresh) bundle.refresh_token = refresh;
    setTokens(bundle); // tokenStorage.js와 완전 통일
    // Maintain legacy separate keys to avoid breaking older code paths still reading them
    try {
        localStorage.setItem(LEGACY_ACCESS_KEY, access);
        if (expSeconds) {
            const abs = Date.now() + expSeconds * 1000;
            localStorage.setItem(LEGACY_EXP_KEY, abs.toString());
        } else {
            localStorage.removeItem(LEGACY_EXP_KEY);
        }
    } catch { }
}

function readLegacyToken(): { token: string | null; exp: number | null } {
    const token = typeof window !== 'undefined' ? localStorage.getItem(LEGACY_ACCESS_KEY) : null;
    const expStr = typeof window !== 'undefined' ? localStorage.getItem(LEGACY_EXP_KEY) : null;
    return { token, exp: expStr ? parseInt(expStr, 10) : null };
}

export function useAuth() {
    // NOTE: build env currently flags generics; fallback to assertion
    const [user, setUser] = useState(null as AuthUser | null);
    const [loading, setLoading] = useState(false);
    const refreshTimer = useRef(null as number | null);

    const scheduleRefresh = useCallback((exp: number | null) => {
        if (refreshTimer.current) window.clearTimeout(refreshTimer.current);
        if (!exp) return; // no exp claim present
        const now = Date.now();
        const msLeft = exp - now;
        // refresh 60s 전에 시도
        const refreshIn = Math.max(msLeft - 60_000, 10_000);
        refreshTimer.current = window.setTimeout(() => {
            void refresh();
        }, refreshIn);
    }, []);

    const applyTokens = useCallback((t: Tokens) => {
        // Persist in unified bundle + legacy keys
        writeBundle(t.access_token, t.refresh_token, t.expires_in);
        try {
            const payload = JSON.parse(atob(t.access_token.split('.')[1]));
            if (payload.exp) scheduleRefresh(payload.exp * 1000);
        } catch { /* silent */ }
    }, [scheduleRefresh]);

    // 권위 잔액 동기화: /users/balance → { cyber_token_balance }
    const fetchAndMergeBalance = useCallback(async (baseUser: AuthUser | null): Promise<AuthUser | null> => {
        if (!baseUser) return null;
        try {
            const bal = await api.get<any>('users/balance');
            const cyber = bal?.cyber_token_balance ?? baseUser.cyber_token_balance ?? 0;
            // gold_balance 백워드 호환 필드 채움
            const merged: AuthUser = { ...baseUser, cyber_token_balance: cyber, gold_balance: cyber };
            setUser(merged);
            return merged;
        } catch {
            // 실패 시 기존 유저 유지하되 gold_balance 미러링만 보정
            const cyber = baseUser.cyber_token_balance ?? baseUser.gold_balance ?? 0;
            const merged: AuthUser = { ...baseUser, gold_balance: cyber };
            setUser(merged);
            return merged;
        }
    }, []);

    const signup = useCallback(async (data: SignupPayload) => {
        setLoading(true);
        try {
        const res = await api.post<SignupResponse>('auth/signup', data, { auth: false });
            // Backend returns flat structure: { access_token, token_type, user, refresh_token }
            applyTokens(res);
            // 잔액 병합
            const merged = await fetchAndMergeBalance(res.user as AuthUser);
            return merged as AuthUser;
        } finally {
            setLoading(false);
        }
    }, [applyTokens, fetchAndMergeBalance]);

    const login = useCallback(async (site_id: string, password: string) => {
        if (!site_id || !password) {
            throw new Error('아이디와 비밀번호를 입력하세요');
        }
        setLoading(true);
        try {
            try {
                const res = await api.post<any>('auth/login', { site_id: site_id.trim(), password }, { auth: false });
                applyTokens(res);
                if (res && res.user) {
                    const merged = await fetchAndMergeBalance(res.user as AuthUser);
                    return merged as AuthUser;
                }
                // Fallback: profile fetch
                const profile = await api.get<AuthUser>('auth/profile');
                const merged = await fetchAndMergeBalance(profile as AuthUser);
                return merged as AuthUser;
            } catch (e: any) {
                const msg = e?.message || '';
                // 백엔드가 문자열로 dict를 감싼 형태도 포괄
                if (/Invalid credentials|invalid_credentials|아이디\s*또는\s*비밀번호가\s*올바르지\s*않습니다/i.test(msg)) {
                    throw new Error('아이디 또는 비밀번호가 올바르지 않습니다. 다시 시도하세요.');
                }
                if (/Too many failed attempts/i.test(msg)) {
                    throw new Error('로그인 시도 제한에 도달했습니다. 잠시 후 다시 시도하세요.');
                }
                throw e;
            }
        } finally { setLoading(false); }
    }, [applyTokens, fetchAndMergeBalance]);

    const adminLogin = useCallback(async (site_id: string, password: string) => {
        if (!site_id || !password) {
            throw new Error('아이디와 비밀번호를 입력하세요');
        }
        setLoading(true);
        try {
            try {
                const res = await api.post<any>('auth/admin/login', { site_id: site_id.trim(), password }, { auth: false });
                applyTokens(res);
                if (res && res.user) {
                    const merged = await fetchAndMergeBalance(res.user as AuthUser);
                    return merged as AuthUser;
                }
                // Fallback: profile fetch
                const profile = await api.get<AuthUser>('auth/profile');
                const merged = await fetchAndMergeBalance(profile as AuthUser);
                return merged as AuthUser;
            } catch (e: any) {
                const msg = e?.message || '';
                if (/Invalid credentials|invalid_credentials|아이디\s*또는\s*비밀번호가\s*올바르지\s*않습니다/i.test(msg)) {
                    throw new Error('아이디 또는 비밀번호가 올바르지 않습니다. 다시 시도하세요.');
                }
                if (/Only admin users allowed/i.test(msg)) {
                    throw new Error('관리자 계정만 접근할 수 있습니다.');
                }
                if (/Too many failed attempts/i.test(msg)) {
                    throw new Error('로그인 시도 제한에 도달했습니다. 잠시 후 다시 시도하세요.');
                }
                throw e;
            }
        } finally { setLoading(false); }
    }, [applyTokens, fetchAndMergeBalance]);

    // logout 먼저 선언 필요 (refresh 훅 의존 순서 문제 회피)
    const logout = useCallback(() => {
        if (refreshTimer.current) window.clearTimeout(refreshTimer.current);
        try {
            localStorage.removeItem(LEGACY_ACCESS_KEY);
            localStorage.removeItem(LEGACY_EXP_KEY);
            localStorage.removeItem(BUNDLE_KEY);
        } catch { }
        setUser(null);
    }, []);

    const refresh = useCallback(async () => {
        let bundle: any = undefined;
        if (typeof window !== 'undefined') {
            try { bundle = JSON.parse(localStorage.getItem(BUNDLE_KEY) || 'null'); } catch { /* ignore */ }
        }
        const refreshToken: string | undefined = bundle?.refresh_token || undefined;
        const { token } = readLegacyToken();
        if (!token) return null;
        if (!refreshToken) return null;
        try {
        const res = await api.post<Tokens>('auth/refresh', { refresh_token: refreshToken });
            applyTokens(res);
            return res;
        } catch {
            logout();
            return null;
        }
    }, [applyTokens, logout]);

    // 위로 이동 (중복 선언 방지) 

    // init load
    useEffect(() => {
        const { token } = readLegacyToken();
        if (token) {
            api.get<AuthUser>('auth/profile')
                .then(async (u: any) => {
                    // 초기 진입 시에도 잔액 권위 소스와 동기화
                    await fetchAndMergeBalance(u as AuthUser);
                })
                .catch(() => logout());
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return { user, loading, signup, login, adminLogin, refresh, logout };
}

export type UseAuthReturn = ReturnType<typeof useAuth>;
