/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        navy: {
          50:  '#eef2ff',
          100: '#dce6ff',
          200: '#b9ccff',
          300: '#85a3ff',
          400: '#4d72ff',
          500: '#1a44ff',
          600: '#0026f5',
          700: '#001bd4',
          800: '#0d1b6e',
          900: '#0a1245',
          950: '#060b2e',
        },
        cyan: {
          400: '#22d3ee',
          500: '#06b6d4',
        },
      },
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        sans: ['DM Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      backgroundImage: {
        'grid-pattern': `linear-gradient(rgba(34,211,238,0.04) 1px, transparent 1px),
          linear-gradient(90deg, rgba(34,211,238,0.04) 1px, transparent 1px)`,
        'glow-radial': 'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(34,211,238,0.15), transparent)',
      },
      backgroundSize: {
        'grid': '48px 48px',
      },
      boxShadow: {
        'glow-cyan': '0 0 20px rgba(34,211,238,0.15), 0 0 40px rgba(34,211,238,0.05)',
        'glow-navy': '0 0 30px rgba(13,27,110,0.4)',
        'card': '0 1px 1px rgba(0,0,0,0.05), 0 4px 6px rgba(0,0,0,0.08), inset 0 1px 0 rgba(255,255,255,0.06)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
    },
  },
  plugins: [],
};