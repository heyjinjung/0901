import React from 'react';

// Crown Icon SVG
export const CrownIcon = ({ className = "w-6 h-6", color = "currentColor" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M5 16L3 4l3.5 2.5L12 3l5.5 3.5L21 4l-2 12H5z"
      fill={color}
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <circle cx="12" cy="8" r="1" fill="white"/>
    <circle cx="8" cy="10" r="0.5" fill="white"/>
    <circle cx="16" cy="10" r="0.5" fill="white"/>
  </svg>
);

// Slot Machine Icon SVG
export const SlotMachineIcon = ({ className = "w-6 h-6", color = "currentColor" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="4" y="3" width="16" height="18" rx="2" fill={color} stroke="white" strokeWidth="2"/>
    <rect x="6" y="6" width="3" height="4" rx="1" fill="white"/>
    <rect x="10.5" y="6" width="3" height="4" rx="1" fill="white"/>
    <rect x="15" y="6" width="3" height="4" rx="1" fill="white"/>
    <circle cx="7.5" cy="8" r="0.5" fill={color}/>
    <circle cx="12" cy="8" r="0.5" fill={color}/>
    <circle cx="16.5" cy="8" r="0.5" fill={color}/>
    <rect x="8" y="16" width="8" height="2" rx="1" fill="white"/>
    <circle cx="12" cy="17" r="0.5" fill={color}/>
  </svg>
);

// Roulette Icon SVG
export const RouletteIcon = ({ className = "w-6 h-6", color = "currentColor" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="9" fill={color} stroke="white" strokeWidth="2"/>
    <circle cx="12" cy="12" r="6" fill="none" stroke="white" strokeWidth="1"/>
    <circle cx="12" cy="12" r="3" fill="none" stroke="white" strokeWidth="1"/>
    <circle cx="12" cy="12" r="1" fill="white"/>
    <path d="M12 3 L13 6 L11 6 Z" fill="white"/>
    <path d="M12 6 L12.5 9 L11.5 9 Z" fill="white"/>
    <path d="M15 12 L18 12" stroke="white" strokeWidth="1"/>
    <path d="M9 12 L6 12" stroke="white" strokeWidth="1"/>
    <path d="M12 15 L12 18" stroke="white" strokeWidth="1"/>
  </svg>
);

// Gacha Box Icon SVG
export const GachaBoxIcon = ({ className = "w-6 h-6", color = "currentColor" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="3" y="6" width="18" height="12" rx="2" fill={color} stroke="white" strokeWidth="2"/>
    <rect x="3" y="4" width="18" height="4" rx="2" fill="white"/>
    <rect x="10" y="2" width="4" height="4" rx="1" fill={color}/>
    <circle cx="12" cy="12" r="3" fill="white"/>
    <circle cx="12" cy="12" r="2" fill={color}/>
    <circle cx="12" cy="12" r="1" fill="white"/>
    <path d="M6 10 L8 8" stroke="white" strokeWidth="1"/>
    <path d="M18 10 L16 8" stroke="white" strokeWidth="1"/>
    <circle cx="7" cy="15" r="0.5" fill="white"/>
    <circle cx="17" cy="15" r="0.5" fill="white"/>
  </svg>
);

// Sword Fight Icon SVG
export const SwordFightIcon = ({ className = "w-6 h-6", color = "currentColor" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M6 3 L8 5 L5 8 L3 6 Z" fill={color} stroke="white" strokeWidth="1"/>
    <path d="M18 3 L16 5 L19 8 L21 6 Z" fill={color} stroke="white" strokeWidth="1"/>
    <path d="M8 5 L16 13" stroke="white" strokeWidth="2"/>
    <path d="M16 5 L8 13" stroke="white" strokeWidth="2"/>
    <circle cx="12" cy="9" r="2" fill="white" stroke={color} strokeWidth="1"/>
    <path d="M5 8 L8 11 L6 13 L3 10 Z" fill="white"/>
    <path d="M19 8 L16 11 L18 13 L21 10 Z" fill="white"/>
    <circle cx="12" cy="9" r="1" fill={color}/>
  </svg>
);

// Gold Coin Icon SVG
export const GoldCoinIcon = ({ className = "w-6 h-6", color = "#e6c200" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="9" fill={color} stroke="#f5d700" strokeWidth="2"/>
    <circle cx="12" cy="12" r="6" fill="none" stroke="#cc9e00" strokeWidth="1"/>
    <path d="M9 10 C9 8 10 7 12 7 C14 7 15 8 15 10 C15 11 14 11 13 12 L11 12 C10 11 9 11 9 10 Z" fill="#cc9e00"/>
    <path d="M10 14 L14 14" stroke="#cc9e00" strokeWidth="2"/>
    <path d="M12 16 L12 18" stroke="#cc9e00" strokeWidth="2"/>
    <path d="M12 6 L12 8" stroke="#cc9e00" strokeWidth="2"/>
  </svg>
);

// Trophy Icon SVG
export const TrophyIcon = ({ className = "w-6 h-6", color = "currentColor" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M7 3 L17 3 L17 10 C17 13 14.5 15 12 15 C9.5 15 7 13 7 10 L7 3 Z" fill={color} stroke="white" strokeWidth="2"/>
    <path d="M17 5 L20 5 C21 5 21 7 20 8 L17 8" stroke="white" strokeWidth="2" fill="none"/>
    <path d="M7 5 L4 5 C3 5 3 7 4 8 L7 8" stroke="white" strokeWidth="2" fill="none"/>
    <rect x="9" y="15" width="6" height="4" fill="white"/>
    <rect x="6" y="19" width="12" height="2" rx="1" fill="white"/>
    <circle cx="12" cy="8" r="2" fill="white"/>
    <circle cx="12" cy="8" r="1" fill={color}/>
  </svg>
);

// Star Achievement Icon SVG
export const StarAchievementIcon = ({ className = "w-6 h-6", color = "currentColor" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2 L15 8 L22 9 L17 14 L18 21 L12 18 L6 21 L7 14 L2 9 L9 8 Z" fill={color} stroke="white" strokeWidth="2"/>
    <circle cx="12" cy="10" r="3" fill="white"/>
    <circle cx="12" cy="10" r="2" fill={color}/>
    <circle cx="12" cy="10" r="1" fill="white"/>
    <path d="M9 16 L15 16" stroke="white" strokeWidth="1"/>
  </svg>
);

// Lightning Bolt Icon SVG
export const LightningBoltIcon = ({ className = "w-6 h-6", color = "currentColor" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M13 2 L4 14 L10 14 L11 22 L20 10 L14 10 L13 2 Z" fill={color} stroke="white" strokeWidth="2"/>
    <path d="M11 6 L13 8 L11 10" stroke="white" strokeWidth="1" fill="none"/>
    <path d="M13 14 L11 16 L13 18" stroke="white" strokeWidth="1" fill="none"/>
  </svg>
);

// Gem Diamond Icon SVG
export const GemDiamondIcon = ({ className = "w-6 h-6", color = "currentColor" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M6 9 L12 3 L18 9 L12 21 Z" fill={color} stroke="white" strokeWidth="2"/>
    <path d="M6 9 L18 9" stroke="white" strokeWidth="1"/>
    <path d="M9 9 L12 3 L15 9" stroke="white" strokeWidth="1" fill="none"/>
    <path d="M9 9 L12 15" stroke="white" strokeWidth="1"/>
    <path d="M15 9 L12 15" stroke="white" strokeWidth="1"/>
    <circle cx="12" cy="12" r="1" fill="white"/>
  </svg>
);