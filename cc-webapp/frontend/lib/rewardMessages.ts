// 중앙 집중 사용자 보상/스트릭 관련 메시지 모듈
// 번들 문자열 diff 추적 및 다국어/i18n 전환 준비용 단일 소스
// 함수형 메시지는 파라미터 (gold, xp, streak 등)을 받아 동적으로 생성

export const rewardMessages = {
    loginRequired: '🔐 로그인 후 오늘의 출석 보상을 받을 수 있어요! 먼저 로그인해주세요 😊',
    alreadyClaimed: '오늘 출석 보상은 이미 받으셨어요 😎 내일 또 방문하면 더 많은 보너스가 기다립니다!',
    networkFail: '🌐 연결이 잠시 불안정합니다. 인터넷 상태 확인 후 다시 시도해주세요.',
    success: (gold: number, xp: number, streakCount: number) =>
        `🎁 ${streakCount}일째 출석! +${gold.toLocaleString()}G / +${xp}XP 획득! 내일 더 커집니다!`,
    genericFail: (msg: string) => `😢 보상 수령에 실패했어요: ${msg} 잠시 후 다시 시도해주세요.`,
} as const;

export type RewardMessages = typeof rewardMessages;
