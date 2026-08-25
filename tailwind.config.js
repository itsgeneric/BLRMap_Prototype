/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          500: '#0284c7',
          600: '#0369a1',
        },
        shortest: '#a3e635',
        traffic: '#f472b6',
        inner: '#fbbf24',
        twowheeler: '#60a5fa',
        combined: '#c084fc',
      },
      fontFamily: {
        mono: ['var(--font-ibm-mono)', 'monospace'],
        sans: ['var(--font-ibm-sans)', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
