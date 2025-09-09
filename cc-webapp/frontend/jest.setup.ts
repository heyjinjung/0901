/// <reference types="jest" />
import type { } from 'jest';
declare const beforeAll: (fn: () => void) => void;
declare const afterAll: (fn: () => void) => void;

// Polyfill MessageChannel early for React 19 server rendering in Jest
// Force a lightweight no-op implementation to avoid open handles (MESSAGEPORT)
(() => {
  const g: any = globalThis as any;
  g.MessageChannel = class {
    port1 = { postMessage: () => { }, close: () => { } };
    port2 = { postMessage: () => { }, close: () => { } };
  };
})();

// Mock realtime badge hook to avoid provider dependency in unit tests
const jestAny: any = globalThis as any;
if (jestAny.jest && typeof jestAny.jest.mock === 'function') {
  jestAny.jest.mock('@/hooks/useRealtimeData', () => ({
    useRealtimePurchaseBadge: () => ({ pendingCount: 0 })
  }));
}
import '@testing-library/jest-dom';

// Polyfill TextEncoder/TextDecoder for Node test runtime (React 19 & Next 15)
(() => {
  const g: any = globalThis as any;
  if (!g.TextEncoder || !g.TextDecoder) {
    try {
      const { TextEncoder, TextDecoder } = require('util');
      if (!g.TextEncoder) g.TextEncoder = TextEncoder;
      if (!g.TextDecoder) g.TextDecoder = TextDecoder as any;
    } catch { }
  }
})();

// Reduce console noise in smoke tests
const originalError = console.error;
beforeAll(() => {
  console.error = (...args: any[]) => {
    const msg = args.join(' ');
    if (msg.includes('Warning:')) return;
    originalError(...args);
  };
});

afterAll(() => {
  console.error = originalError;
});
