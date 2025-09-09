// @ts-nocheck
// Mock realtime hooks to avoid provider dependency during SSR render in tests.
jest.mock('@/hooks/useRealtimeData', () => ({
  useRealtimePurchaseBadge: () => ({ pendingCount: 0 })
}));

import React from 'react';
import ReactDOMServer from 'react-dom/server';
import { BottomNavigation } from '@/components/BottomNavigation';
import { GlobalStoreProvider } from '@/store/globalStore';

describe('BottomNavigation selectors', () => {
  it('server-renders without user prop using store selectors', () => {
    const html = ReactDOMServer.renderToString(
      <GlobalStoreProvider>
        <BottomNavigation currentScreen="home-dashboard" onNavigate={() => {}} />
      </GlobalStoreProvider>
    );
    expect(typeof html).toBe('string');
    expect(html.length).toBeGreaterThan(0);
  });
});
