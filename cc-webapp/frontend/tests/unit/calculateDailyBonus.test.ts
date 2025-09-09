/// <reference types="jest" />

import { calculateDailyBonus } from '../../utils/userUtils';

describe('calculateDailyBonus', () => {
  test('raw dailyStreak = 0 -> displayStreak=1 bonus and updated streak becomes 1', () => {
    const user: any = {
      goldBalance: 0,
      dailyStreak: 0,
      lastLogin: new Date(),
    };

    const { updatedUser, bonusGold } = calculateDailyBonus(user);

    expect(bonusGold).toBe(1000 + 1 * 200); // default base + 1*perStreak
    expect(updatedUser.dailyStreak).toBe(1);
    expect(updatedUser.goldBalance).toBe(bonusGold);
  });

  test('raw dailyStreak = 2 -> bonus uses 2 and updated streak becomes 3', () => {
    const user: any = {
      goldBalance: 500,
      dailyStreak: 2,
      lastLogin: new Date(),
    };

    const { updatedUser, bonusGold } = calculateDailyBonus(user);

    expect(bonusGold).toBe(1000 + 2 * 200);
    expect(updatedUser.dailyStreak).toBe(3);
    expect(updatedUser.goldBalance).toBe(500 + bonusGold);
  });
});
