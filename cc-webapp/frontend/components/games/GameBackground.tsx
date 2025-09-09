'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface GameBackgroundProps {
  particleCount?: number;
}

export function GameBackground({ particleCount = 25 }: GameBackgroundProps) {
  return (
    <div className="absolute inset-0">
      {[...Array(particleCount)].map((_, i) => (
        <motion.div
          key={i}
          initial={{ 
            opacity: 0,
            x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1000),
            y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 1000)
          }}
          animate={{ 
            opacity: [0, 0.3, 0],
            scale: [0, 1.5, 0],
            rotate: 360
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            delay: i * 0.2,
            ease: "easeInOut"
          }}
          className="absolute w-1 h-1 bg-gold rounded-full"
        />
      ))}
    </div>
  );
}