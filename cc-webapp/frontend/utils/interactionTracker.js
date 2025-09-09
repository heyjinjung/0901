// interactionTracker.js
// 개발용: 프론트의 API 요청과 주요 인터랙션을 수집/노출합니다.
const logs = [];

export function recordApiCall(entry) {
  try {
    const now = new Date().toISOString();
    const id = logs.length + 1;
    const record = { id, ts: now, ...entry };
    logs.push(record);
    // eslint-disable-next-line no-console
    console.log('%c[InteractionTracker] API recorded', 'color:#6A1B9A;font-weight:bold', record);
    return id;
  } catch (e) {
    // eslint-disable-next-line no-console
    console.warn('[InteractionTracker] record failed', e);
    return null;
  }
}

export function recordApiResult(id, result) {
  try {
    const idx = logs.findIndex(l => l.id === id);
    if (idx !== -1) {
      logs[idx] = { ...logs[idx], result, resultTs: new Date().toISOString() };
      // eslint-disable-next-line no-console
      console.log('%c[InteractionTracker] API result attached', 'color:#2E7D32', logs[idx]);
    }
  } catch (e) {
    // eslint-disable-next-line no-console
    console.warn('[InteractionTracker] recordApiResult failed', e);
  }
}

export function getInteractionLogs() {
  return logs.slice();
}

export async function sendLogsToBackend() {
  try {
    // NOTE: ESModule 환경에서 직접 import가 더 안전하지만, 이 파일은 .js이므로 동적 import 사용
    const mod = await import('../lib/unifiedApi');
    const origin = (mod.API_ORIGIN || process.env.NEXT_PUBLIC_API_ORIGIN || 'http://127.0.0.1:8000');
    const url = origin.replace(/\/+$/, '') + '/api/dev/logs';
    // Best-effort: non-blocking
    await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ logs }),
    });
    // eslint-disable-next-line no-console
    console.log('[InteractionTracker] sent logs to backend');
  } catch (e) {
    // eslint-disable-next-line no-console
    console.warn('[InteractionTracker] send logs failed', e);
  }
}

export function clearLogs() {
  logs.length = 0;
}

export default {
  recordApiCall,
  recordApiResult,
  getInteractionLogs,
  sendLogsToBackend,
  clearLogs,
};
