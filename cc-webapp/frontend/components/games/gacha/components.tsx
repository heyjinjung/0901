import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Heart, Crown, Package } from 'lucide-react';
import { User } from '../../../types';
import { Button } from '../../ui/button';
import { GachaBanner, GachaItem, HeartParticle } from '../../../types/gacha';
import {
  generateSparkles,
  getAnimationDelay,
  getBannerStyle,
  generateHeartParticles,
} from './utils';
import { SEXY_EMOJIS, RARITY_COLORS } from './constants';

// 배너 선택 컴포넌트
export function SexyBannerSelector({
  banners,
  onSelectBanner,
  selectedBanner,
  isPulling,
}: {
  banners: GachaBanner[];
  onSelectBanner: (banner: GachaBanner) => void;
  selectedBanner: GachaBanner;
  isPulling?: boolean;
}) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
      {banners.map((banner, index) => {
        const sparkles = generateSparkles();
        const isSelected = selectedBanner.id === banner.id;

        return (
          <motion.div
            key={banner.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: getAnimationDelay(index, 0.3) }}
            whileHover={{ scale: 1.02, rotateY: 5 }}
            onClick={() => onSelectBanner(banner)}
            className="relative rounded-xl p-6 cursor-pointer transition-all overflow-hidden"
            style={getBannerStyle(banner, isSelected)}
          >
            <div
              className={`absolute inset-0 ${RARITY_COLORS[(banner.guaranteedRarity as keyof typeof RARITY_COLORS) ? (banner.guaranteedRarity as keyof typeof RARITY_COLORS) : 'common']}40 opacity-20`}
            />

            {isSelected && (
              <div className="absolute inset-0 bg-gradient-to-br from-pink-500/20 to-purple-500/20 animate-pulse" />
            )}

            {/* 배너 내용 */}
            <div className="relative z-10">
              <h3 className="text-xl font-bold text-white mb-1">{banner.name}</h3>
              <p className="text-sm text-pink-100 mb-3">{banner.description}</p>
              <div className="flex items-center">
                <span className="text-yellow-300 font-bold">{banner.cost} G</span>
              </div>
            </div>

            {/* 반짝이 효과 */}
            {sparkles.map((sparkle) => (
              <motion.div
                key={sparkle.id}
                className="absolute text-white pointer-events-none"
                style={{
                  left: sparkle.left,
                  top: sparkle.top,
                  fontSize: `${sparkle.size}px`,
                  animationDelay: sparkle.animationDelay,
                }}
                animate={{
                  opacity: [0, 1, 0],
                  scale: [0.5, 1.2, 0.5],
                }}
                transition={{
                  repeat: Infinity,
                  duration: 2,
                  ease: 'easeInOut',
                }}
              >
                {sparkle.emoji}
              </motion.div>
            ))}
          </motion.div>
        );
      })}
    </div>
  );
}

// 아이템 카드 컴포넌트
export function SexyItemCard({
  item,
  isNew = false,
  animate = false,
  showDetails = false,
  onClick,
}: {
  item: GachaItem;
  isNew?: boolean;
  animate?: boolean;
  showDetails?: boolean;
  onClick?: () => void;
}) {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <motion.div
      whileHover={{ scale: 1.05, y: -5 }}
      onClick={onClick}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className={`relative rounded-lg p-4 bg-gradient-to-br ${RARITY_COLORS[item.rarity as keyof typeof RARITY_COLORS]}20 to-transparent border border-${RARITY_COLORS[item.rarity as keyof typeof RARITY_COLORS]}40 cursor-pointer overflow-hidden`}
    >
      {isNew && (
        <div className="absolute top-2 right-2 z-10">
          <div className="bg-pink-500 text-xs text-white font-bold px-2 py-1 rounded-full animate-pulse">
            NEW
          </div>
        </div>
      )}

      <div className="flex items-center justify-center mb-3 h-16">
        <motion.div
          animate={
            animate
              ? {
                  scale: [1, 1.2, 1],
                  rotate: [0, 10, -10, 0],
                }
              : {}
          }
          transition={{ duration: 0.8, repeat: animate ? Infinity : 0, repeatDelay: 1 }}
          className="text-4xl"
        >
          {item.icon}
        </motion.div>
      </div>

      <h3 className="text-center font-bold mb-1 text-white">{item.name}</h3>

      <p
        className={`text-xs text-center text-${RARITY_COLORS[item.rarity as keyof typeof RARITY_COLORS]}`}
      >
        {item.rarity.toUpperCase()} 등급
      </p>

      {showDetails && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: isHovered ? 1 : 0, height: isHovered ? 'auto' : 0 }}
          className="mt-2 text-xs text-gray-300"
        >
          <p>{item.description}</p>
          <div className="mt-1 flex justify-between">
            <span>가치: {item.value} G</span>
            <div className="flex">
              {Array(item.sexiness || 1)
                .fill(0)
                .map((_, i) => (
                  <Heart key={i} size={10} className="text-pink-400" />
                ))}
            </div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

