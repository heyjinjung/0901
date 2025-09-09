'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/unifiedApi';
import useAuthToken from '../../hooks/useAuthToken';
import useFeedback from '../../hooks/useFeedback';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Coins, RefreshCw, Package, Heart, Crown } from 'lucide-react';
import { User } from '../../types'; // App.tsx가 아닌 types에서 import
import { GachaItem } from '../../types/gacha';
import { Button } from '../ui/button';
import { useGameConfig } from '../../hooks/useGameConfig';
import { GACHA_BANNERS, ANIMATION_DURATIONS } from './gacha/constants';
import {
  generateParticles,
  generateHeartParticles,
  getRandomItem,
  updateUserInventory,
  getRarityMessage,
  getTenPullMessage,
  Particle,
  HeartParticle,
} from './gacha/utils';
import {
  SexyBannerSelector,
  SexyPullResultsModal,
  SexyInventoryModal,
  BackgroundEffects, // BackgroundEffects 컴포넌트 추가
} from './gacha/components';
import type { GachaBanner } from '../../types/gacha';

interface GachaSystemProps {
  user: User;
  onBack: () => void;
  onUpdateUser: (user: User) => void;
  onAddNotification: (message: string) => void;
}

interface GachaPullApiResponse {
  success?: boolean;
  items: Array<{ name: string; rarity: string }>;
  rare_item_count?: number;
  ultra_rare_item_count?: number;
  pull_count?: number;
  balance?: number; // token balance
  animation_type?: string;
  special_animation?: string | null;
  psychological_message?: string;
  message?: string;
  feedback?: any; // fed into fromApi
  currency_balance?: { tokens?: number };
}

