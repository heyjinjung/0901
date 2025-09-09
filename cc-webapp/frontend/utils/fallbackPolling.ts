/**
 * WebSocket 연결 실패 시 사용하는 폴백 폴링 시스템
 */

export interface PollingOptions {
    interval: number; // 폴링 간격 (ms)
    maxRetries?: number; // 최대 재시도 횟수
    backoffMultiplier?: number; // 재시도 시 지연 시간 배율
    maxInterval?: number; // 최대 폴링 간격
    onError?: (error: Error, retryCount: number) => void;
    onSuccess?: () => void;
    onMaxRetriesReached?: () => void;
}

export interface PollingTask {
    id: string;
    execute: () => Promise<void>;
    options: PollingOptions;
}

export class FallbackPoller {
    private tasks: Map<string, {
        task: PollingTask;
        timer: number | null;
        retryCount: number;
        currentInterval: number;
        isRunning: boolean;
    }> = new Map();

    /**
     * 폴링 태스크 등록
     */
    register(task: PollingTask): void {
        if (this.tasks.has(task.id)) {
            console.warn(`[FallbackPoller] Task ${task.id} is already registered`);
            return;
        }

        this.tasks.set(task.id, {
            task,
            timer: null,
            retryCount: 0,
            currentInterval: task.options.interval,
            isRunning: false
        });

        console.log(`[FallbackPoller] Registered task: ${task.id}`);
    }

    /**
     * 폴링 태스크 제거
     */
    unregister(taskId: string): void {
        const taskInfo = this.tasks.get(taskId);
        if (!taskInfo) {
            return;
        }

        this.stop(taskId);
        this.tasks.delete(taskId);
        console.log(`[FallbackPoller] Unregistered task: ${taskId}`);
    }

    /**
     * 특정 태스크 시작
     */
    start(taskId: string): void {
        const taskInfo = this.tasks.get(taskId);
        if (!taskInfo) {
            console.warn(`[FallbackPoller] Task ${taskId} not found`);
            return;
        }

        if (taskInfo.isRunning) {
            console.log(`[FallbackPoller] Task ${taskId} is already running`);
            return;
        }

        taskInfo.isRunning = true;
        this.scheduleExecution(taskId);
        console.log(`[FallbackPoller] Started task: ${taskId}`);
    }

    /**
     * 특정 태스크 중지
     */
    stop(taskId: string): void {
        const taskInfo = this.tasks.get(taskId);
        if (!taskInfo) {
            return;
        }

        if (taskInfo.timer) {
            window.clearTimeout(taskInfo.timer);
            taskInfo.timer = null;
        }

        taskInfo.isRunning = false;
        taskInfo.retryCount = 0;
        taskInfo.currentInterval = taskInfo.task.options.interval;
        console.log(`[FallbackPoller] Stopped task: ${taskId}`);
    }

    /**
     * 모든 태스크 시작
     */
    startAll(): void {
        for (const taskId of this.tasks.keys()) {
            this.start(taskId);
        }
    }

    /**
     * 모든 태스크 중지
     */
    stopAll(): void {
        for (const taskId of this.tasks.keys()) {
            this.stop(taskId);
        }
    }

    /**
     * 특정 태스크 즉시 실행
     */
    async executeNow(taskId: string): Promise<void> {
        const taskInfo = this.tasks.get(taskId);
        if (!taskInfo) {
            console.warn(`[FallbackPoller] Task ${taskId} not found`);
            return;
        }

        try {
            await taskInfo.task.execute();
            taskInfo.retryCount = 0;
            taskInfo.currentInterval = taskInfo.task.options.interval;

            if (taskInfo.task.options.onSuccess) {
                taskInfo.task.options.onSuccess();
            }
        } catch (error) {
            console.error(`[FallbackPoller] Task ${taskId} execution failed:`, error);

            if (taskInfo.task.options.onError) {
                taskInfo.task.options.onError(error as Error, taskInfo.retryCount);
            }
        }
    }

