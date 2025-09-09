import { useCallback, useRef, useEffect, useMemo, useState } from 'react';

// 디바운스 훅
export function useDebounce<T extends (...args: unknown[]) => unknown>(
  callback: T,
  delay: number
): T {
  const timeoutRef = useRef(null as NodeJS.Timeout | null);
  
  return useCallback((...args: Parameters<T>) => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    timeoutRef.current = setTimeout(() => {
      callback(...args);
    }, delay);
  }, [callback, delay]) as T;
}

// 쓰로틀 훅
export function useThrottle<T extends (...args: unknown[]) => unknown>(
  callback: T,
  delay: number
): T {
  const lastCallRef = useRef(0 as number);
  const timeoutRef = useRef(null as NodeJS.Timeout | null);
  
  return useCallback((...args: Parameters<T>) => {
    const now = Date.now();
    
    if (now - lastCallRef.current >= delay) {
      lastCallRef.current = now;
      callback(...args);
    } else {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      timeoutRef.current = setTimeout(() => {
        lastCallRef.current = Date.now();
        callback(...args);
      }, delay - (now - lastCallRef.current));
    }
  }, [callback, delay]) as T;
}

// 메모리 안전한 타이머 훅
export function useSafeTimer() {
  const timersRef = useRef(new Set() as Set<NodeJS.Timeout>);
  const intervalsRef = useRef(new Set() as Set<NodeJS.Timeout>);
  
  const setTimeout = useCallback((callback: () => void, delay: number) => {
    const timer = globalThis.setTimeout(() => {
      timersRef.current.delete(timer);
      callback();
    }, delay);
    
    timersRef.current.add(timer);
    return timer;
  }, []);
  
  const setInterval = useCallback((callback: () => void, delay: number) => {
    const interval = globalThis.setInterval(callback, delay);
    intervalsRef.current.add(interval);
    return interval;
  }, []);
  
  const clearTimeout = useCallback((timer: NodeJS.Timeout) => {
    globalThis.clearTimeout(timer);
    timersRef.current.delete(timer);
  }, []);
  
  const clearInterval = useCallback((interval: NodeJS.Timeout) => {
    globalThis.clearInterval(interval);
    intervalsRef.current.delete(interval);
  }, []);
  
  // 컴포넌트 언마운트시 모든 타이머 정리
  useEffect(() => {
    return () => {
  timersRef.current.forEach((timer: NodeJS.Timeout) => globalThis.clearTimeout(timer));
  intervalsRef.current.forEach((interval: NodeJS.Timeout) => globalThis.clearInterval(interval));
      timersRef.current.clear();
      intervalsRef.current.clear();
    };
  }, []);
  
  return { setTimeout, setInterval, clearTimeout, clearInterval };
}

// 애니메이션 최적화를 위한 훅
export function useAnimationFrame(callback: (time: number) => void, enabled: boolean = true) {
  const requestRef = useRef(null as number | null);
  const callbackRef = useRef(callback);
  
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);
  
  useEffect(() => {
    if (!enabled) return;
    
    const animate = (time: number) => {
      callbackRef.current(time);
      requestRef.current = requestAnimationFrame(animate);
    };
    
    requestRef.current = requestAnimationFrame(animate);
    
    return () => {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, [enabled]);
}

// 렌더링 최적화를 위한 가시성 훅
export function useIntersectionObserver(
  elementRef: React.RefObject<Element>,
  options?: IntersectionObserverInit
) {
  const [isVisible, setIsVisible] = useState(false);
  
  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;
    
    const observer = new IntersectionObserver(
      ([entry]) => {
        setIsVisible(entry.isIntersecting);
      },
      {
        threshold: 0,
        rootMargin: '50px',
        ...options
      }
    );
    
    observer.observe(element);
    
    return () => {
      observer.unobserve(element);
    };
  }, [elementRef, options]);
  
  return isVisible;
}

// 메모리 사용량 모니터링
interface MemoryInfo {
  used: number;
  total: number;
  limit: number;
}

