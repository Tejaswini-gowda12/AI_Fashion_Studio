/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#f2f7f4',
          100: '#e1ede5',
          200: '#c4dcca',
          300: '#9bc2a4',
          400: '#6ea37a',
          500: '#4e865b',
          600: '#3c6b47',
          700: '#31553a',
          800: '#294430',
          900: '#1c3a27',
          950: '#0f1f14',
        },
        sage: {
          50: '#f5f7f5',
          100: '#e6ebe6',
          200: '#cfd8cf',
          300: '#adbcad',
          400: '#8a9a86',
          500: '#6f7f6b',
          600: '#576454',
          700: '#475144',
          800: '#3b4339',
          900: '#323831',
        },
        terracotta: {
          50: '#fbf4f2',
          100: '#f6e7e3',
          200: '#efd2c9',
          300: '#e3b2a2',
          400: '#d58872',
          500: '#c86d51',
          600: '#b45439',
          700: '#96422d',
          800: '#7c3929',
          900: '#673326',
        },
        cream: {
          50: '#fffdfa',
          100: '#f9f7f1',
          200: '#f2eee3',
          300: '#e5decb',
          400: '#d3c6aa',
          500: '#c0af8b',
        },
        charcoal: {
          50: '#f6f7f7',
          100: '#e2e5e5',
          200: '#c5cbcc',
          300: '#9faab0',
          400: '#73838b',
          500: '#53646d',
          600: '#3f4f57',
          700: '#2f3b42',
          800: '#222525',
          850: '#1a1c1e',
          900: '#181a1b',
          950: '#111213',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
