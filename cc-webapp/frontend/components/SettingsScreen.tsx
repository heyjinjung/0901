'use client';

import React, { useState } from 'react';
// unifiedApi/profile edit removed — nickname editing disabled
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft,
  Volume2,
  VolumeX,
  Vibrate,
  Bell,
  BellOff,
  User,
  Settings,
  HelpCircle,
  Info,
  Mail,
  Star,
  ExternalLink,
  Video,
  Crown,
  Sparkles,
} from 'lucide-react';
import { User as UserType } from '../types';
import { useGlobalStore, useGlobalProfile } from '@/store/globalStore';
// profile writeback disabled — global store updates via canonical sync flows
import { useUserSummary } from '@/hooks/useSelectors';
import api from '../utils/api';
import { Button } from './ui/button';
import { Switch } from './ui/switch';
import { Slider } from './ui/slider';

interface SettingsScreenProps {
  user: UserType;
  onBack: () => void;
  onUpdateUser: (user: UserType) => void;
  onAddNotification: (message: string) => void;
}

export function SettingsScreen({
  user,
  onBack,
  onUpdateUser,
  onAddNotification,
}: SettingsScreenProps) {
  const { dispatch } = useGlobalStore();
  const globalProfile = useGlobalProfile();
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [soundVolume, setSoundVolume] = useState([80]);
  const [musicEnabled, setMusicEnabled] = useState(true);
  const [musicVolume, setMusicVolume] = useState([60]);
  const [vibrationEnabled, setVibrationEnabled] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [showBalance, setShowBalance] = useState(true);
  // 닉네임 편집 기능 비활성화: display-only

  const handleSoundToggle = (enabled: boolean) => {
    setSoundEnabled(enabled);
    onAddNotification(enabled ? '🔊 사운드가 활성화되었습니다' : '🔇 사운드가 비활성화되었습니다');
  };

  const handleVibrationToggle = (enabled: boolean) => {
    setVibrationEnabled(enabled);
    onAddNotification(enabled ? '📳 진동이 활성화되었습니다' : '📳 진동이 비활성화되었습니다');
  };

  const handleNotificationToggle = (enabled: boolean) => {
    setNotificationsEnabled(enabled);
    onAddNotification(enabled ? '🔔 알림이 활성화되었습니다' : '🔕 알림이 비활성화되었습니다');
  };

  // 닉네임 수정/저장 기능은 정책상 제거되었습니다. 프로필 변경은 서버 측 계정 설정을 통해 처리하세요.

  // 🗑️ 자동플레이 기능 완전 제거 + 간소화
  const settingsSections = [
    {
      title: '오디오 설정',
      icon: Volume2,
      items: [
        {
          title: '사운드 효과',
          description: '게임 내 효과음',
          control: <Switch checked={soundEnabled} onCheckedChange={handleSoundToggle} />,
        },
        {
          title: '사운드 볼륨',
          description: '효과음 크기 조절',
          control: (
            <div className="w-24">
              <Slider
                value={soundVolume}
                onValueChange={setSoundVolume}
                max={100}
                step={10}
                disabled={!soundEnabled}
              />
            </div>
          ),
        },
        {
          title: '배경 음악',
          description: '게임 BGM',
          control: <Switch checked={musicEnabled} onCheckedChange={setMusicEnabled} />,
        },
        {
          title: '음악 볼륨',
          description: '배경음악 크기 조절',
          control: (
            <div className="w-24">
              <Slider
                value={musicVolume}
                onValueChange={setMusicVolume}
                max={100}
                step={10}
                disabled={!musicEnabled}
              />
            </div>
          ),
        },
      ],
    },
    {
      title: '알림 설정',
      icon: Bell,
      items: [
        {
          title: '푸시 알림',
          description: '게임 알림 받기',
          control: (
            <Switch checked={notificationsEnabled} onCheckedChange={handleNotificationToggle} />
          ),
        },
        {
          title: '진동',
          description: '햅틱 피드백',
          control: <Switch checked={vibrationEnabled} onCheckedChange={handleVibrationToggle} />,
        },
      ],
    },
    {
      title: '프라이버시',
      icon: Settings,
      items: [
        {
          title: '골드 표시',
          description: '다른 사용자에게 골드 공개',
          control: <Switch checked={showBalance} onCheckedChange={setShowBalance} />,
        },
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-black to-primary-soft relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0">
        {[...Array(15)].map((_, i) => (
          <motion.div
            key={i}
            initial={{
              opacity: 0,
              x: Math.random() * (typeof window !== 'undefined' ? window.innerWidth : 1000),
              y: Math.random() * (typeof window !== 'undefined' ? window.innerHeight : 1000),
            }}
            animate={{
              opacity: [0, 0.2, 0],
              scale: [0, 1, 0],
              rotate: 360,
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              delay: i * 0.5,
              ease: 'easeInOut',
            }}
            className="absolute w-1 h-1 bg-primary rounded-full"
          />
        ))}
      </div>

      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 p-4 lg:p-6 border-b border-border-secondary backdrop-blur-sm"
      >
        <div className="flex items-center justify-between max-w-4xl mx-auto">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={onBack}
              className="border-border-secondary hover:border-primary btn-hover-lift"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              뒤로가기
            </Button>

            <div>
              <h1 className="text-xl lg:text-2xl font-bold text-gradient-primary">설정</h1>
            </div>
          </div>

          <div className="text-right">
            <div className="text-sm text-muted-foreground">{globalProfile?.nickname ?? user.nickname}</div>
            <div className="text-lg font-bold text-gold">레벨 {globalProfile?.level ?? 1}</div>
          </div>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="relative z-10 p-4 lg:p-6 max-w-4xl mx-auto pb-24">
        {/* User Profile Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-effect rounded-xl p-6 mb-6 card-hover-float"
        >
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-gradient-game rounded-full flex items-center justify-center">
              <User className="w-8 h-8 text-white" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <div className="text-lg font-bold text-foreground">{user.nickname}</div>
              </div>
              <p className="text-sm text-muted-foreground">
                레벨 {globalProfile?.level ?? 1} • {(globalProfile?.goldBalance ?? 0).toLocaleString()}G
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-gold">{(() => {
                  const raw = (globalProfile as any)?.daily_streak ?? (globalProfile as any)?.dailyStreak ?? 0;
                  return raw === 0 ? 1 : raw;
                })()}</div>
              <div className="text-xs text-muted-foreground">연속일</div>
            </div>
          </div>
        </motion.div>

        {/* 🎯 프리미엄 모델 바로가기 - 강조된 새로운 섹션 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25 }}
          className="mb-8"
        >
          <div className="glass-metal rounded-xl p-8 border-2 border-gold/30 relative overflow-hidden metal-shine">
            {/* 배경 효과 */}
            <div className="absolute inset-0 bg-gradient-to-r from-gold/5 to-primary/5"></div>

            <div className="relative z-10 text-center">
              <motion.div
                animate={{
                  scale: [1, 1.1, 1],
                  rotate: [0, 5, -5, 0],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
                className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-gold to-gold-light rounded-full flex items-center justify-center"
              >
                <Sparkles className="w-10 h-10 text-black" />
              </motion.div>

              <h3 className="text-2xl font-bold text-gradient-gold mb-3">✨ 프리미엄 모델 ✨</h3>
              <p className="text-lg text-muted-foreground mb-6">
                전속 VJ "Luna Star"와 함께하는 특별한 경험
              </p>

              <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
                <div className="glass-metal rounded-lg p-3">
                  <Video className="w-5 h-5 text-primary mx-auto mb-2" />
                  <div className="text-foreground font-bold">개인방 시스템</div>
                  <div className="text-muted-foreground">1:1 맞춤 서비스</div>
                </div>
                <div className="glass-metal rounded-lg p-3">
                  <Crown className="w-5 h-5 text-gold mx-auto mb-2" />
                  <div className="text-foreground font-bold">VIP 구독</div>
                  <div className="text-muted-foreground">프리미엄 혜택</div>
                </div>
              </div>

              <Button
                onClick={() => {
                  window.open('https://md-01.com', '_blank');
                  onAddNotification('🌟 프리미엄 모델 페이지로 이동합니다!');
                }}
                className="bg-gradient-to-r from-gold to-gold-light text-black font-bold px-8 py-4 text-lg btn-hover-lift relative overflow-hidden"
              >
                <motion.div
                  animate={{
                    x: ['100%', '-100%'],
                    opacity: [0, 1, 0],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                  className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                />
                <Star className="w-5 h-5 mr-2" />
                모델 바로가기
                <ExternalLink className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Settings Sections */}
        {settingsSections.map((section, sectionIndex) => (
          <motion.div
            key={section.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + sectionIndex * 0.1 }}
            className="glass-effect rounded-xl p-6 mb-6 card-hover-float"
          >
            <div className="flex items-center gap-3 mb-4">
              <section.icon className="w-5 h-5 text-primary" />
              <h3 className="text-lg font-bold text-foreground">{section.title}</h3>
            </div>

            <div className="space-y-4">
              {section.items.map((item, itemIndex) => (
                <div key={itemIndex} className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="font-medium text-foreground">{item.title}</div>
                    <div className="text-sm text-muted-foreground">{item.description}</div>
                  </div>
                  <div className="ml-4">{item.control}</div>
                </div>
              ))}
            </div>
          </motion.div>
        ))}

        {/* App Info */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="glass-effect rounded-xl p-6 card-hover-float"
        >
          <div className="flex items-center gap-3 mb-4">
            <Info className="w-5 h-5 text-info" />
            <h3 className="text-lg font-bold text-foreground">앱 정보</h3>
          </div>

          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-foreground">버전</span>
              <span className="text-muted-foreground">1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-foreground">마지막 업데이트</span>
              <span className="text-muted-foreground">2024.12.30</span>
            </div>
            <div className="flex justify-between">
              <span className="text-foreground">개발자</span>
              <span className="text-muted-foreground">Neon Quest Team</span>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-border-secondary">
            <div className="grid grid-cols-2 gap-4">
              <Button
                variant="outline"
                className="border-border-secondary hover:border-info text-info btn-hover-lift"
                onClick={() => onAddNotification('📚 도움말을 확인해보세요')}
              >
                <HelpCircle className="w-4 h-4 mr-2" />
                도움말
              </Button>
              <Button
                variant="outline"
                className="border-border-secondary hover:border-success text-success btn-hover-lift"
                onClick={() => onAddNotification('✉️ 문의사항을 보내주세요')}
              >
                <Mail className="w-4 h-4 mr-2" />
                문의하기
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}