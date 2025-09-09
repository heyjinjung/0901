'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Play, Coins } from 'lucide-react';
import { Button } from '../ui/button';
import { GameDashboardGame } from '../../types';
import { getDifficultyColor } from '../../utils/gameUtils';

interface GameCardProps {
  game: GameDashboardGame;
  index: number;
  userGoldBalance: number;
  onGameClick: (gameId: string) => void;
}

export function GameCard({ game, index, userGoldBalance, onGameClick }: GameCardProps) {
  const canAfford = userGoldBalance >= game.cost;
  
  // 안전한 값 처리
  const bestScore = game.bestScore || 0;
  const playCount = game.playCount || 0;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{
        delay: 0.3 + index * 0.1,
        duration: 0.5,
        type: 'tween', // spring 대신 tween 사용
      }}
      className={`bg-black/50 backdrop-blur-sm rounded-2xl p-6 relative overflow-hidden border ${
        game.trending ? 'border-purple-400/50' : 'border-purple-500/30'
      } hover:border-purple-400/60 transition-all`}
    >
      {/* 🎯 배지 영역 - animate-pulse 제거 */}
      <div className="absolute top-4 right-4 flex flex-col gap-2">
        {game.trending && (
          <motion.div
            className="bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs px-3 py-1.5 rounded-full font-bold flex items-center gap-1"
            animate={{ scale: [1, 1.05, 1] }}
            transition={{
              duration: 2,
              repeat: Infinity,
              repeatType: 'loop',
              ease: 'easeInOut',
              type: 'tween',
            }}
          >
            🔥 HOT
          </motion.div>
        )}
        <div
          className={`${getDifficultyColor(game.difficulty)} bg-black/50 text-xs px-3 py-1 rounded-full font-medium backdrop-blur-sm`}
        >
          {game.difficulty}
        </div>
      </div>

      {/* 🎮 게임 정보 헤더 */}
      <div className="flex items-center gap-4 mb-6">
        <div
          className={`w-16 h-16 bg-gradient-to-r ${game.color} rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/25`}
        >
          <game.icon className="w-8 h-8 text-white drop-shadow-lg" />
        </div>
        <div className="flex-1">
          <h3 className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
            {game.name}
          </h3>
          <p className="text-sm text-gray-400 leading-relaxed">{game.description}</p>
        </div>
      </div>

      {/* 💎 핵심 정보 1개 - 최고 기록 */}
      <div className="bg-purple-900/30 backdrop-blur-sm rounded-xl p-4 mb-6 text-center border border-purple-500/20">
        <div className="text-2xl font-black text-yellow-400 mb-1">{bestScore.toLocaleString()}</div>
        <div className="text-sm text-gray-400">최고 기록 ({playCount}회 플레이)</div>
      </div>

      {/* 🎯 실행 버튼 */}
      <Button
        onClick={() => onGameClick(game.id)}
        disabled={!canAfford}
        className={`w-full bg-gradient-to-r ${game.color} hover:opacity-90 text-white font-bold py-4 text-lg flex items-center justify-center gap-3 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-purple-500/25 rounded-xl border-0`}
      >
        <Play className="w-6 h-6" />
        {!canAfford ? (
          <span className="flex items-center gap-2">
            <Coins className="w-5 h-5" />
            골드 부족 ({game.cost}G 필요)
          </span>
        ) : (
          <span className="flex items-center gap-2">
            지금 플레이
            <div className="flex items-center gap-1 text-sm opacity-80">
              <Coins className="w-4 h-4" />-{game.cost}G
            </div>
          </span>
        )}
      </Button>
    </motion.div>
  );
}