    /**
     * 태스크 실행 일정 예약
     */
    private scheduleExecution(taskId: string): void {
        const taskInfo = this.tasks.get(taskId);
        if (!taskInfo || !taskInfo.isRunning) {
            return;
        }

        taskInfo.timer = window.setTimeout(async () => {
            try {
                await taskInfo.task.execute();

                // 성공 시 재시도 카운트 리셋 및 간격 초기화
                taskInfo.retryCount = 0;
                taskInfo.currentInterval = taskInfo.task.options.interval;

                if (taskInfo.task.options.onSuccess) {
                    taskInfo.task.options.onSuccess();
                }

            } catch (error) {
                console.error(`[FallbackPoller] Task ${taskId} failed:`, error);

                // 실패 시 재시도 카운트 증가 및 백오프
                taskInfo.retryCount++;
                const { maxRetries = 5, backoffMultiplier = 1.5, maxInterval = 60000 } = taskInfo.task.options;

                if (taskInfo.retryCount <= maxRetries) {
                    // 백오프 적용
                    taskInfo.currentInterval = Math.min(
                        taskInfo.currentInterval * backoffMultiplier,
                        maxInterval
                    );

                    if (taskInfo.task.options.onError) {
                        taskInfo.task.options.onError(error as Error, taskInfo.retryCount);
                    }
                } else {
                    // 최대 재시도 횟수 도달
                    console.error(`[FallbackPoller] Task ${taskId} reached max retries (${maxRetries})`);

                    if (taskInfo.task.options.onMaxRetriesReached) {
                        taskInfo.task.options.onMaxRetriesReached();
                    }

                    this.stop(taskId);
                    return;
                }
            }

            // 다음 실행 예약
            if (taskInfo.isRunning) {
                this.scheduleExecution(taskId);
            }
        }, taskInfo.currentInterval);
    }

    /**
     * 현재 실행 중인 태스크 목록
     */
    getRunningTasks(): string[] {
        const running: string[] = [];
        for (const [taskId, taskInfo] of this.tasks.entries()) {
            if (taskInfo.isRunning) {
                running.push(taskId);
            }
        }
        return running;
    }

    /**
     * 태스크 상태 정보
     */
    getTaskStatus(taskId: string) {
        const taskInfo = this.tasks.get(taskId);
        if (!taskInfo) {
            return null;
        }

        return {
            id: taskId,
            isRunning: taskInfo.isRunning,
            retryCount: taskInfo.retryCount,
            currentInterval: taskInfo.currentInterval,
            nextExecutionIn: taskInfo.timer ? taskInfo.currentInterval : null
        };
    }

    /**
     * 모든 태스크 해제 (메모리 정리)
     */
    dispose(): void {
        this.stopAll();
        this.tasks.clear();
        console.log('[FallbackPoller] Disposed all tasks');
    }
}

/**
 * 글로벌 폴러 인스턴스
 */
export const globalFallbackPoller = new FallbackPoller();

/**
 * 실시간 동기화용 폴링 태스크 팩토리
 */
export function createSyncPollingTasks(
    refreshProfile: () => Promise<void>,
    refreshStreaks: () => Promise<void>,
    refreshEvents: () => Promise<void>,
    options: Partial<PollingOptions> = {}
): PollingTask[] {
    const defaultOptions: PollingOptions = {
        interval: 30000, // 30초
        maxRetries: 3,
        backoffMultiplier: 2,
        maxInterval: 120000, // 2분
        ...options
    };

    return [
        {
            id: 'sync-profile',
            execute: refreshProfile,
            options: {
                ...defaultOptions,
                interval: 60000 // 프로필은 1분마다
            }
        },
        {
            id: 'sync-streaks',
            execute: refreshStreaks,
            options: {
                ...defaultOptions,
                interval: 30000 // 스트릭은 30초마다
            }
        },
        {
            id: 'sync-events',
            execute: refreshEvents,
            options: {
                ...defaultOptions,
                interval: 45000 // 이벤트는 45초마다
            }
        }
    ];
}
