This folder contains lightweight development tools to trace frontend API calls and record simple UI actions.

Files:
- interactionTracker.js: recordApiCall(record) / recordApiResult(id, result) / getInteractionLogs() / sendLogsToBackend()
- uiActionRecorder.js: initUiActionRecorder(opts) / undoLastAction() / getActionHistory()

Usage:
- In app entrypoint (e.g., _app.js), call `import { initUiRecorder } from './utils/apiClient'; initUiRecorder();` to start recording UI actions.
- To programmatically get traces: `import { getApiTraceLogs, sendApiTraceToBackend } from './utils/apiClient';`
- The backend includes a dev-only POST /api/dev/logs endpoint to accept logs (prints to backend stdout).

Note: These utilities are intended for local development only. Do not ship to production.
