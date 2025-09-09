'use client';

import React from 'react';
import { ToastProvider } from '@/components/NotificationToast';
import { FeedbackProvider } from '../contexts/FeedbackContext';
import { EnsureHydrated } from '@/lib/sync';
import { RealtimeSyncProvider } from '../contexts/RealtimeSyncContext';
import { GlobalStoreProvider } from '@/store/globalStore';

export function Providers({ children }: { children: React.ReactNode }) {
  // Note: avoid console.error here; Next.js dev overlay treats errors as fatal and replaces the document,
  // which breaks E2E/A11y tests. If you need import sanity checks locally, re-enable behind a flag.
  // if (process.env.NEXT_PUBLIC_PROVIDER_IMPORT_SANITY === '1') {
  //   const missing: string[] = [];
  //   if (!(GlobalStoreProvider as any)) missing.push('GlobalStoreProvider(@/store/globalStore)');
  //   if (!(ToastProvider as any)) missing.push('ToastProvider(@/components/NotificationToast)');
  //   if (!(EnsureHydrated as any)) missing.push('EnsureHydrated(@/lib/sync)');
  //   if (!(RealtimeSyncProvider as any)) missing.push('RealtimeSyncProvider(../contexts/RealtimeSyncContext)');
  //   if (!(FeedbackProvider as any)) missing.push('FeedbackProvider(../contexts/FeedbackContext)');
  //   if (missing.length) {
  //     // eslint-disable-next-line no-console
  //     console.warn('[Providers] missing imports:', missing);
  //   }
  // }
  return (
    <GlobalStoreProvider>
      <ToastProvider>
        <EnsureHydrated>
          <RealtimeSyncProvider>
            <FeedbackProvider>{children}</FeedbackProvider>
          </RealtimeSyncProvider>
        </EnsureHydrated>
      </ToastProvider>
    </GlobalStoreProvider>
  );
}