export function GachaSystem({ user, onBack, onUpdateUser, onAddNotification }: GachaSystemProps) {
  const { fromApi } = useFeedback();
  const { getAccessToken } = useAuthToken();
  const { config: gameConfig, loading: configLoading } = useGameConfig();
  
  const [selectedBanner, setSelectedBanner] = useState(GACHA_BANNERS[0] as GachaBanner);
  const [isPulling, setIsPulling] = useState(false);
  const [pullResults, setPullResults] = useState([] as GachaItem[]);
  const [showResults, setShowResults] = useState(false);
  const [particles, setParticles] = useState([] as Particle[]);
  const [currentPullIndex, setCurrentPullIndex] = useState(0);
  const [showInventory, setShowInventory] = useState(false);
  const [pullAnimation, setPullAnimation] = useState(null as 'opening' | 'revealing' | null);
  const [heartParticles, setHeartParticles] = useState(
    [] as Array<{ id: string; x: number; y: number }>
  );

  // 동적 가챠 비용 계산 (서버 설정 우선, fallback으로 배너 기본값)
  const getSinglePullCost = () => {
    return gameConfig.gacha?.cost_single ?? selectedBanner.cost;
  };
  
  const getTenPullCost = () => {
    return gameConfig.gacha?.cost_ten ?? Math.floor(getSinglePullCost() * 10 * 0.9);
  };

  // Clear particles after animation
  useEffect(() => {
    if (particles.length > 0) {
      const timer = setTimeout(() => setParticles([]), ANIMATION_DURATIONS.sparkle || 2000);
      return () => clearTimeout(timer);
    }
  }, [particles]);

  // Generate heart particles for ambient effect
  useEffect(() => {
    const generateHearts = () => {
      const newHearts = generateHeartParticles();
      setHeartParticles((prev: any[]) => [...prev.slice(-10), ...newHearts]);
    };

    const interval = setInterval(generateHearts, 3000);
    return () => clearInterval(interval);
  }, []);

  // 컴포넌트 마운트 시 실행되는 초기화 함수
  useEffect(() => {
    // User 객체의 gameStats.gacha 초기화
    if (
      !user.gameStats.gacha ||
      user.gameStats.gacha.pulls === undefined ||
      user.gameStats.gacha.totalSpent === undefined ||
      user.gameStats.gacha.epicCount === undefined ||
      user.gameStats.gacha.legendaryCount === undefined
    ) {
      onUpdateUser({
        ...user,
        gameStats: {
          ...user.gameStats,
          gacha: {
            totalPulls: user.gameStats.gacha?.totalPulls || 0,
            legendaryPulls: user.gameStats.gacha?.legendaryPulls || 0,
            totalValue: user.gameStats.gacha?.totalValue || 0,
            // 누락된 필드 초기화
            pulls: [],
            totalSpent: 0,
            epicCount: 0,
            legendaryCount: 0,
          },
        },
      });
    }
  }, []);

  // Perform single pull
  const performSinglePull = async () => {
    const cost = getSinglePullCost();
    if (user.goldBalance < cost) {
      onAddNotification('❌ 골드가 부족합니다!');
      return;
    }
    setIsPulling(true);
    setPullAnimation('opening');
    await new Promise((r) => setTimeout(r, ANIMATION_DURATIONS.fadeIn));
    setPullAnimation('revealing');
    let serverUsed = false;
    try {
      // Auth token retrieval (temporary: reading localStorage like slot game)
  const res = await api.post<GachaPullApiResponse>('games/gacha/pull', { pull_count: 1 });
      fromApi(res);
      if (res?.items?.length) {
        serverUsed = true;
        const mapped: GachaItem[] = res.items.map(
          (it, idx) =>
            ({
              id: `srv-${Date.now()}-${idx}`,
              name: it.name,
              // fallback values for fields expected by UI logic
              type: 'item',
              rarity: (it.rarity as any) || 'common',
              rate: 0,
              quantity: 1,
              value: 0,
            }) as unknown as GachaItem
        );
        setPullResults(mapped);
        setCurrentPullIndex(0);
        setShowResults(true);
        // Update user from authoritative balance & stats
        const newBalance = res.balance ?? res.currency_balance?.tokens;
        const first = mapped[0];
        const updatedUser = updateUserInventory(
          {
            ...user,
            goldBalance:
              typeof newBalance === 'number' ? newBalance : user.goldBalance - cost,
            gameStats: {
              ...user.gameStats,
              gacha: {
                ...user.gameStats.gacha,
                pulls: user.gameStats.gacha.pulls + 1,
                totalSpent: user.gameStats.gacha.totalSpent + cost,
                epicCount:
                  (user.gameStats.gacha.epicCount || 0) + (first.rarity === 'epic' ? 1 : 0),
                legendaryCount:
                  (user.gameStats.gacha.legendaryCount || 0) +
                  (['legendary', 'mythic'].includes(first.rarity) ? 1 : 0),
              },
            },
          } as User,
          first
        );
        onUpdateUser(updatedUser as User);
        onAddNotification(getRarityMessage(first));
      }
    } catch (e) {
      // Fallback to local simulation
    }
    if (!serverUsed) {
      // Local fallback logic replicating previous behavior
      let updatedUser = {
        ...user,
        goldBalance: user.goldBalance - cost,
        gameStats: {
          ...user.gameStats,
          gacha: {
            ...user.gameStats.gacha,
            pulls: user.gameStats.gacha.pulls + 1,
            totalSpent: user.gameStats.gacha.totalSpent + cost,
          },
        },
      };
      const item = getRandomItem(selectedBanner, updatedUser);
      const newParticles = generateParticles(item.rarity);
      setParticles(newParticles);
      updatedUser = updateUserInventory(updatedUser as unknown as User, item);
      if (item.rarity === 'epic') {
        updatedUser.gameStats.gacha.epicCount = (updatedUser.gameStats.gacha.epicCount || 0) + 1;
      } else if (item.rarity === 'legendary' || item.rarity === 'mythic') {
        updatedUser.gameStats.gacha.legendaryCount =
          (updatedUser.gameStats.gacha.legendaryCount || 0) + 1;
      }
      setPullResults([item]);
      setCurrentPullIndex(0);
      setShowResults(true);
      onUpdateUser(updatedUser as User);
      onAddNotification(getRarityMessage(item));
    }
    setIsPulling(false);
    setPullAnimation(null);
  };

  // Perform 10-pull
  const performTenPull = async () => {
    const discountedCost = getTenPullCost();
    if (user.goldBalance < discountedCost) {
      onAddNotification('❌ 골드가 부족합니다!');
      return;
    }
    setIsPulling(true);
    setPullAnimation('opening');
    await new Promise((r) => setTimeout(r, ANIMATION_DURATIONS.fadeIn + 500));
    setPullAnimation('revealing');
    let serverUsed = false;
    try {
  const res = await api.post<GachaPullApiResponse>('games/gacha/pull', { pull_count: 10 });
      fromApi(res);
      if (res?.items?.length) {
        serverUsed = true;
        const mapped: GachaItem[] = res.items.map(
          (it, idx) =>
            ({
              id: `srv-${Date.now()}-${idx}`,
              name: it.name,
              type: 'item',
              rarity: (it.rarity as any) || 'common',
              rate: 0,
              quantity: 1,
              value: 0,
            }) as unknown as GachaItem
        );
        setPullResults(mapped);
        setCurrentPullIndex(0);
        setShowResults(true);
        // Determine best item for particle effect
        const rarityOrder: Record<string, number> = {
          common: 1,
          rare: 2,
          epic: 3,
          legendary: 4,
          mythic: 5,
        };
        const bestItem = mapped.reduce(
          (b, c) => (rarityOrder[c.rarity] > rarityOrder[b.rarity] ? c : b),
          mapped[0]
        );
        setParticles(generateParticles(bestItem.rarity));
        const ultraAdds = mapped.filter((i) => ['legendary', 'mythic'].includes(i.rarity)).length;
        const epicAdds = mapped.filter((i) => i.rarity === 'epic').length;
        const newBalance = res.balance ?? res.currency_balance?.tokens;
        const updatedUser = mapped.reduce(
          (acc, item) => updateUserInventory(acc as User, item) as User,
          {
            ...user,
            goldBalance:
              typeof newBalance === 'number' ? newBalance : user.goldBalance - discountedCost,
            gameStats: {
              ...user.gameStats,
              gacha: {
                ...user.gameStats.gacha,
                pulls: user.gameStats.gacha.pulls + 10,
                totalSpent: user.gameStats.gacha.totalSpent + discountedCost,
                epicCount: (user.gameStats.gacha.epicCount || 0) + epicAdds,
                legendaryCount: (user.gameStats.gacha.legendaryCount || 0) + ultraAdds,
              },
            },
          } as User
        );
        onUpdateUser(updatedUser as User);
        onAddNotification(getTenPullMessage(mapped));
      }
    } catch (e) {
      // swallow & fallback
    }
    if (!serverUsed) {
      const items: GachaItem[] = [];
      let updatedUser = {
        ...user,
        goldBalance: user.goldBalance - discountedCost,
        gameStats: {
          ...user.gameStats,
          gacha: {
            ...user.gameStats.gacha,
            pulls: user.gameStats.gacha.pulls + 10,
            totalSpent: user.gameStats.gacha.totalSpent + discountedCost,
          },
        },
      };
      for (let i = 0; i < 10; i++) {
        const item = getRandomItem(selectedBanner, updatedUser);
        items.push(item);
        updatedUser = updateUserInventory(updatedUser as unknown as User, item);
        if (item.rarity === 'epic') {
          updatedUser.gameStats.gacha.epicCount = (updatedUser.gameStats.gacha.epicCount || 0) + 1;
        } else if (['legendary', 'mythic'].includes(item.rarity)) {
          updatedUser.gameStats.gacha.legendaryCount =
            (updatedUser.gameStats.gacha.legendaryCount || 0) + 1;
        }
      }
      const rarityOrder: Record<string, number> = {
        common: 1,
        rare: 2,
        epic: 3,
        legendary: 4,
        mythic: 5,
      };
      const bestItem = items.reduce((b, c) =>
        rarityOrder[c.rarity] > rarityOrder[b.rarity] ? c : b
      );
      setParticles(generateParticles(bestItem.rarity));
      setPullResults(items);
      setCurrentPullIndex(0);
      setShowResults(true);
      onUpdateUser(updatedUser as User);
      onAddNotification(getTenPullMessage(items));
    }
    setIsPulling(false);
    setPullAnimation(null);
  };

  // Navigate to next result
  const handleNextResult = () => {
    if (currentPullIndex < pullResults.length - 1) {
      setCurrentPullIndex((prev: number) => prev + 1);
    }
  };

  // Close results modal
  const handleCloseResults = () => {
    setShowResults(false);
    setPullResults([]);
    setCurrentPullIndex(0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-pink-900/20 to-purple-900/30 relative overflow-hidden">
      {/* Floating Heart Particles */}
      <AnimatePresence mode="wait">
        {heartParticles.map((heart: any) => (
          <motion.div
            key={heart.id} // 이미 고유 ID 사용 중
            initial={{
              opacity: 0,
              scale: 0,
              x: `${heart.x}vw`,
              y: `${heart.y}vh`,
            }}
            animate={{
              opacity: [0, 0.6, 0],
              scale: [0, 1, 0],
              y: `${heart.y - 50}vh`,
              rotate: [0, 360],
            }}
            exit={{ opacity: 0 }}
            transition={{ duration: ANIMATION_DURATIONS.pulse, ease: 'easeOut' }}
            className="fixed text-pink-400 text-2xl pointer-events-none z-20"
          >
            💖
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Particle Effects */}
      <AnimatePresence>
        {particles.map((particle: any) => (
          <motion.div
            key={particle.id}
            initial={{
              opacity: 0,
              scale: 0,
              x: `${particle.x}vw`,
              y: `${particle.y}vh`,
            }}
            animate={{
              opacity: [0, 1, 0],
              scale: [0, 1.5, 0],
              y: `${particle.y - 30}vh`,
              rotate: 360,
            }}
            exit={{ opacity: 0 }}
            transition={{ duration: ANIMATION_DURATIONS.sparkle, ease: 'easeOut' }}
            className="fixed rounded-full pointer-events-none z-30"
            style={{
              backgroundColor: particle.color,
              width: particle.size,
              height: particle.size,
            }}
          />
        ))}
      </AnimatePresence>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 p-4 lg:p-6 border-b border-pink-500/30 backdrop-blur-sm bg-black/20"
      >
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={onBack}
              className="border-pink-500/50 hover:border-pink-400 text-pink-300 hover:text-pink-200"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              뒤로가기
            </Button>

            <div>
              <motion.h1
                animate={{
                  textShadow: [
                    '0 0 20px rgba(236, 72, 153, 0.5)',
                    '0 0 30px rgba(236, 72, 153, 0.8)',
                    '0 0 20px rgba(236, 72, 153, 0.5)',
                  ],
                }}
                transition={{ duration: 2, repeat: Infinity }}
                className="text-xl lg:text-2xl font-black text-transparent bg-gradient-to-r from-pink-400 via-purple-400 to-pink-400 bg-clip-text"
              >
                가챠
              </motion.h1>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={() => setShowInventory(true)}
              className="border-pink-500/50 hover:border-pink-400 text-pink-300 hover:text-pink-200"
            >
              <Package className="w-4 h-4 mr-2" />
              컬렉션
            </Button>

            <div className="text-right">
              <div className="text-sm text-pink-300/60">보유 골드</div>
              <div className="text-xl font-bold text-yellow-400">
                {user.goldBalance.toLocaleString()}G
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="relative z-10 p-4 lg:p-6 max-w-6xl mx-auto">
        {/* Game Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6"
        >
          <div className="glass-effect rounded-xl p-4 text-center bg-pink-900/20 border-pink-500/30">
            <div className="text-xl font-bold text-pink-300">{user.gameStats.gacha.pulls}</div>
            <div className="text-sm text-pink-400/60">총 뽑기</div>
          </div>
          <div className="glass-effect rounded-xl p-4 text-center bg-purple-900/20 border-purple-500/30">
            <div className="text-xl font-bold text-purple-300">
              {user.gameStats.gacha.epicCount}
            </div>
            <div className="text-sm text-purple-400/60">에픽 획득</div>
          </div>
          <div className="glass-effect rounded-xl p-4 text-center bg-yellow-900/20 border-yellow-500/30">
            <div className="text-xl font-bold text-yellow-300">
              {user.gameStats.gacha.legendaryCount}
            </div>
            <div className="text-sm text-yellow-400/60">레전더리+</div>
          </div>
          <div className="glass-effect rounded-xl p-4 text-center bg-red-900/20 border-red-500/30">
            <div className="text-xl font-bold text-red-300">
              {user?.gameStats?.gacha?.totalSpent?.toLocaleString() || '0'}G
            </div>
            <div className="text-sm text-red-400/60">총 소모</div>
          </div>
        </motion.div>

        {/* Banner Selection */}
        <SexyBannerSelector
          banners={GACHA_BANNERS}
          selectedBanner={selectedBanner}
          onSelectBanner={setSelectedBanner}
          isPulling={isPulling}
        />

        {/* Gacha Machine */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="glass-effect rounded-3xl p-8 mb-6 relative overflow-hidden bg-gradient-to-br from-pink-900/20 to-purple-900/20 border-pink-500/30"
        >
          {/* Machine Animation Overlay */}
          <AnimatePresence>
            {pullAnimation && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="absolute inset-0 bg-black/70 flex items-center justify-center z-20 rounded-3xl"
              >
                <motion.div
                  animate={
                    pullAnimation === 'opening'
                      ? {
                          scale: [1, 1.5, 1],
                          rotate: [0, 360],
                          filter: ['hue-rotate(0deg)', 'hue-rotate(360deg)'],
                        }
                      : {
                          scale: [1, 2, 1],
                          opacity: [0.5, 1, 0.5],
                          textShadow: [
                            '0 0 20px rgba(236, 72, 153, 0.5)',
                            '0 0 40px rgba(236, 72, 153, 1)',
                            '0 0 20px rgba(236, 72, 153, 0.5)',
                          ],
                        }
                  }
                  transition={{ duration: pullAnimation === 'opening' ? 2 : 1, repeat: Infinity }}
                  className="text-8xl"
                >
                  {pullAnimation === 'opening' ? '🎁' : '✨'}
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Sexy Background Elements */}
          <BackgroundEffects />

          <div className="text-center relative z-10">
            <motion.div
              animate={{
                scale: [1, 1.1, 1],
                rotate: [0, 5, -5, 0],
                textShadow: [
                  '0 0 20px rgba(236, 72, 153, 0.5)',
                  '0 0 30px rgba(236, 72, 153, 0.8)',
                  '0 0 20px rgba(236, 72, 153, 0.5)',
                ],
              }}
              transition={{ duration: 3, repeat: Infinity }}
              className="text-8xl mb-6"
            >
              🎰
            </motion.div>

            <motion.h2
              className="text-3xl font-black text-transparent bg-gradient-to-r from-pink-400 to-purple-400 bg-clip-text mb-4"
              animate={{
                backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
              }}
              transition={{ duration: 3, repeat: Infinity }}
            >
              {selectedBanner.name}
            </motion.h2>

            <p className="text-pink-300/80 mb-8 text-lg">{selectedBanner.description}</p>

            {/* Pull Buttons */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-lg mx-auto">
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  onClick={performSinglePull}
                  disabled={isPulling || user.goldBalance < getSinglePullCost()}
                  className="w-full h-20 bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-400 hover:to-purple-400 text-white font-bold text-lg relative overflow-hidden border-0"
                  style={{ boxShadow: '0 0 20px rgba(236, 72, 153, 0.5)' }}
                >
                  {isPulling ? (
                    <>
                      <RefreshCw className="w-6 h-6 mr-2 animate-spin" />
                      뽑는 중...
                    </>
                  ) : (
                    <>
                      <Heart className="w-6 h-6 mr-2" />
                      <div className="flex flex-col">
                        <span>섹시 단발 뽑기</span>
                        <span className="text-sm opacity-80">{getSinglePullCost()}G</span>
                      </div>
                    </>
                  )}

                  <motion.div
                    animate={{
                      x: ['100%', '-100%'],
                      opacity: [0, 1, 0],
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                  />
                </Button>
              </motion.div>

              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  onClick={performTenPull}
                  disabled={isPulling || user.goldBalance < getTenPullCost()}
                  className="w-full h-20 bg-gradient-to-r from-yellow-500 to-red-500 hover:from-yellow-400 hover:to-red-400 text-white font-bold text-lg relative overflow-hidden border-0"
                  style={{ boxShadow: '0 0 20px rgba(245, 158, 11, 0.5)' }}
                >
                  {isPulling ? (
                    <>
                      <RefreshCw className="w-6 h-6 mr-2 animate-spin" />
                      뽑는 중...
                    </>
                  ) : (
                    <>
                      <Crown className="w-6 h-6 mr-2" />
                      <div className="flex flex-col">
                        <span>글래머 10연 뽑기</span>
                        <span className="text-sm opacity-80">
                          {getTenPullCost()}G (10% 할인!)
                        </span>
                      </div>
                    </>
                  )}

                  <motion.div
                    animate={{
                      x: ['100%', '-100%'],
                      opacity: [0, 1, 0],
                    }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                  />
                </Button>
              </motion.div>
            </div>

            {/* 🔧 Sexiness Level Display - 고유 키 수정 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
              className="mt-8 p-4 bg-black/30 rounded-xl border border-pink-500/30"
            >
              <div className="text-pink-300 text-sm mb-2">💕 SEXINESS LEVEL 💕</div>
              <div className="flex justify-center gap-1">
                {[1, 2, 3, 4, 5].map((level) => (
                  <motion.div
                    key={`sexiness-level-${level}`} // Date.now() 제거
                    animate={{
                      scale: [1, 1.2, 1],
                      opacity: [0.5, 1, 0.5],
                    }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      delay: level * 0.1,
                    }}
                    className="text-2xl"
                  >
                    💖
                  </motion.div>
                ))}
              </div>
              <div className="text-xs text-pink-400/60 mt-1">더 섹시할수록 더 레어한 아이템!</div>
            </motion.div>
          </div>
        </motion.div>
      </div>

      {/* Modals */}
      <AnimatePresence mode="wait">
        {showResults && (
          <SexyPullResultsModal
            results={pullResults}
            showResults={showResults}
            currentIndex={currentPullIndex}
            onNext={handleNextResult}
            onClose={handleCloseResults}
          />
        )}

        {showInventory && (
          <SexyInventoryModal
            isOpen={showInventory}
            inventory={user.inventory as unknown as GachaItem[]}
            onClose={() => setShowInventory(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

export interface GachaStats {
  totalPulls: number;
  legendaryPulls: number;
  totalValue: number;
  pulls: number[];
  totalSpent: number;
  epicCount: number;
  legendaryCount: number;
}

export type GachaRarity = "common" | "rare" | "epic" | "legendary" | "mythic";