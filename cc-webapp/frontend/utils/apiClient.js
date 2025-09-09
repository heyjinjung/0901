// Temporary shim to redirect away from legacy client. This module exports a no-op function.
function apiRequest() {
  throw new Error('Legacy utils/apiClient.js is deprecated. Use unifiedApi instead.');
}
module.exports = apiRequest;