export function useMemoryMonitor() {
  const [memoryInfo, setMemoryInfo] = useState(null as MemoryInfo | null);
  
  useEffect(() => {
    // performance.memory는 Chrome에서만 사용 가능
    const perf = performance as Performance & { memory?: { usedJSHeapSize?: number; totalJSHeapSize?: number; jsHeapSizeLimit?: number } };
    if (perf.memory) {
      const updateMemoryInfo = () => {
        const memory = perf.memory;
        if (!memory) return;
        setMemoryInfo({
          used: memory.usedJSHeapSize ?? 0,
          total: memory.totalJSHeapSize ?? 0,
          limit: memory.jsHeapSizeLimit ?? 0
        });
      };
      
      updateMemoryInfo();
      const interval = setInterval(updateMemoryInfo, 5000);
      
      return () => clearInterval(interval);
    }
  }, []);
  
  return memoryInfo;
}

// 이미지 지연 로딩
export function useLazyImage(src: string, placeholder?: string) {
  const [imageSrc, setImageSrc] = useState(placeholder || '');
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  
  useEffect(() => {
    const img = new Image();
    
    img.onload = () => {
      setImageSrc(src);
      setIsLoading(false);
    };
    
    img.onerror = () => {
      setHasError(true);
      setIsLoading(false);
    };
    
    img.src = src;
  }, [src]);
  
  return { imageSrc, isLoading, hasError };
}

// 배치 업데이트를 위한 훅
export function useBatchUpdate<T>(initialValue: T, batchDelay: number = 100) {
  const [value, setValue] = useState(initialValue);
  const pendingUpdatesRef = useRef([] as Array<(prev: T) => T>);
  const timeoutRef = useRef(null as NodeJS.Timeout | null);
  
  const batchUpdate = useCallback((updater: (prev: T) => T | T) => {
    const updateFn = typeof updater === 'function' ? updater as (prev: T) => T : () => updater;
    pendingUpdatesRef.current.push(updateFn);
    
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    
    timeoutRef.current = setTimeout(() => {
      setValue((prev: T) => {
        return pendingUpdatesRef.current.reduce((acc: T, update: (p: T) => T) => update(acc), prev);
      });
      pendingUpdatesRef.current = [];
    }, batchDelay);
  }, [batchDelay]);
  
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);
  
  return [value, batchUpdate] as const;
}

// 가상화를 위한 훅 (대용량 리스트 최적화)
export function useVirtualization<T>(
  items: T[],
  itemHeight: number,
  containerHeight: number,
  overscan: number = 5
) {
  const [scrollTop, setScrollTop] = useState(0);
  
  const visibleItems = useMemo(() => {
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
    const endIndex = Math.min(
      items.length - 1,
      Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
    );
    
    return {
      startIndex,
      endIndex,
      items: items.slice(startIndex, endIndex + 1),
      totalHeight: items.length * itemHeight,
      offsetY: startIndex * itemHeight
    };
  }, [items, itemHeight, containerHeight, scrollTop, overscan]);
  
  const handleScroll = useCallback((event: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(event.currentTarget.scrollTop);
  }, []);
  
  return {
    ...visibleItems,
    handleScroll
  };
}

// 웹 워커를 사용한 백그라운드 처리
export function useWebWorker<T, R>(
  workerFunction: (data: T) => R,
  dependencies: unknown[] = []
) {
  const workerRef = useRef(null as Worker | null);
  
  useEffect(() => {
    const workerCode = `
      self.onmessage = function(e) {
        const result = (${workerFunction.toString()})(e.data);
        self.postMessage(result);
      }
    `;
    
    const blob = new Blob([workerCode], { type: 'application/javascript' });
    workerRef.current = new Worker(URL.createObjectURL(blob));
    
    return () => {
      if (workerRef.current) {
        workerRef.current.terminate();
      }
    };
  }, dependencies);
  
  const runWorker = useCallback((data: T): Promise<R> => {
    return new Promise((resolve, reject) => {
      if (!workerRef.current) {
        reject(new Error('Worker not initialized'));
        return;
      }
      
      const handleMessage = (e: MessageEvent) => {
        workerRef.current?.removeEventListener('message', handleMessage);
        resolve(e.data);
      };
      
      const handleError = (error: ErrorEvent) => {
        workerRef.current?.removeEventListener('error', handleError);
        reject(error);
      };
      
      workerRef.current.addEventListener('message', handleMessage);
      workerRef.current.addEventListener('error', handleError);
      workerRef.current.postMessage(data);
    });
  }, []);
  
  return runWorker;
}