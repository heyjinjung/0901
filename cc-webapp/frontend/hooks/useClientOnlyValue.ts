'use client';

import { useState, useEffect } from 'react';

/**
 * 클라이언트 사이드에서만 값을 제공하는 훅
 * 서버 렌더링 시에는 기본값을 반환하고 클라이언트에서만 실제 값을 반환
 * 하이드레이션 불일치 문제 방지에 사용
 */
export function useClientOnlyValue<T>(clientValue: T, serverValue: T): T {
  // 서버사이드에서는 항상 serverValue 반환
  const isClient = typeof window !== 'undefined';
  
  // 객체 생성을 한 번만 하기 위한 초기값 설정 (useRef는 서버/클라이언트 사이에 값 불일치 문제가 있음)
  // 따라서 useState를 사용하여 serverValue를 초기값으로 설정
    const [initialValue] = useState(serverValue as T);
  
  // 클라이언트 사이드에서 한 번만 실행되는 플래그
    const [hasClientRendered, setHasClientRendered] = useState(false as boolean);
  
  // 클라이언트 사이드에서 마운트 후 1회만 실행
  useEffect(() => {
    if (isClient && !hasClientRendered) {
      setHasClientRendered(true);
    }
  }, []);
  
  // 서버에서는 serverValue, 클라이언트에서는 hasClientRendered가 true면 clientValue, 아니면 initialValue
  if (!isClient) return serverValue;
  return hasClientRendered ? clientValue : initialValue;
}
