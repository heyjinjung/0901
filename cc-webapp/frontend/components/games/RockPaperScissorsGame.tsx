'use client';

import React, { useState } from 'react';
import { api } from '@/lib/unifiedApi';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft,
  Coins,
  Trophy,
  Timer,
  RotateCcw,
  Volume2,
  VolumeX,
  Flame,
  Crown,
  Sparkles,
} from 'lucide-react';
import { User } from '../../types';
import { Button } from '../ui/button';
import { useWithReconcile } from '@/lib/sync';
import { useGlobalSync } from '@/hooks/useGlobalSync';
import { useGlobalStore, useGlobalProfile } from '@/store/globalStore';
import { mergeGameStats } from '@/store/globalStore';
import { useGameTileStats } from '@/hooks/useGameStats';

interface RockPaperScissorsGameProps {
  user: User;
  onBack: () => void;
  onUpdateUser: (user: User) => void;
  onAddNotification: (message: string) => void;
}

type Choice = 'rock' | 'paper' | 'scissors';
type GameResult = 'win' | 'lose' | 'draw';

interface GameRound {
  playerChoice: Choice;
  aiChoice: Choice;
  result: GameResult;
  winnings: number;
  isSpecialMove: boolean;
}

interface SoundEffect {
  name: string;
  duration: number;
  visual: string;
}

const CHOICES = {
  rock: { emoji: '✊', name: '바위', beats: 'scissors', color: 'text-orange-400' },
  paper: { emoji: '✋', name: '보', beats: 'rock', color: 'text-blue-400' },
  scissors: { emoji: '✌️', name: '가위', beats: 'paper', color: 'text-red-400' },
};

const SOUND_EFFECTS: Record<string, SoundEffect> = {
  countdown: { name: '카운트다운', duration: 800, visual: '⏰' },
  playerAttack: { name: '플레이어 공격', duration: 500, visual: '💥' },
  aiAttack: { name: 'AI 공격', duration: 500, visual: '⚡' },
  clash: { name: '충돌', duration: 300, visual: '💢' },
  victory: { name: '승리', duration: 1000, visual: '🎉' },
  defeat: { name: '패배', duration: 800, visual: '😵' },
  draw: { name: '무승부', duration: 600, visual: '🤝' },
  combo: { name: '콤보', duration: 1200, visual: '🔥' },
  perfect: { name: '퍼펙트', duration: 1500, visual: '⭐' },
};

