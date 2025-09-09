# CC-WEBAPP Frontend Development Guide

**Complete English Specification - All Dev Spec Documents Implemented**

Last Updated: 2025-01-26

---

## ✅ Dev Spec Documentation Status

All required "개발용 스펙 문서" items from Figma workflow are **COMPLETE**:

- [x] **CSS Variables** - Fully implemented and documented
- [x] **Animation Timing Functions** - Complete with cubic bezier functions
- [x] **Responsive Breakpoints** - Tailwind-based responsive system
- [x] **Component Props Definitions** - TypeScript interfaces documented
- [x] **State Transition Diagrams** - Logic flow documented in code

---

## Table of Contents

1. [CSS Variables System](#1-css-variables-system)
2. [Animation Timing Functions](#2-animation-timing-functions)
3. [Responsive Breakpoints](#3-responsive-breakpoints)
4. [Component Props Definitions](#4-component-props-definitions)
5. [State Transition Diagrams](#5-state-transition-diagrams)
6. [Color System](#6-color-system)
7. [Typography](#7-typography)
8. [Grid & Spacing](#8-grid--spacing)
9. [Component Architecture](#9-component-architecture)
10. [Layout System](#10-layout-system)

---

## 1. CSS Variables System

### 🎨 Color Variables

```css
:root {
  /* Neon Purple System */
  --neon-purple-1: #7b29cd;
  --neon-purple-2: #870dd1;
  --neon-purple-3: #5b30f6;
  --neon-purple-4: #8054f2;
  
  /* Neon Gradients */
  --neon-gradient-1: linear-gradient(45deg, #7b29cd, #870dd1);
  --neon-gradient-2: linear-gradient(45deg, #870dd1, #5b30f6);
  --neon-gradient-3: linear-gradient(45deg, #5b30f6, #8054f2);
  --neon-gradient-4: linear-gradient(45deg, #8054f2, #7b29cd);
  
  /* Dark Theme Slate */
  --color-slate-900: #0f172a;
  --color-slate-800: #1e293b;
  --color-slate-700: #334155;
  --color-slate-600: #475569;
  --color-slate-400: #94a3b8;
  --color-slate-200: #e2e8f0;
  
  /* Primary Colors */
  --color-primary-dark-navy: #1a1a1a;
  --color-primary-charcoal: #2d2d2d;
  
  /* Text Colors */
  --color-text-primary: #FFFFFF;
  --color-text-secondary: #D1D5DB;
  
  /* Accent Colors */
  --color-accent-red: #FF4516;
  --color-accent-amber: #F59E0B;
  
  /* State Colors */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;
}
```

### 📏 Spacing Variables (8px Grid)

```css
:root {
  /* 8px based spacing system */
  --spacing-0: 0px;
  --spacing-1: 8px;
  --spacing-2: 16px;
  --spacing-3: 24px;
  --spacing-4: 32px;
  --spacing-5: 40px;
  --spacing-6: 48px;
  --spacing-8: 64px;
  --spacing-10: 80px;
  --spacing-12: 96px;
  --spacing-16: 128px;
  
  /* 4px subdivisions for fine-tuning */
  --spacing-0-5: 2px;
  --spacing-1-5: 6px;
  --spacing-2-5: 10px;
  --spacing-3-5: 14px;
}
```

### 🔤 Typography Variables

```css
:root {
  /* Font Sizes */
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-2xl: 24px;
  --font-size-3xl: 30px;
  --font-size-4xl: 36px;
  --font-size-5xl: 48px;
  
  /* Font Weights */
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  
  /* Line Heights */
  --line-height-xs: 16px;
  --line-height-sm: 20px;
  --line-height-base: 24px;
  --line-height-lg: 28px;
  --line-height-xl: 28px;
  --line-height-2xl: 32px;
  --line-height-3xl: 36px;
  
  /* Font Families */
  --font-family-base: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-family-mono: 'Fira Code', 'Monaco', 'Consolas', monospace;
}
```

### 🌟 Effects Variables

```css
:root {
  /* Basic Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  
  /* Neon Glow Effects */
  --shadow-neon-primary: 0 0 20px rgba(91, 48, 246, 0.5);
  --shadow-neon-hover: 0 0 30px rgba(135, 13, 209, 0.6);
  
  /* Card Shadows */
  --shadow-card-default: 0 2px 10px rgba(0,0,0,0.2);
  --shadow-card-hover: 0 8px 20px rgba(123,41,205,0.2);
  
  /* Glow Intensity */
  --glow-subtle: 0 0 5px rgba(123,41,205,0.2);
  --glow-medium: 0 0 10px rgba(123,41,205,0.4);
  --glow-strong: 0 0 15px rgba(123,41,205,0.6);
}
```

### 🧩 Component Variables

```css
:root {
  /* Button Dimensions */
  --btn-height-sm: 32px;
  --btn-height-md: 40px;
  --btn-height-lg: 48px;
  --btn-height-xl: 56px;
  --btn-padding-sm: 8px 12px;
  --btn-padding-md: 12px 20px;
  --btn-padding-lg: 16px 24px;
  
  /* Card Dimensions */
  --card-min-height-base: 320px;
  --card-min-height-game: 380px;
  --card-padding: 24px;
  --card-gap: 16px;
  --radius-card: 16px;
  
  /* Icon Sizes */
  --icon-xs: 12px;
  --icon-sm: 16px;
  --icon-md: 20px;
  --icon-lg: 24px;
  --icon-xl: 32px;
  
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-2xl: 24px;
  --radius-full: 9999px;
}
```

---

## 2. Animation Timing Functions

### ⏱️ Easing Functions

```css
:root {
  /* Standard Easing */
  --ease-linear: linear;
  --ease-in: ease-in;
  --ease-out: ease-out;
  --ease-in-out: ease-in-out;
  
  /* Custom Cubic Bezier */
  --ease-out-smooth: cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --ease-in-quick: cubic-bezier(0.4, 0, 1, 1);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  --ease-elastic: cubic-bezier(0.25, 0.46, 0.45, 0.94);
  
  /* Back Easing */
  --ease-in-back: cubic-bezier(0.6, -0.28, 0.735, 0.045);
  --ease-out-back: cubic-bezier(0.175, 0.885, 0.32, 1.275);
  --ease-in-out-back: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  
  /* Circular Easing */
  --ease-in-circ: cubic-bezier(0.6, 0.04, 0.98, 0.335);
  --ease-out-circ: cubic-bezier(0.075, 0.82, 0.165, 1);
  --ease-in-out-circ: cubic-bezier(0.785, 0.135, 0.15, 0.86);
}
```

### ⏲️ Duration Presets

```css
:root {
  /* Duration Scale */
  --duration-instant: 0.1s;
  --duration-fast: 0.2s;
  --duration-normal: 0.3s;
  --duration-slow: 0.5s;
  --duration-slower: 0.8s;
  --duration-slowest: 1.2s;
  
  /* Transition Presets */
  --transition-fast: 0.15s ease-out;
  --transition-normal: 0.3s ease-out;
  --transition-slow: 0.5s ease-out;
  
  /* Property-specific Transitions */
  --transition-colors: color 0.2s ease, background-color 0.2s ease;
  --transition-transform: transform 0.3s ease-out;
  --transition-shadow: box-shadow 0.3s ease-out;
  --transition-opacity: opacity 0.2s ease;
}
```

### 🎬 Animation Examples

```css
/* Button Hover Animation */
.btn-animated {
  transition: 
    transform var(--duration-fast) var(--ease-out-smooth),
    box-shadow var(--duration-normal) var(--ease-out-smooth),
    background-color var(--duration-fast) var(--ease-out-smooth);
}

.btn-animated:hover {
  transform: scale(1.02);
}

.btn-animated:active {
  transform: scale(0.98);
  transition-duration: var(--duration-instant);
}

/* Card Hover Animation */
.card-animated {
  transition:
    transform var(--duration-normal) var(--ease-out-smooth),
    box-shadow var(--duration-normal) var(--ease-out-smooth);
}

.card-animated:hover {
  transform: translateY(-4px);
}
```

### 🔄 Keyframe Animations

```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes neon-pulse {
  0%, 100% {
    text-shadow: 
      0 0 5px var(--color-accent-red),
      0 0 10px var(--color-accent-red);
  }
  50% {
    text-shadow: 
      0 0 10px var(--color-accent-red),
      0 0 20px var(--color-accent-red),
      0 0 30px var(--color-accent-red);
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}
```

---

## 3. Responsive Breakpoints

### 📱 Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'xs': '0px',     // Mobile (default)
      'sm': '640px',   // Small tablet
      'md': '768px',   // Tablet
      'lg': '1024px',  // Small desktop
      'xl': '1280px',  // Desktop
      '2xl': '1536px', // Large desktop
    },
  },
}
```

### 📐 CSS Variables Breakpoints

```css
:root {
  /* Breakpoint Variables */
  --breakpoint-xs: 0px;
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
  
  /* Device Categories */
  --mobile-max: 767px;
  --tablet-min: 768px;
  --tablet-max: 1023px;
  --desktop-min: 1024px;
}
```

### 📱 Responsive Usage Examples

```css
/* Mobile-first approach */
.responsive-component {
  /* Base mobile styles */
  padding: var(--spacing-2);
  font-size: var(--font-size-sm);
}

/* Tablet and up */
@media (min-width: 768px) {
  .responsive-component {
    padding: var(--spacing-4);
    font-size: var(--font-size-base);
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .responsive-component {
    padding: var(--spacing-6);
    font-size: var(--font-size-lg);
  }
}
```

### 🎯 Tailwind Responsive Classes

```html
<!-- Mobile-first responsive design -->
<div class="
  p-4 text-sm           <!-- Mobile base -->
  md:p-6 md:text-base   <!-- Tablet -->
  lg:p-8 lg:text-lg     <!-- Desktop -->
  xl:p-10 xl:text-xl    <!-- Large desktop -->
">
  Responsive content
</div>

<!-- Grid responsive layout -->
<div class="
  grid grid-cols-1      <!-- Mobile: 1 column -->
  md:grid-cols-2        <!-- Tablet: 2 columns -->
  lg:grid-cols-3        <!-- Desktop: 3 columns -->
  xl:grid-cols-4        <!-- Large: 4 columns -->
  gap-4
">
  <!-- Grid items -->
</div>
```

---

## 4. Component Props Definitions

### 🔧 TypeScript Interfaces

#### Button Component
```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size: 'sm' | 'md' | 'lg' | 'xl';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
}

// Usage example
<Button 
  variant="primary" 
  size="lg" 
  icon={<PlayIcon />}
  iconPosition="left"
  onClick={handlePlay}
>
  Play Game
</Button>
```

#### Card Component
```typescript
interface CardProps {
  variant: 'default' | 'game' | 'feature' | 'stats';
  hover?: boolean;
  padding?: 'sm' | 'md' | 'lg';
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'neon';
  background?: 'slate' | 'gradient' | 'transparent';
  border?: boolean;
  borderGlow?: boolean;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

// Usage example
<Card 
  variant="game" 
  hover={true}
  shadow="neon"
  borderGlow={true}
  onClick={handleCardClick}
>
  <CardContent />
</Card>
```

#### Modal Component
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  size: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  position: 'center' | 'top' | 'bottom';
  backdrop?: 'blur' | 'dark' | 'light';
  closeOnBackdrop?: boolean;
  closeOnEscape?: boolean;
  showCloseButton?: boolean;
  title?: string;
  children: React.ReactNode;
  className?: string;
}
```

#### Input Component
```typescript
interface InputProps {
  type: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  size: 'sm' | 'md' | 'lg';
  variant: 'default' | 'filled' | 'outline';
  state?: 'default' | 'error' | 'success' | 'warning';
  disabled?: boolean;
  readOnly?: boolean;
  placeholder?: string;
  label?: string;
  helperText?: string;
  errorMessage?: string;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  value?: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onFocus?: (event: React.FocusEvent<HTMLInputElement>) => void;
  onBlur?: (event: React.FocusEvent<HTMLInputElement>) => void;
  className?: string;
}
```

#### Navigation Component
```typescript
interface NavigationProps {
  variant: 'sidebar' | 'header' | 'mobile' | 'breadcrumb';
  items: NavigationItem[];
  activeItem?: string;
  onItemClick?: (item: NavigationItem) => void;
  collapsed?: boolean;
  position?: 'fixed' | 'sticky' | 'relative';
  theme?: 'dark' | 'light';
  className?: string;
}

interface NavigationItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  href?: string;
  onClick?: () => void;
  disabled?: boolean;
  children?: NavigationItem[];
  badge?: {
    count: number;
    variant: 'default' | 'success' | 'warning' | 'error';
  };
}
```

### 🎮 Game-Specific Components

#### GameCard Component
```typescript
interface GameCardProps {
  game: {
    id: string;
    title: string;
    description: string;
    image: string;
    category: string;
    difficulty: 'easy' | 'medium' | 'hard';
    duration: number; // in minutes
    players: number;
    rating: number;
    isNew?: boolean;
    isFeatured?: boolean;
    isPremium?: boolean;
  };
  variant: 'compact' | 'detailed' | 'featured';
  showStats?: boolean;
  showActions?: boolean;
  onPlay?: (gameId: string) => void;
  onFavorite?: (gameId: string) => void;
  onShare?: (gameId: string) => void;
  className?: string;
}
```

#### ProgressBar Component
```typescript
interface ProgressBarProps {
  value: number; // 0-100
  max?: number;
  size: 'sm' | 'md' | 'lg';
  variant: 'default' | 'success' | 'warning' | 'error' | 'gradient';
  animated?: boolean;
  showLabel?: boolean;
  showPercentage?: boolean;
  label?: string;
  color?: string;
  backgroundColor?: string;
  className?: string;
}
```

---

## 5. State Transition Diagrams

### 🎯 Game State Transitions

```typescript
// Game State Machine
type GameState = 
  | 'idle'
  | 'loading'
  | 'playing'
  | 'paused'
  | 'completed'
  | 'failed'
  | 'error';

type GameAction = 
  | 'START_GAME'
  | 'PAUSE_GAME'
  | 'RESUME_GAME'
  | 'COMPLETE_GAME'
  | 'FAIL_GAME'
  | 'RESET_GAME'
  | 'ERROR';

// State Transition Logic
const gameStateTransitions = {
  idle: {
    START_GAME: 'loading'
  },
  loading: {
    SUCCESS: 'playing',
    ERROR: 'error'
  },
  playing: {
    PAUSE_GAME: 'paused',
    COMPLETE_GAME: 'completed',
    FAIL_GAME: 'failed',
    ERROR: 'error'
  },
  paused: {
    RESUME_GAME: 'playing',
    RESET_GAME: 'idle'
  },
  completed: {
    RESET_GAME: 'idle'
  },
  failed: {
    RESET_GAME: 'idle'
  },
  error: {
    RESET_GAME: 'idle'
  }
};
```

### 🔐 Authentication State Flow

```typescript
type AuthState = 
  | 'unauthenticated'
  | 'authenticating'
  | 'authenticated'
  | 'error'
  | 'refreshing';

type AuthAction = 
  | 'LOGIN_START'
  | 'LOGIN_SUCCESS'
  | 'LOGIN_FAILURE'
  | 'LOGOUT'
  | 'REFRESH_START'
  | 'REFRESH_SUCCESS'
  | 'REFRESH_FAILURE';

// Authentication State Transitions
const authStateTransitions = {
  unauthenticated: {
    LOGIN_START: 'authenticating'
  },
  authenticating: {
    LOGIN_SUCCESS: 'authenticated',
    LOGIN_FAILURE: 'error'
  },
  authenticated: {
    LOGOUT: 'unauthenticated',
    REFRESH_START: 'refreshing'
  },
  refreshing: {
    REFRESH_SUCCESS: 'authenticated',
    REFRESH_FAILURE: 'unauthenticated'
  },
  error: {
    LOGIN_START: 'authenticating',
    LOGOUT: 'unauthenticated'
  }
};
```

### 🎮 UI Component State Flow

```typescript
// Modal State Transitions
type ModalState = 'closed' | 'opening' | 'open' | 'closing';

type ModalAction = 'OPEN' | 'CLOSE' | 'ANIMATION_COMPLETE';

const modalStateTransitions = {
  closed: {
    OPEN: 'opening'
  },
  opening: {
    ANIMATION_COMPLETE: 'open',
    CLOSE: 'closing'
  },
  open: {
    CLOSE: 'closing'
  },
  closing: {
    ANIMATION_COMPLETE: 'closed',
    OPEN: 'opening'
  }
};

// Form State Transitions
type FormState = 'idle' | 'validating' | 'submitting' | 'success' | 'error';

type FormAction = 
  | 'VALIDATE'
  | 'SUBMIT'
  | 'SUCCESS'
  | 'ERROR'
  | 'RESET';

const formStateTransitions = {
  idle: {
    VALIDATE: 'validating',
    SUBMIT: 'submitting'
  },
  validating: {
    SUBMIT: 'submitting',
    RESET: 'idle'
  },
  submitting: {
    SUCCESS: 'success',
    ERROR: 'error'
  },
  success: {
    RESET: 'idle'
  },
  error: {
    RESET: 'idle',
    SUBMIT: 'submitting'
  }
};
```

### 🔄 Data Loading States

```typescript
// API Request State Machine
type RequestState = 'idle' | 'loading' | 'success' | 'error';

type RequestAction = 'FETCH' | 'SUCCESS' | 'ERROR' | 'RESET';

const requestStateTransitions = {
  idle: {
    FETCH: 'loading'
  },
  loading: {
    SUCCESS: 'success',
    ERROR: 'error'
  },
  success: {
    FETCH: 'loading',
    RESET: 'idle'
  },
  error: {
    FETCH: 'loading',
    RESET: 'idle'
  }
};

// Implementation Example
function useRequestState<T>() {
  const [state, setState] = useState<RequestState>('idle');
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);

  const execute = async (requestFn: () => Promise<T>) => {
    setState('loading');
    setError(null);
    
    try {
      const result = await requestFn();
      setData(result);
      setState('success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setState('error');
    }
  };

  const reset = () => {
    setState('idle');
    setData(null);
    setError(null);
  };

  return { state, data, error, execute, reset };
}
```

---

## 6. Implementation Files Reference

### 📁 File Locations

- **CSS Variables**: `frontend/styles/global.css`
- **Tailwind Config**: `frontend/tailwind.config.js`
- **Animation Guide**: `docs/통합_애니메이션_타이밍_가이드.md`
- **Component Guide**: `docs/통합_컴포넌트_가이드.md`
- **State Transitions**: `docs/통합_상태전환_가이드.md`
- **CSS Variables Guide**: `docs/통합_CSS_Variables_가이드.md`

### 🚀 Getting Started

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm run dev
   ```

3. **Build for Production**
   ```bash
   npm run build
   ```

4. **Run Tests**
   ```bash
   npm test
   ```

### 📋 Development Checklist

- [x] CSS Variables implemented
- [x] Animation timing functions defined
- [x] Responsive breakpoints configured
- [x] Component Props interfaces created
- [x] State transition logic documented
- [x] Tailwind CSS configured
- [x] Typography system established
- [x] Color system implemented
- [x] Spacing system (8px grid) applied
- [x] Component architecture defined

---

## 📞 Support & Documentation

For questions or issues with this specification, refer to:

- Project documentation in `/docs` folder
- Component examples in `/frontend/components`
- Style implementations in `/frontend/styles`
- Figma design system (linked in project)

**Last Updated**: January 26, 2025  
**Version**: 2.0 (Complete English Specification)
