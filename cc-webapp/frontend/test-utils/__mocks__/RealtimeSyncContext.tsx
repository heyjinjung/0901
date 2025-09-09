import React from 'react';

// Minimal mock provider/hook to satisfy components in tests
const initial = {
  state: {
    connection: { status: 'disconnected' },
    profile: {},
    achievements: {},
    events: {},
  },
};
const Ctx = React.createContext<any>(initial);

export function RealtimeSyncProvider({ children }: { children?: React.ReactNode }) {
  return <Ctx.Provider value={initial}>{children}</Ctx.Provider>;
}

export function useRealtimeSync() {
  return React.useContext(Ctx);
}

export default { RealtimeSyncProvider, useRealtimeSync };
