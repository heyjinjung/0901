import { useCallback, useContext } from 'react';
import { FeedbackContext } from '../contexts/FeedbackContext';

export interface ServerFeedback {
    code: string;
    severity?: 'info' | 'success' | 'warn' | 'error';
    message?: string;
    animation?: string | null;
    streak?: number | null;
    meta?: Record<string, any>;
}

export interface FeedbackToast extends ServerFeedback {
    id: string;
    createdAt: number;
}

export interface UseFeedbackResult {
    push: (fb: ServerFeedback) => void;
    fromApi: (payload: { feedback?: any;[k: string]: any }) => void;
}

export function useFeedback(): UseFeedbackResult {
    const ctx = useContext(FeedbackContext);
    if (!ctx) {
        return { push: () => void 0, fromApi: () => void 0 };
    }
    const push = useCallback((fb: ServerFeedback) => { ctx.enqueue(fb); }, [ctx]);
    const fromApi = useCallback((payload: { feedback?: any }) => {
        if (payload && payload.feedback && typeof payload.feedback === 'object') {
            const { feedback } = payload;
            if (feedback.code) {
                push({
                    code: String(feedback.code),
                    severity: feedback.severity || 'info',
                    message: feedback.message,
                    animation: feedback.animation,
                    streak: feedback.streak,
                    meta: feedback.meta,
                });
            }
        }
    }, [push]);
    return { push, fromApi };
}

export default useFeedback;
