// DEPRECATED. This hook has been removed in favor of unifiedApi.
// Keeping a minimal export to avoid breakage in built artifacts; will be deleted after a clean build.
export function useApiClient() {
  throw new Error('useApiClient is deprecated. Switch to unifiedApi.');
}
export function buildQuery() { return ''; }
