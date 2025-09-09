'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Gamepad2, Sparkles } from 'lucide-react';

interface ProductionLoadingScreenProps {
  onComplete?: () => void;
  duration?: number;
}

export function ProductionLoadingScreen({
  onComplete,
  duration = 3000,
}: ProductionLoadingScreenProps) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev: number) => {
        const newValue = prev + 1;
        if (newValue >= 100) {
          clearInterval(interval);
          if (onComplete) {
            setTimeout(onComplete, 500);
          }
          return 100;
        }
        return newValue;
      });
    }, duration / 100);

    return () => clearInterval(interval);
  }, [duration, onComplete]);

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-gray-900 to-black flex flex-col items-center justify-center z-50">
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ type: 'spring', duration: 0.8 }}
        className="mb-8"
      >
        <div className="relative">
          <Gamepad2 className="w-24 h-24 text-primary" />
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: [0, 1.2, 1] }}
            transition={{ delay: 0.5, duration: 0.5, type: 'tween' }}
            className="absolute -top-2 -right-2"
          >
            <Sparkles className="w-8 h-8 text-gold" />
          </motion.div>
        </div>
      </motion.div>

      <h1 className="text-3xl font-bold text-white mb-8 text-center">
        <span className="text-gradient-gold">Casino-Club</span> F2P
      </h1>

      <div className="w-64 h-2 bg-gray-800 rounded-full overflow-hidden mb-2">
        <motion.div
          className="h-full bg-gradient-to-r from-primary to-gold"
          style={{ width: `${progress}%` }}
        />
      </div>

      <p className="text-gray-400 text-sm">{progress}%</p>
    </div>
  );
}

export default ProductionLoadingScreen;
