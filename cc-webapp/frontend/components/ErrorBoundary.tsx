'use client';

import React, { Component } from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw, Home, Bug } from 'lucide-react';
import { Button } from './ui/button';

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  onError?: (error: Error, errorInfo: any) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: any;
  errorId: string;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
      errorId: Date.now().toString()
    };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    this.setState({
      error,
      errorInfo,
      errorId: Date.now().toString()
    });

    // 에러 로깅
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // 프로덕션에서는 에러 리포팅 서비스로 전송
    if (process.env.NODE_ENV === 'production') {
      this.reportError(error, errorInfo);
    }

    // 부모 컴포넌트에 에러 전달
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  private reportError = (error: Error, errorInfo: any) => {
    // 실제 프로덕션에서는 Sentry, LogRocket 등의 서비스 사용
    const errorReport = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    // 여기서 에러 리포팅 서비스로 전송
    console.log('Error Report:', errorReport);
  };

  private handleReload = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    // 로컬 스토리지 정리 후 홈으로
    localStorage.removeItem('game-user');
    window.location.href = '/';
  };

  private handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: ''
    });
  };

  render() {
    if (this.state.hasError) {
      // 커스텀 fallback이 있다면 사용
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // 기본 에러 UI
      return (
        <div className="min-h-screen bg-gradient-to-br from-background via-black to-error-soft flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="glass-effect rounded-2xl p-8 max-w-md w-full text-center"
          >
            <motion.div
              animate={{ rotate: [0, -5, 5, -5, 0] }}
              transition={{ duration: 0.5, repeat: 3 }}
              className="w-16 h-16 bg-error rounded-full flex items-center justify-center mx-auto mb-6"
            >
              <AlertTriangle className="w-8 h-8 text-white" />
            </motion.div>

            <h1 className="text-2xl font-bold text-error mb-4">
              앗! 문제가 발생했어요
            </h1>
            
            <p className="text-muted-foreground mb-6">
              예상치 못한 오류가 발생했습니다. 잠시 후 다시 시도해주세요.
            </p>

            {/* 개발 모드에서만 에러 세부사항 표시 */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mb-6 text-left">
                <summary className="cursor-pointer text-warning mb-2 flex items-center gap-2">
                  <Bug className="w-4 h-4" />
                  개발자 정보
                </summary>
                <div className="bg-secondary/20 rounded-lg p-4 text-xs">
                  <div className="text-error font-mono mb-2">
                    {this.state.error.message}
                  </div>
                  <div className="text-muted-foreground font-mono">
                    {this.state.error.stack?.slice(0, 300)}...
                  </div>
                </div>
              </details>
            )}

            <div className="space-y-3">
              <Button
                onClick={this.handleRetry}
                className="w-full bg-gradient-game hover:opacity-90 btn-hover-lift"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                다시 시도
              </Button>

              <Button
                onClick={this.handleReload}
                variant="outline"
                className="w-full border-border-secondary hover:border-primary btn-hover-lift"
              >
                페이지 새로고침
              </Button>

              <Button
                onClick={this.handleGoHome}
                variant="outline"
                className="w-full border-border-secondary hover:border-warning text-warning btn-hover-lift"
              >
                <Home className="w-4 h-4 mr-2" />
                홈으로 돌아가기
              </Button>
            </div>

            <div className="mt-6 pt-4 border-t border-border-secondary">
              <p className="text-xs text-muted-foreground">
                오류 ID: {this.state.errorId}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                문제가 지속되면 고객지원에 문의해주세요.
              </p>
            </div>
          </motion.div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

// Hook for functional components
export function useErrorHandler() {
  const handleError = React.useCallback((error: Error, errorInfo?: any) => {
    console.error('Manual error handling:', error, errorInfo);
    
    // 에러를 상위 ErrorBoundary로 전파
    throw error;
  }, []);

  return handleError;
}

// 비동기 에러 처리용 훅
export function useAsyncError() {
  const [, setError] = React.useState(null as Error | null);
  
  return React.useCallback((error: Error) => {
    setError(() => {
      throw error;
    });
  }, []);
}

// 에러 복구용 훅
export function useErrorRecovery(onRecover?: () => void) {
  const [retryCount, setRetryCount] = React.useState(0);
  const [isRecovering, setIsRecovering] = React.useState(false);

  const recover = React.useCallback(async () => {
    if (retryCount >= 3) {
      throw new Error('Maximum retry attempts reached');
    }

    setIsRecovering(true);
  setRetryCount((prev: number) => prev + 1);

    try {
      if (onRecover) {
        await onRecover();
      }
      setRetryCount(0);
    } finally {
      setIsRecovering(false);
    }
  }, [retryCount, onRecover]);

  return { recover, retryCount, isRecovering, canRetry: retryCount < 3 };
}