/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae0fd',
          300: '#7cc8fc',
          400: '#38acf8',
          500: '#0e91e9',
          600: '#0273c7',
          700: '#035ca2',
          800: '#074f85',
          900: '#0c426e',
          950: '#082b49',
        },
        cyber: {
          dark: '#030712',
          card: '#0f172a',
          border: '#1e293b',
          glow: '#38bdf8',
          green: '#10b981',
          red: '#ef4444',
          yellow: '#f59e0b',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