// 결과 표시 컴포넌트
export function SexyResultOverlay({
  isVisible,
  item,
  onClose,
  onContinue,
  isTenPull = false,
  items = [],
}: {
  isVisible: boolean;
  item?: GachaItem;
  onClose?: () => void;
  onContinue?: () => void;
  isTenPull?: boolean;
  items?: GachaItem[];
}) {
  const [hearts, setHearts] = useState([] as HeartParticle[]);

  React.useEffect(() => {
    if (isVisible) {
      setHearts(generateHeartParticles());
    }
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center"
    >
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', bounce: 0.4 }}
        className="relative bg-gradient-to-br from-pink-900/60 to-purple-900/60 rounded-2xl p-8 max-w-md w-full text-center"
      >
        {isTenPull ? (
          <>
            <h2 className="text-2xl font-bold text-pink-300 mb-6">10연 가챠 결과</h2>
            <div className="grid grid-cols-5 gap-2 mb-6">
              {items.map((item, index) => (
                <motion.div
                  key={`${item.id}_${index}`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: getAnimationDelay(index, 0.1) }}
                >
                  <SexyItemCard item={item} isNew={item.isNew} />
                </motion.div>
              ))}
            </div>
          </>
        ) : item ? (
          <>
            <motion.div
              animate={{
                scale: [1, 1.05, 1],
                rotate: [0, 1, -1, 0],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatType: 'reverse',
              }}
              className="mb-4"
            >
              {item.rarity === 'legendary' && (
                <Crown className="mx-auto text-yellow-300 animate-pulse" size={40} />
              )}
            </motion.div>

            <motion.div initial={{ y: 20 }} animate={{ y: 0 }} className="mb-6">
              <SexyItemCard item={item} animate isNew={item.isNew} showDetails />
            </motion.div>

            <motion.h2
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className={`text-xl font-bold text-${RARITY_COLORS[item.rarity as keyof typeof RARITY_COLORS]} mb-2`}
            >
              {item.rarity === 'common'
                ? '아이템 획득!'
                : item.rarity === 'rare'
                  ? '레어 아이템 획득!'
                  : item.rarity === 'epic'
                    ? '에픽 아이템 획득!'
                    : item.rarity === 'legendary'
                      ? '레전더리 아이템 획득!'
                      : '미식 아이템 획득!'}
            </motion.h2>
          </>
        ) : null}

        {/* 심장 파티클 */}
            {hearts.map((heart: HeartParticle) => (
          <motion.div
            key={heart.id}
            initial={{ x: heart.x + '%', y: heart.y + '%', opacity: 0 }}
            animate={{
              y: [heart.y + '%', heart.y - 20 + '%'],
              opacity: [0, 1, 0],
            }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute text-pink-500"
          >
            ❤️
          </motion.div>
        ))}

        <div className="flex justify-center gap-3 mt-6">
          {onContinue && (
            <Button
              onClick={onContinue}
              variant="default"
              className="bg-gradient-to-r from-pink-500 to-pink-700 hover:from-pink-600 hover:to-pink-800 text-white"
            >
              계속 뽑기
            </Button>
          )}

          {onClose && (
            <Button
              onClick={onClose}
              variant="outline"
              className="border-pink-500 text-pink-500 hover:bg-pink-500/20"
            >
              닫기
            </Button>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}

// 이모지 반짝임 효과
export function SexyEmojis() {
  const sexyEmojis = SEXY_EMOJIS;

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {sexyEmojis.map((emoji, index) => (
        <motion.div
          key={`emoji_${index}`}
          initial={{
            opacity: 0,
            x: Math.random() * 100 + '%',
            y: Math.random() * 100 + '%',
            scale: 0.5,
          }}
          animate={{
            opacity: [0, 1, 0],
            scale: [0.5, 1, 0.5],
            x: Math.random() * 100 + '%',
            y: Math.random() * 100 + '%',
          }}
          transition={{
            duration: 3 + Math.random() * 2,
            delay: index * 0.5,
            repeat: Infinity,
            repeatDelay: Math.random() * 5,
          }}
          className="absolute text-2xl"
        >
          {emoji}
        </motion.div>
      ))}
    </div>
  );
}

// 배경 효과 컴포넌트
export function BackgroundEffects() {
  return (
    <div className="fixed inset-0 pointer-events-none z-0">
      {/* 네온 그리드 배경 */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-pink-900/20 to-blue-900/20" />

      {/* 반짝이는 점들 */}
      <div className="absolute inset-0">
        {Array.from({ length: 20 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-cyan-400 rounded-full"
            style={{
              left: Math.random() * 100 + '%',
              top: Math.random() * 100 + '%',
            }}
            animate={{
              opacity: [0, 1, 0],
              scale: [0.5, 1.5, 0.5],
            }}
            transition={{
              duration: 2 + Math.random() * 3,
              repeat: Infinity,
              delay: Math.random() * 5,
            }}
          />
        ))}
      </div>

      {/* 떠다니는 파티클 */}
      <div className="absolute inset-0">
        {Array.from({ length: 10 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 border border-pink-400/30 rounded-full"
            style={{
              left: Math.random() * 100 + '%',
              top: Math.random() * 100 + '%',
            }}
            animate={{
              y: [0, -100, 0],
              x: [0, Math.random() * 50 - 25, 0],
              opacity: [0, 0.5, 0],
            }}
            transition={{
              duration: 8 + Math.random() * 4,
              repeat: Infinity,
              delay: Math.random() * 8,
            }}
          />
        ))}
      </div>
    </div>
  );
}

// 뽑기 결과 모달 컴포넌트
export function SexyPullResultsModal({
  results,
  showResults,
  currentIndex,
  onNext,
  onClose,
}: {
  results: GachaItem[];
  showResults: boolean;
  currentIndex: number;
  onNext: () => void;
  onClose: () => void;
}) {
  if (!showResults) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="bg-gradient-to-br from-gray-900 to-purple-900 rounded-2xl p-8 max-w-4xl max-h-[80vh] overflow-y-auto border-2 border-pink-500/30"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          onClick={(e: any) => e.stopPropagation()}
        >
          <div className="text-center mb-6">
            <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-purple-400 mb-2">
              🎉 뽑기 결과 🎉
            </h2>
            <p className="text-gray-300">총 {results.length}개 아이템 획득!</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {results.map((item, index) => (
              <motion.div
                key={index}
                className={`relative p-4 rounded-xl border-2 ${
                  RARITY_COLORS[item.rarity as keyof typeof RARITY_COLORS] || 'border-gray-600'
                }`}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.05 }}
              >
                <div className="text-center">
                  <div className="text-2xl mb-2">{item.icon}</div>
                  <h3 className="text-sm font-semibold text-white mb-1">{item.name}</h3>
                  <p className="text-xs text-gray-400 capitalize">{item.rarity}</p>
                </div>

                {item.rarity === 'legendary' && (
                  <div className="absolute -top-2 -right-2">
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                    >
                      <Crown className="w-6 h-6 text-yellow-400" />
                    </motion.div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>

          <div className="mt-8 text-center">
            <Button
              onClick={onClose}
              className="bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600 text-white px-8 py-3 rounded-xl"
            >
              확인
            </Button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

// 인벤토리 모달 컴포넌트
export function SexyInventoryModal({
  isOpen,
  onClose,
  inventory,
}: {
  isOpen: boolean;
  onClose: () => void;
  inventory: GachaItem[];
}) {
  if (!isOpen) return null;

  const groupedInventory = inventory.reduce(
    (acc, item) => {
      const key = `${item.name}-${item.rarity}`;
      if (!acc[key]) {
        acc[key] = { ...item, count: 0 };
      }
      acc[key].count += 1;
      return acc;
    },
    {} as Record<string, GachaItem & { count: number }>
  );

  const inventoryItems = Object.values(groupedInventory);

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onClose}
      >
        <motion.div
          className="bg-gradient-to-br from-gray-900 to-blue-900 rounded-2xl p-8 max-w-4xl max-h-[80vh] overflow-y-auto border-2 border-cyan-500/30"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.8, opacity: 0 }}
          onClick={(e: any) => e.stopPropagation()}
        >
          <div className="text-center mb-6">
            <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-400 mb-2">
              📦 인벤토리 📦
            </h2>
            <p className="text-gray-300">보유 아이템: {inventoryItems.length}종류</p>
          </div>

          {inventoryItems.length === 0 ? (
            <div className="text-center py-12">
              <Package className="w-16 h-16 text-gray-500 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">아직 보유한 아이템이 없습니다.</p>
              <p className="text-gray-500 text-sm mt-2">가챠를 뽑아보세요!</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {inventoryItems.map((item, index) => (
                <motion.div
                  key={index}
                  className={`relative p-4 rounded-xl border-2 ${
                    RARITY_COLORS[item.rarity as keyof typeof RARITY_COLORS] || 'border-gray-600'
                  }`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  whileHover={{ scale: 1.05 }}
                >
                  <div className="text-center">
                    <div className="text-2xl mb-2">{item.icon}</div>
                    <h3 className="text-sm font-semibold text-white mb-1">{item.name}</h3>
                    <p className="text-xs text-gray-400 capitalize">{item.rarity}</p>
                    <div className="mt-2 bg-gray-700/50 rounded-full px-2 py-1">
                      <span className="text-xs text-cyan-400">x{item.count}</span>
                    </div>
                  </div>

                  {item.rarity === 'legendary' && (
                    <div className="absolute -top-2 -right-2">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                      >
                        <Crown className="w-6 h-6 text-yellow-400" />
                      </motion.div>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          )}

          <div className="mt-8 text-center">
            <Button
              onClick={onClose}
              className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white px-8 py-3 rounded-xl"
            >
              닫기
            </Button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
