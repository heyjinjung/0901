'use client';
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '../ui/button';

interface DailyRewardClaimedDialogProps {
  open: boolean;
  onClose: () => void;
  onNavigateGame: () => void;
  onScheduleReminder: () => void; // 추후 실제 알림 스케줄러 연동
  nextResetAt?: string; // ISO (선택)
}

export const DailyRewardClaimedDialog = ({
  open,
  onClose,
  onNavigateGame,
  onScheduleReminder,
  nextResetAt,
}: DailyRewardClaimedDialogProps) => {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 backdrop-blur-sm bg-black/60"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="w-full max-w-md rounded-2xl bg-gradient-to-b from-zinc-900 to-zinc-950 border border-zinc-700 shadow-2xl relative overflow-hidden"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 160, damping: 18 }}
          >
            <div className="absolute inset-0 pointer-events-none opacity-20 bg-[radial-gradient(circle_at_30%_30%,#ffaa00,transparent_60%)]" />
            <div className="p-6 relative z-10">
              <h2 className="text-xl font-extrabold text-amber-300 flex items-center gap-2 mb-3">
                <span>📦 일일 보상 이미 수령</span>
              </h2>
              <p className="text-sm text-zinc-300 leading-relaxed mb-4">
                중복 지급은 되지 않아요. 내일 00:00 이후 다시 도전!
                <br />
                {nextResetAt && (
                  <span className="block mt-2 text-xs text-amber-400/80">
                    다음 리셋 예정: {nextResetAt}
                  </span>
                )}
              </p>
              <div className="flex flex-col gap-2">
                <Button
                  onClick={() => {
                    onScheduleReminder();
                    onClose();
                  }}
                  className="w-full bg-amber-500 hover:bg-amber-400 font-semibold text-black"
                >
                  내일 알림 받기
                </Button>
                <Button
                  variant="outline"
                  onClick={() => {
                    onNavigateGame();
                    onClose();
                  }}
                  className="w-full border-amber-400 text-amber-300 hover:bg-amber-400/10"
                >
                  다른 게임 하기
                </Button>
                <Button
                  variant="ghost"
                  onClick={onClose}
                  className="w-full text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/30"
                >
                  닫기
                </Button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default DailyRewardClaimedDialog;
