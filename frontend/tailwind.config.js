/** @type {import('tailwindcss').Config} */
const defaultTheme = require('tailwindcss/defaultTheme');

module.exports = {
  // Paths are relative to the project root, where npm scripts run.
  content: [
    './templates/**/*.html',
    './website/**/*.py',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        aether: {
          bg: '#0b0e14',
          surface: '#131722',
          panel: '#1a1f2c',
          accent: '#7c5cff',
          accent2: '#22d3ee',
        },
      },
      fontFamily: {
        display: ['Unbounded', ...defaultTheme.fontFamily.sans],
        sans: ['"Golos Text"', ...defaultTheme.fontFamily.sans],
        mono: ['"JetBrains Mono"', ...defaultTheme.fontFamily.mono],
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
