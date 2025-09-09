/** @type {import('tailwindcss').Config} */
// VSCode 확장에서 node_modules 미존재 시 require 실패를 무시하도록 안전 처리
let animatePlugin = null;
try {
  // 컨테이너/CI에서는 정상 로드됨
  animatePlugin = require("tailwindcss-animate");
} catch (_) {
  // 호스트(에디터)에서 의존성 부재 시 no-op 플러그인으로 대체하여 경고 억제
  animatePlugin = function () {
    return function () { /* no-op */ };
  };
}

module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // 사용자 정의 색상
        'neon-pink': '#F6037C',
        'soft-pink': '#EC66A5',
        'light-pink': '#FFBBD3',
        'red-pink': '#FF0D66',
        'crimson': '#C90045',
        'deep-wine': '#450626',
        'dark-purple': '#38041A',
        'mauve': '#8C1B41',
        'light-purple': '#E98BD9',
        'off-white': '#F7F2EF',
        'peach': '#F7D7D2',
        'light-gray': '#D9D9D9',
        'dark-black': '#060103',
        
        // 기존 Tailwind 변수에 대한 매핑
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        premium: {
          DEFAULT: "hsl(var(--premium))",
          foreground: "hsl(var(--premium-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["var(--font-sans)"],
      },
      animation: {
        'neon-pulse': 'neon-pulse 2s infinite',
        'sexy-bounce': 'sexy-bounce 1s ease-in-out infinite',
      },
      keyframes: {
        'neon-pulse': {
          '0%, 100%': {
            boxShadow: '0 0 5px #F6037C, 0 0 10px rgba(246, 3, 124, 0.5)',
          },
          '50%': {
            boxShadow: '0 0 20px #F6037C, 0 0 30px rgba(246, 3, 124, 0.8)',
          },
        },
        'sexy-bounce': {
          '0%, 100%': {
            transform: 'translateY(0)',
          },
          '50%': {
            transform: 'translateY(-10px)',
          },
        },
      },
    },
  },
  plugins: [animatePlugin],
}
