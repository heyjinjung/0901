// @ts-nocheck
import React from 'react';
import ReactDOMServer from 'react-dom/server';
import { SideMenu } from '@/components/SideMenu';
import { GlobalStoreProvider } from '@/store/globalStore';

it('server-renders SideMenu using store selectors without user prop', () => {
  const html = ReactDOMServer.renderToString(
    <GlobalStoreProvider>
      <SideMenu
        isOpen={true}
        onClose={() => {}}
        onNavigateToAdminPanel={() => {}}
        onNavigateToEventMissionPanel={() => {}}
        onNavigateToSettings={() => {}}
        onLogout={() => {}}
        onAddNotification={() => {}}
      />
    </GlobalStoreProvider>
  );
  expect(typeof html).toBe('string');
});
