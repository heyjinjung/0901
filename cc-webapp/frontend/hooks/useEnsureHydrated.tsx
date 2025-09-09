import { useEffect } from 'react';
import { useGlobalStore, hydrateFromServer } from '@/store/globalStore';

export default function useEnsureHydrated() {
  const { state, dispatch } = useGlobalStore();

  useEffect(() => {
    if (state.ready) return;
    // if missing user or balances or stats, hydrate
    hydrateFromServer(dispatch);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
}

export const EnsureHydrated: React.FC<{ children?: React.ReactNode }> = ({ children }) => {
  useEnsureHydrated();
  return <>{children}</>;
};
