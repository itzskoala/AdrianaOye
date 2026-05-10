import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter-tight)', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
      },
      colors: {
        brand: {
          blue:        '#1483F3',
          'blue-dark': '#1170d4',
          'blue-glow': '#c1e5ff',
          'blue-soft': '#ebfaff',
        },
        tag: {
          'purple-bg':  '#f0efff',
          'purple-txt': '#6a60dd',
          'green-bg':   '#eeffe7',
          'green-txt':  '#23a312',
          'pink-bg':    '#fdefff',
          'pink-txt':   '#f258bf',
          'yellow-bg':  '#fffbe8',
          'yellow-txt': '#b07c10',
          'blue-bg':    '#ebfaff',
          'blue-txt':   '#0d7fd1',
          'grey-bg':    '#f0f0f0',
          'grey-txt':   '#666666',
        },
      },
      boxShadow: {
        card: '0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.06)',
        'card-hover': '0 4px 8px rgba(0,0,0,0.06), 0 12px 32px rgba(0,0,0,0.10)',
        float: '0 8px 32px rgba(0,0,0,0.10), 0 2px 8px rgba(0,0,0,0.06)',
      },
      borderRadius: {
        '4xl': '2rem',
      },
      keyframes: {
        'slide-up': { from: { opacity: '0', transform: 'translateY(8px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        'fade-in':  { from: { opacity: '0' }, to: { opacity: '1' } },
        pulse2: { '0%,100%': { opacity: '1' }, '50%': { opacity: '.4' } },
        'bar-fill': { from: { width: '0%' }, to: { width: 'var(--bar-w)' } },
      },
      animation: {
        'slide-up': 'slide-up 0.35s cubic-bezier(0.4,0,0.2,1) both',
        'fade-in':  'fade-in 0.25s ease both',
        pulse2:     'pulse2 1.5s ease-in-out infinite',
        'bar-fill': 'bar-fill 0.7s cubic-bezier(0.4,0,0.2,1) both',
      },
    },
  },
  plugins: [],
}

export default config
