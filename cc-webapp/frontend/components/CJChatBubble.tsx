'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, 
  MicOff, 
  Heart, 
  Frown, 
  Angry, 
  Sparkles,
  Volume2,
  VolumeX
} from 'lucide-react';

interface CJChatBubbleProps {
  message: string;
  state?: 'idle' | 'typing' | 'speaking';
  avatarMood?: 'normal' | 'happy' | 'sad' | 'angry';
  showVoiceToggle?: boolean;
  onVoiceToggle?: () => void;
  className?: string;
}

export function CJChatBubble({
  message,
  state = 'idle',
  avatarMood = 'normal',
  showVoiceToggle = false,
  onVoiceToggle,
  className = ''
}: CJChatBubbleProps) {
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false);
  const [displayedMessage, setDisplayedMessage] = useState('');

  // Typing animation effect
  useEffect(() => {
    if (state === 'typing') {
      setDisplayedMessage('');
      let index = 0;
      const timer = setInterval(() => {
        if (index < message.length) {
          setDisplayedMessage((prev: string) => prev + message[index]);
          index++;
        } else {
          clearInterval(timer);
        }
      }, 50);
      return () => clearInterval(timer);
    } else {
      setDisplayedMessage(message);
    }
  }, [message, state]);

  const getAvatarColors = () => {
    switch (avatarMood) {
      case 'happy':
        return {
          bg: 'from-emerald-400 to-cyan-400',
          glow: 'shadow-emerald-400/30',
          filter: 'saturate-150 brightness-110'
        };
      case 'sad':
        return {
          bg: 'from-blue-400 to-indigo-400',
          glow: 'shadow-blue-400/30',
          filter: 'saturate-75 brightness-90'
        };
      case 'angry':
        return {
          bg: 'from-red-400 to-orange-400',
          glow: 'shadow-red-400/30',
          filter: 'saturate-125 contrast-110'
        };
      default:
        return {
          bg: 'from-blue-500 to-purple-500',
          glow: 'shadow-blue-500/30',
          filter: 'saturate-100'
        };
    }
  };

  const getAvatarIcon = () => {
    switch (avatarMood) {
      case 'happy':
        return <Heart className="w-5 h-5 text-white" />;
      case 'sad':
        return <Frown className="w-5 h-5 text-white" />;
      case 'angry':
        return <Angry className="w-5 h-5 text-white" />;
      default:
        return <Sparkles className="w-5 h-5 text-white" />;
    }
  };

  const getStateAnimation = () => {
    switch (state) {
      case 'typing':
        return {
          scale: [1, 1.05, 1],
          transition: { duration: 1.5, repeat: Infinity }
        };
      case 'speaking':
        return {
          scale: [1, 1.1, 1],
          transition: { duration: 0.8, repeat: Infinity }
        };
      default:
        return {
          scale: [1, 1.02, 1],
          transition: { duration: 3, repeat: Infinity }
        };
    }
  };

  const handleVoiceToggle = () => {
    setIsVoiceEnabled(!isVoiceEnabled);
    onVoiceToggle?.();
  };

  const avatarColors = getAvatarColors();
  const avatarIcon = getAvatarIcon();
  const stateAnimation = getStateAnimation();

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5, type: "spring", stiffness: 100 }}
      className={`flex items-start gap-3 max-w-2xl ${className}`}
    >
      {/* AI Avatar */}
      <div className="flex-shrink-0">
        <motion.div
          animate={stateAnimation}
          className={`relative w-12 h-12 rounded-full overflow-hidden shadow-lg ${avatarColors.glow}`}
        >
          {/* Avatar Background */}
          <div className={`w-full h-full bg-gradient-to-br ${avatarColors.bg} flex items-center justify-center ${avatarColors.filter}`}>
            {avatarIcon}
          </div>

          {/* Breathing Animation Ring */}
          <motion.div
            animate={{ 
              scale: [1, 1.2, 1],
              opacity: [0.6, 0, 0.6]
            }}
            transition={{ 
              duration: 2, 
              repeat: Infinity,
              ease: "easeInOut",
              type: 'tween'
            }}
            className={`absolute inset-0 rounded-full bg-gradient-to-br ${avatarColors.bg} opacity-30`}
          />

          {/* State Indicator */}
          <AnimatePresence>
            {state !== 'idle' && (
              <motion.div
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0, opacity: 0 }}
                className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-emerald-500 border-2 border-slate-900 flex items-center justify-center"
              >
                {state === 'speaking' && (
                  <motion.div
                    animate={{ scale: [1, 1.3, 1] }}
                    transition={{ duration: 0.6, repeat: Infinity, type: 'tween' }}
                  >
                    <Volume2 className="w-2 h-2 text-white" />
                  </motion.div>
                )}
                  {state === 'typing' && (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    >
                      <div className="w-1 h-1 bg-white rounded-full" />
                    </motion.div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
        {/* Chat Bubble */}
      <div className="flex-1 relative">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.4, type: "spring", stiffness: 150 }}
          className="relative"
        >
          <div className={`
            relative bg-[#2d2d2d] backdrop-blur-xl 
            border border-slate-700/50 rounded-xl rounded-bl-none
            px-4 py-3 max-w-xs w-fit
            shadow-xl shadow-black/20
            before:absolute before:inset-0 before:rounded-xl before:rounded-bl-none
            before:bg-gradient-to-br before:from-white/5 before:to-transparent
            before:pointer-events-none
          `}>
            {/* Speech Tail */}
            <div className="absolute -left-2 bottom-0 w-4 h-4">
              <div className="w-full h-full bg-[#2d2d2d] border-l border-b border-slate-700/50 rounded-bl-lg transform rotate-45 origin-bottom-left" />
            </div>

            {/* Message Content */}
            <div className="relative z-10">
              {state === 'typing' && displayedMessage === '' ? (
                <div className="flex items-center gap-1 py-1">
                  <motion.div
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
                    className="w-1.5 h-1.5 bg-slate-400 rounded-full"
                  />
                  <motion.div
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.2, type: 'tween' }}
                    className="w-1.5 h-1.5 bg-slate-400 rounded-full"
                  />
                  <motion.div
                    animate={{ opacity: [0.4, 1, 0.4] }}
                    transition={{ duration: 1.5, repeat: Infinity, delay: 0.4, type: 'tween' }}
                    className="w-1.5 h-1.5 bg-slate-400 rounded-full"
                  />
                </div>
              ) : (
                <motion.p 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-slate-100 text-sm leading-relaxed"
                >
                  {displayedMessage}
                  {state === 'typing' && (
                    <motion.span
                      animate={{ opacity: [0, 1, 0] }}
                      transition={{ duration: 1, repeat: Infinity, type: 'tween' }}
                      className="ml-1 text-blue-400"
                    >
                      |
                    </motion.span>
                  )}
                </motion.p>
              )}
            </div>

            {/* Voice Toggle Button */}
            {showVoiceToggle && (
              <motion.div
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.5, type: "spring", stiffness: 200 }}
                className="absolute -top-2 -right-2"
              >
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={handleVoiceToggle}
                  className={`
                    w-8 h-8 rounded-full flex items-center justify-center
                    border-2 border-slate-700/50 backdrop-blur-xl
                    shadow-lg transition-colors duration-200
                    ${isVoiceEnabled 
                      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' 
                      : 'bg-slate-700/50 text-slate-400 hover:bg-slate-600/50 hover:text-slate-300'
                    }
                  `}
                >
                  <AnimatePresence mode="wait">
                    {isVoiceEnabled ? (
                      <motion.div
                        key="mic-on"
                        initial={{ rotate: -90, opacity: 0 }}
                        animate={{ rotate: 0, opacity: 1 }}
                        exit={{ rotate: 90, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                      >
                        <Mic className="w-3 h-3" />
                      </motion.div>
                    ) : (
                      <motion.div
                        key="mic-off"
                        initial={{ rotate: 90, opacity: 0 }}
                        animate={{ rotate: 0, opacity: 1 }}
                        exit={{ rotate: -90, opacity: 0 }}
                        transition={{ duration: 0.2 }}
                      >
                        <MicOff className="w-3 h-3" />
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.button>

                {/* Voice Toggle Indicator */}
                {isVoiceEnabled && (
                  <motion.div
                    animate={{ scale: [1, 1.5, 1], opacity: [0.6, 0, 0.6] }}
                    transition={{ duration: 2, repeat: Infinity, type: 'tween' }}
                    className="absolute inset-0 rounded-full bg-emerald-400/20"
                  />
                )}
              </motion.div>
            )}
          </div>
        </motion.div>

        {/* Message Timestamp */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="mt-1 ml-2 text-xs text-slate-500"
        >
          CJ AI • {new Date().toLocaleTimeString('ko-KR', { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </motion.div>
      </div>
    </motion.div>
  );
}