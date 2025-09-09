// Centralized build info for UI banners, decoupled from deprecated simpleApi
// NEXT_PUBLIC_BUILD_ID should be injected by CI; defaults to 'dev-local'
// Keep minimal to avoid client/runtime bloat.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare const process: any;

export const BUILD_ID: string = (typeof process !== 'undefined' && process?.env?.NEXT_PUBLIC_BUILD_ID) || 'dev-local';

export default BUILD_ID;
