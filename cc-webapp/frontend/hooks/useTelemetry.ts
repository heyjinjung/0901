import { useCallback } from 'react';

// Lightweight telemetry hook (console + optional window buffer)
// Events: fetch_start, fetch_success, fetch_skip, fetch_error, action
// Future: ship to /api/telemetry or Prometheus pushgateway via backend batching.
export interface TelemetryEvent {
  ts: number; // epoch ms
  name: string; // event name
  meta?: Record<string, any>;
}

// Provide global buffer (best-effort)
if (typeof window !== 'undefined') {
  (window as any).__telemetryBuffer = (window as any).__telemetryBuffer || [];
}

export default function useTelemetry(prefix = 'panel') {
  const record = useCallback((name: string, meta?: Record<string, any>) => {
    const evt: TelemetryEvent = { ts: Date.now(), name: `${prefix}:${name}`, meta };
    try {
      if (typeof window !== 'undefined') {
        (window as any).__telemetryBuffer.push(evt);
      }
      // For now just log; swap with network post later
      if (process.env.NODE_ENV !== 'production') {
        // eslint-disable-next-line no-console
        console.debug('[telemetry]', evt);
      }
    } catch {
      /* swallow */
    }
  }, [prefix]);

  return { record };
}
