// 레벨 관련 유틸리티 함수들

export interface LevelProgress {
  currentLevel: number;
  currentXP: number;
  xpForNextLevel: number;
  progressPercentage: number;
}

/**
 * 경험치를 기반으로 레벨 진행도를 계산합니다.
 * @param experiencePoints 총 경험치
 * @returns 레벨 진행도 정보
 */
export function calculateLevelProgress(experiencePoints: number): LevelProgress {
  const XP_PER_LEVEL = 500;
  const currentLevel = Math.floor(experiencePoints / XP_PER_LEVEL) + 1;
  const currentXP = experiencePoints % XP_PER_LEVEL;
  const xpForNextLevel = XP_PER_LEVEL;
  const progressPercentage = (currentXP / xpForNextLevel) * 100;

  return {
    currentLevel,
    currentXP,
    xpForNextLevel,
    progressPercentage,
  };
}

/**
 * 레벨에서 필요한 총 경험치를 계산합니다.
 * @param level 목표 레벨
 * @returns 해당 레벨에 필요한 총 경험치
 */
export function getXPRequiredForLevel(level: number): number {
  return (level - 1) * 500;
}

/**
 * 현재 레벨에서 다음 레벨까지 필요한 경험치를 계산합니다.
 * @param experiencePoints 현재 경험치
 * @returns 다음 레벨까지 필요한 경험치
 */
export function getXPToNextLevel(experiencePoints: number): number {
  const XP_PER_LEVEL = 500;
  const currentXP = experiencePoints % XP_PER_LEVEL;
  return XP_PER_LEVEL - currentXP;
}