export function RockPaperScissorsGame({
  user,
  onBack,
  onUpdateUser,
  onAddNotification,
}: RockPaperScissorsGameProps) {
  const rpsStats = useGameTileStats('rps');
  const [playerChoice, setPlayerChoice] = useState(null as Choice | null);
  const [aiChoice, setAiChoice] = useState(null as Choice | null);
  const [gameResult, setGameResult] = useState(null as GameResult | null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [roundHistory, setRoundHistory] = useState([] as GameRound[]);
  const [streak, setStreak] = useState(0);
  const [betAmount, setBetAmount] = useState(50);
  const [countdown, setCountdown] = useState(null as number | null);
  const [showResult, setShowResult] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [currentSoundEffect, setCurrentSoundEffect] = useState(null as string | null);
  const [particles, setParticles] = useState(
    [] as Array<{ id: number; x: number; y: number; color: string }>
  );
  const [comboCount, setComboCount] = useState(0);
  const [isSpecialMove, setIsSpecialMove] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null as string | null);
  const withReconcile = useWithReconcile();
  const globalProfile = useGlobalProfile();
  const { syncAfterGame } = useGlobalSync();
  const { state, dispatch } = useGlobalStore();
  const gold = globalProfile?.goldBalance ?? 0;

  // Play sound effect (visual simulation)
  // 전역 store의 rps 승수 우선 표시 컴포넌트
  function RpsWins({ userWins }: { userWins: number }) {
    const { state } = useGlobalStore();
    const r = (state?.gameStats?.rps as any) || (state?.gameStats as any)?.['rps'];
    const rData = r && (r as any).data ? (r as any).data : r;
    const wins = typeof (rData as any)?.wins === 'number' ? (rData as any).wins : userWins;
    return <div className="text-xl font-bold text-primary">{wins}</div>;
  }
  const playSoundEffect = (effectName: string) => {
    if (!soundEnabled) return;

    const effect = SOUND_EFFECTS[effectName];
    if (effect) {
      setCurrentSoundEffect(effect.visual);
      setTimeout(() => setCurrentSoundEffect(null), effect.duration);
    }
  };

  // Generate particles
  const generateParticles = (result: GameResult) => {
    const colors = {
      win: ['#00ff88', '#ffeb3b', '#ff006e'],
      lose: ['#ff3366', '#666'],
      draw: ['#ffaa00', '#00ccff'],
    };

    const newParticles = Array.from({ length: 15 }, (_, i) => ({
      id: Date.now() + i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      color: colors[result][Math.floor(Math.random() * colors[result].length)],
    }));

    setParticles(newParticles);
    setTimeout(() => setParticles([]), 2000);
  };

  // Simple AI choice calculation (no patterns)
  const calculateAiChoice = (): Choice => {
    const choices: Choice[] = ['rock', 'paper', 'scissors'];
    return choices[Math.floor(Math.random() * 3)];
  };

  // Determine winner
  const determineWinner = (player: Choice, ai: Choice): GameResult => {
    if (player === ai) return 'draw';
    if (CHOICES[player].beats === ai) return 'win';
    return 'lose';
  };

  // Handle game play with improved timing
  const playGame = async (choice: Choice) => {
    if (isPlaying) return;

    if (gold < betAmount) {
      onAddNotification('❌ 골드가 부족합니다!');
      return;
    }

    setIsPlaying(true);
    setErrorMessage(null);
    // 🚫 사용자 선택을 미리 보여주지 않음!
    setPlayerChoice(null);
    setAiChoice(null);
    setShowResult(false);
    setGameResult(null);

    // 🎯 카운트다운 (선택 숨김 상태에서)
    playSoundEffect('countdown');
    for (let i = 3; i > 0; i--) {
      setCountdown(i);
      await new Promise((resolve) => setTimeout(resolve, 600));
    }
    setCountdown(null);

    // 🤖 AI와 플레이어 동시에 선택 공개 (동시성 보장)
    const ai = calculateAiChoice();
    setPlayerChoice(choice);
    setAiChoice(ai);

    // 서버 권위 플레이 호출 + 재동기화
    try {
      await withReconcile(async (idemKey: string) => {
        // 백엔드 스키마 준수: choice + bet_amount 필수
        const res = await api.post<any>(
          'games/rps/play',
          { choice, bet_amount: betAmount, game_id: 'rps' },
          { headers: { 'X-Idempotency-Key': idemKey } }
        );
        // 서버 결과를 화면 연출에 사용하되, 잔액은 재동기화에 위임
        const result: GameResult = res?.result ?? determineWinner(choice, ai);
        setGameResult(result);
        const winnings = Number(res?.win_amount ?? 0);
        // 히스토리/이펙트만 반영(로컬 잔액 수학 금지)
        const round: GameRound = {
          playerChoice: choice,
          aiChoice: ai,
          result,
          winnings: winnings - betAmount,
          isSpecialMove: false,
        };
        setRoundHistory((prev: GameRound[]) => [round, ...prev.slice(0, 9)]);
        // 통계 병합(표시용 캐시) — 최종 값은 syncAfterGame으로 서버 권위 반영
        mergeGameStats(dispatch, 'rps', {
          totalGames: 1,
          wins: result === 'win' ? 1 : 0,
          losses: result === 'lose' ? 1 : 0,
          draws: result === 'draw' ? 1 : 0,
          totalBet: betAmount,
          totalPayout: winnings,
        });
        // 게임 후 전역 동기화 (권위 반영)
        await syncAfterGame();
        return res;
      });
    } catch (e: any) {
      const msg =
        e?.message || (typeof e === 'string' ? e : '플레이 실패. 네트워크 상태를 확인해주세요.');
      setErrorMessage(msg);
      onAddNotification('플레이 실패. 네트워크 상태를 확인해주세요.');
    }

    setShowResult(true);
    setIsPlaying(false);
  };

  // Reset game
  const resetGame = () => {
    setPlayerChoice(null);
    setAiChoice(null);
    setGameResult(null);
    setShowResult(false);
    setCountdown(null);
    setIsSpecialMove(false);
    setComboCount(0);
    setParticles([]);
  };

  // 기존 user.gameStats 직접 참조 제거: 전역 store 우선 + legacy 폴백 계산을 사용
  // UI 표시는 전역 store의 gameStats 우선, 없으면 legacy user.gameStats로 폴백
  function firstNum(obj: any, keys: string[]): number | undefined {
    if (!obj) return undefined;
    for (const k of keys) {
      const v = obj?.[k];
      if (typeof v === 'number' && !Number.isNaN(v)) return v;
    }
    return undefined;
  }

  const rpsRaw = (state?.gameStats as any)?.rps ?? (state?.gameStats as any)?.['rps'];
  const rpsData = rpsRaw && (rpsRaw as any).data ? (rpsRaw as any).data : rpsRaw;
  const totalFromStore = firstNum(rpsData, [
    'totalGames',
    'matches',
    'games',
    'plays',
    'total_games',
  ]);
  const winsFromStore = firstNum(rpsData, ['wins', 'totalWins']);
  const lossesFromStore = firstNum(rpsData, ['losses']);
  const drawsFromStore = firstNum(rpsData, ['draws']);

  const totalGames = (totalFromStore ??
    (user as any)?.gameStats?.rps?.totalGames ??
    (user as any)?.gameStats?.rps?.matches ??
    0) as number;
  const wins = (winsFromStore ?? (user as any)?.gameStats?.rps?.wins ?? 0) as number;
  const losses = (lossesFromStore ??
    (user as any)?.gameStats?.rps?.losses ??
    Math.max(0, totalGames - wins)) as number;
  const draws = (drawsFromStore ??
    (user as any)?.gameStats?.rps?.draws ??
    Math.max(0, totalGames - wins - losses)) as number;
  const winRate = totalGames > 0 ? Math.round((wins / totalGames) * 100) : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-black to-success/10 relative overflow-hidden">
      {/* 오류 배너 */}
      <AnimatePresence>
        {errorMessage && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[92%] max-w-3xl bg-destructive/15 border border-destructive/40 text-destructive px-4 py-3 rounded-lg shadow-sm"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="text-sm leading-relaxed break-all">{errorMessage}</div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setErrorMessage(null);
                    if (playerChoice) {
                      void playGame(playerChoice);
                    }
                  }}
                >
                  재시도
                </Button>
                <Button size="sm" variant="ghost" onClick={() => setErrorMessage(null)}>
                  닫기
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      {/* Particle Effects */}
      <AnimatePresence>
        {particles.map((particle: { id: number; x: number; y: number; color: string }) => (
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
              y: `${particle.y - 20}vh`,
            }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
            className="fixed w-3 h-3 rounded-full pointer-events-none z-30"
            style={{ backgroundColor: particle.color }}
          />
        ))}
      </AnimatePresence>

      {/* Sound Effect Visual */}
      <AnimatePresence>
        {currentSoundEffect && (
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1.2 }}
            exit={{ opacity: 0, scale: 0.5 }}
            className="fixed top-20 left-1/2 transform -translate-x-1/2 text-4xl z-50 pointer-events-none bg-black/50 px-4 py-2 rounded-full backdrop-blur-sm"
          >
            {currentSoundEffect}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Countdown Overlay */}
      <AnimatePresence>
        {countdown && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-40 pointer-events-none"
          >
            <motion.div
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 1.5, opacity: 0 }}
              transition={{ duration: 0.6 }}
              className="relative"
            >
              <motion.div
                animate={{
                  scale: [1, 1.3, 1],
                  textShadow: [
                    '0 0 20px rgba(255,0,110,0.5)',
                    '0 0 40px rgba(255,0,110,1)',
                    '0 0 20px rgba(255,0,110,0.5)',
                  ],
                }}
                transition={{ duration: 0.6 }}
                className="text-9xl font-black text-primary"
              >
                {countdown}
              </motion.div>

              <motion.div
                initial={{ scale: 0, rotate: 0 }}
                animate={{ scale: 1.2, rotate: 360 }}
                transition={{ duration: 0.6 }}
                className="absolute inset-0 border-8 border-primary rounded-full"
              />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Simple Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 p-4 lg:p-6 border-b border-border-secondary/50 backdrop-blur-xl bg-card/80"
      >
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={onBack}
              className="glass-effect hover:bg-primary/10 transition-all duration-300"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              뒤로가기
            </Button>

            <h1 className="text-xl lg:text-2xl font-bold text-gradient-primary">가위바위보 대전</h1>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-4">
              <div className="glass-effect rounded-xl p-3 border border-primary/20">
                <div className="text-center">
                  <div className="text-xs text-muted-foreground">총 플레이</div>
                  <div className="text-lg font-bold text-primary">
                    {rpsStats.playCount.toLocaleString()}
                  </div>
                </div>
              </div>
              <div className="glass-effect rounded-xl p-3 border border-gold/20">
                <div className="text-center">
                  <div className="text-xs text-muted-foreground">최대 승리</div>
                  <div className="text-lg font-bold text-gradient-gold">
                    {rpsStats.bestScore.toLocaleString()}G
                  </div>
                </div>
              </div>
            </div>

            <Button
              variant="outline"
              size="icon"
              onClick={() => setSoundEnabled(!soundEnabled)}
              className="glass-effect hover:bg-primary/10 transition-all duration-300"
            >
              {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
            </Button>

            <div className="glass-effect rounded-xl p-3 border border-gold/20">
              <div className="text-right">
                <div className="text-sm text-muted-foreground">보유 골드</div>
                <div className="text-xl font-black text-gradient-gold">
                  {gold.toLocaleString()}G
                </div>
              </div>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Combo Banner */}
      {comboCount >= 3 && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative z-10 bg-gradient-to-r from-error to-warning text-white text-center py-3 font-bold"
        >
          <div className="flex items-center justify-center gap-2">
            <Flame className="w-5 h-5" />
            <span>🔥 {comboCount} COMBO STREAK! 🔥</span>
            <Flame className="w-5 h-5" />
          </div>
        </motion.div>
      )}

      {/* Main Content */}
      <div className="relative z-10 p-4 lg:p-6 max-w-4xl mx-auto">
        {/* 배팅액 설정 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-effect rounded-xl p-6 mb-6"
        >
          <div className="text-center">
            <h3 className="text-lg font-bold text-foreground mb-4 flex items-center justify-center gap-2">
              <Coins className="w-5 h-5 text-gold" />
              배팅액 설정
            </h3>

            <div className="flex items-center justify-center gap-4 mb-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setBetAmount(Math.max(10, betAmount - 50))}
                disabled={isPlaying || betAmount <= 10}
                className="border-border-secondary hover:border-primary"
              >
                -50G
              </Button>

              <div className="bg-gradient-to-r from-gold to-gold-light text-black px-6 py-3 rounded-lg font-bold text-xl min-w-[120px]">
                {betAmount.toLocaleString()}G
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setBetAmount(Math.min(1000, betAmount + 50))}
                disabled={isPlaying || betAmount >= 1000}
                className="border-border-secondary hover:border-primary"
              >
                +50G
              </Button>
            </div>

            <div className="flex gap-2 justify-center flex-wrap">
              {[10, 50, 100, 200, 500].map((amount) => (
                <Button
                  key={amount}
                  variant="outline"
                  size="sm"
                  onClick={() => setBetAmount(amount)}
                  disabled={isPlaying}
                  className={`border-border-secondary hover:border-primary ${
                    betAmount === amount ? 'bg-primary text-white' : ''
                  }`}
                >
                  {amount}G
                </Button>
              ))}
            </div>

            <div className="text-sm text-muted-foreground mt-2">
              승리 시 2배 지급 • 무승부 시 베팅금 반환
            </div>
          </div>
        </motion.div>

        {/* 🎯 완전 대칭적인 게임 화면 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-effect rounded-3xl p-12 mb-6 relative overflow-hidden"
        >
          {/* Result Effect */}
          <AnimatePresence>
            {showResult && gameResult && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className={`absolute inset-0 pointer-events-none z-10 ${
                  gameResult === 'win'
                    ? 'bg-success/10'
                    : gameResult === 'lose'
                    ? 'bg-error/10'
                    : 'bg-warning/10'
                }`}
              >
                <motion.div
                  animate={{
                    scale: [1, 1.05, 1],
                    boxShadow: [
                      `0 0 20px ${
                        gameResult === 'win'
                          ? 'rgba(0,255,136,0.3)'
                          : gameResult === 'lose'
                          ? 'rgba(255,51,102,0.3)'
                          : 'rgba(255,170,0,0.3)'
                      }`,
                      `0 0 40px ${
                        gameResult === 'win'
                          ? 'rgba(0,255,136,0.6)'
                          : gameResult === 'lose'
                          ? 'rgba(255,51,102,0.6)'
                          : 'rgba(255,170,0,0.6)'
                      }`,
                      `0 0 20px ${
                        gameResult === 'win'
                          ? 'rgba(0,255,136,0.3)'
                          : gameResult === 'lose'
                          ? 'rgba(255,51,102,0.3)'
                          : 'rgba(255,170,0,0.3)'
                      }`,
                    ],
                  }}
                  transition={{ duration: 1, repeat: Infinity }}
                  className={`absolute inset-0 border-4 rounded-3xl ${
                    gameResult === 'win'
                      ? 'border-success'
                      : gameResult === 'lose'
                      ? 'border-error'
                      : 'border-warning'
                  }`}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* 🔄 완전 대칭적인 플레이어들 */}
          <div className="grid grid-cols-2 gap-16 mb-12">
            {/* 🧑 플레이어 - 왼쪽 */}
            <div className="text-center">
              <div className="text-lg font-bold text-foreground mb-4 flex items-center justify-center gap-2">
                {isSpecialMove && <Sparkles className="w-5 h-5 text-gold" />}
                당신
                {streak >= 3 && <Crown className="w-5 h-5 text-gold" />}
              </div>
              <motion.div
                animate={
                  playerChoice
                    ? {
                        scale: [1, 1.3, 1],
                        rotate: [0, 10, -10, 0],
                      }
                    : {}
                }
                transition={{ duration: 0.6 }}
                className={`w-40 h-40 mx-auto bg-gradient-to-br from-primary to-primary-light rounded-full flex items-center justify-center text-8xl mb-6 shadow-2xl border-4 border-primary/30 ${
                  isSpecialMove ? 'animate-pulse' : ''
                }`}
              >
                {playerChoice ? CHOICES[playerChoice as Choice].emoji : '❓'}

                {isSpecialMove && (
                  <motion.div
                    animate={{ opacity: [0.5, 1, 0.5], scale: [1, 1.2, 1] }}
                    transition={{ duration: 0.8, repeat: Infinity }}
                    className="absolute inset-0 border-4 border-gold rounded-full"
                  />
                )}
              </motion.div>
              <div
                className={`text-lg font-bold ${
                  playerChoice ? CHOICES[playerChoice as Choice].color : 'text-muted-foreground'
                }`}
              >
                {playerChoice ? CHOICES[playerChoice as Choice].name : '선택하세요'}
              </div>
            </div>

            {/* 🤖 AI - 오른쪽 (완전 대칭) */}
            <div className="text-center">
              <div className="text-lg font-bold text-foreground mb-4 flex items-center justify-center gap-2">
                <span>🤖</span>
                AI 대전상대
                <span>⚡</span>
              </div>
              <motion.div
                animate={
                  aiChoice
                    ? {
                        scale: [1, 1.3, 1],
                        rotate: [0, -10, 10, 0],
                      }
                    : isPlaying
                    ? {
                        rotate: [0, 360],
                        scale: [1, 1.1, 1],
                      }
                    : {}
                }
                transition={{
                  duration: isPlaying ? 2 : 0.6,
                  repeat: isPlaying ? Infinity : 0,
                  ease: isPlaying ? 'linear' : 'easeInOut',
                }}
                className="w-40 h-40 mx-auto bg-gradient-to-br from-warning to-gold rounded-full flex items-center justify-center text-8xl mb-6 shadow-2xl border-4 border-warning/30"
              >
                {aiChoice ? CHOICES[aiChoice as Choice].emoji : '🤖'}
              </motion.div>
              <div
                className={`text-lg font-bold ${
                  aiChoice ? CHOICES[aiChoice as Choice].color : 'text-muted-foreground'
                }`}
              >
                {aiChoice ? CHOICES[aiChoice as Choice].name : isPlaying ? '생각 중...' : 'AI 대기'}
              </div>
            </div>
          </div>

          {/* VS */}
          <div className="text-center mb-8">
            <motion.div
              animate={{
                scale: [1, 1.2, 1],
                textShadow: [
                  '0 0 20px rgba(255,0,110,0.5)',
                  '0 0 40px rgba(255,0,110,1)',
                  '0 0 20px rgba(255,0,110,0.5)',
                ],
              }}
              transition={{ duration: 2, repeat: Infinity }}
              className="text-4xl font-black text-gradient-primary"
            >
              ⚔️ VS ⚔️
            </motion.div>
          </div>

          {/* Result */}
          <AnimatePresence>
            {showResult && gameResult && (
              <motion.div
                initial={{ opacity: 0, y: 20, scale: 0.8 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.8 }}
                className="text-center mb-6"
              >
                <motion.div
                  animate={{
                    scale: [1, 1.2, 1],
                    textShadow: [
                      `0 0 20px ${
                        gameResult === 'win'
                          ? 'rgba(0,255,136,0.5)'
                          : gameResult === 'lose'
                          ? 'rgba(255,51,102,0.5)'
                          : 'rgba(255,170,0,0.5)'
                      }`,
                      `0 0 40px ${
                        gameResult === 'win'
                          ? 'rgba(0,255,136,1)'
                          : gameResult === 'lose'
                          ? 'rgba(255,51,102,1)'
                          : 'rgba(255,170,0,1)'
                      }`,
                      `0 0 20px ${
                        gameResult === 'win'
                          ? 'rgba(0,255,136,0.5)'
                          : gameResult === 'lose'
                          ? 'rgba(255,51,102,0.5)'
                          : 'rgba(255,170,0,0.5)'
                      }`,
                    ],
                  }}
                  transition={{ duration: 0.8, repeat: 3, type: 'tween' }}
                  className={`text-4xl font-black mb-2 ${
                    gameResult === 'win'
                      ? 'text-success'
                      : gameResult === 'lose'
                      ? 'text-error'
                      : 'text-warning'
                  }`}
                >
                  {gameResult === 'win'
                    ? '🎉 VICTORY!'
                    : gameResult === 'lose'
                    ? '💀 DEFEAT!'
                    : '🤝 DRAW!'}
                </motion.div>

                {streak > 1 && gameResult === 'win' && (
                  <motion.div
                    animate={{ scale: [1, 1.1, 1] }}
                    transition={{ duration: 0.5, repeat: 2, type: 'tween' }}
                    className="text-lg text-gold font-bold"
                  >
                    🔥 {streak}연승 콤보! 🔥
                  </motion.div>
                )}

                {isSpecialMove && (
                  <motion.div
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 0.6, repeat: 3, type: 'tween' }}
                    className="text-lg text-gradient-gold font-bold"
                  >
                    ⭐ SPECIAL MOVE! ⭐
                  </motion.div>
                )}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Choice Buttons */}
          <div className="grid grid-cols-3 gap-6">
            {(Object.keys(CHOICES) as Choice[]).map((choice) => (
              <motion.div key={choice} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                  onClick={() => playGame(choice)}
                  disabled={isPlaying || gold < betAmount}
                  className="h-32 w-full bg-gradient-to-r from-secondary to-secondary-hover hover:from-primary hover:to-primary-light text-white font-bold text-xl flex flex-col items-center gap-3 relative overflow-hidden btn-hover-glow"
                >
                  <motion.div
                    animate={{ opacity: [0.3, 0.7, 0.3] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent"
                  />

                  <span className="text-5xl relative z-10">{CHOICES[choice].emoji}</span>
                  <span className="text-lg relative z-10">{CHOICES[choice].name}</span>
                </Button>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Game Stats & History */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Game Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="glass-effect rounded-xl p-6"
          >
            <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <Trophy className="w-5 h-5 text-gold" />
              게임 통계
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center p-3 rounded-lg bg-primary/10 border border-primary/20">
                  <RpsWins userWins={user?.gameStats?.rps?.wins ?? 0} />
                <div className="text-sm text-muted-foreground">승리</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-error/10 border border-error/20">
                <div className="text-xl font-bold text-error">{losses}</div>
                <div className="text-sm text-muted-foreground">패배</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-warning/10 border border-warning/20">
                <div className="text-xl font-bold text-warning">{draws}</div>
                <div className="text-sm text-muted-foreground">무승부</div>
              </div>
              <div className="text-center p-3 rounded-lg bg-success/10 border border-success/20">
                <div className="text-xl font-bold text-success">{streak}</div>
                <div className="text-sm text-muted-foreground">연승</div>
              </div>
            </div>
          </motion.div>

          {/* Recent History */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="glass-effect rounded-xl p-6"
          >
            <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <Timer className="w-5 h-5 text-primary" />
              최근 게임
            </h3>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {roundHistory.length === 0 ? (
                <div className="text-center text-muted-foreground py-4">
                  아직 게임 기록이 없습니다
                </div>
              ) : (
                <>
                  {roundHistory.slice(0, 5).map((round: GameRound, index: number) => (
                    <div
                      key={index}
                      className={`flex items-center justify-between p-2 rounded-lg text-sm ${
                        round.result === 'win'
                          ? 'bg-success/10 border border-success/20'
                          : round.result === 'lose'
                          ? 'bg-error/10 border border-error/20'
                          : 'bg-warning/10 border border-warning/20'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span>{CHOICES[round.playerChoice].emoji}</span>
                        <span className="text-muted-foreground">vs</span>
                        <span>{CHOICES[round.aiChoice].emoji}</span>
                      </div>
                      <div
                        className={`font-bold ${
                          round.result === 'win'
                            ? 'text-success'
                            : round.result === 'lose'
                            ? 'text-error'
                            : 'text-warning'
                        }`}
                      >
                        {round.result === 'win' ? '+' : round.result === 'lose' ? '-' : ''}
                        {Math.abs(round.winnings).toLocaleString()}G
                      </div>
                    </div>
                  ))}
                </>
              )}
            </div>
          </motion.div>
        </div>

        {/* Reset Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="text-center mt-6"
        >
          <Button
            onClick={resetGame}
            variant="outline"
            className="border-border-secondary hover:border-primary btn-hover-lift"
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            게임 초기화
          </Button>
        </motion.div>
      </div>
    </div>
  );
}
