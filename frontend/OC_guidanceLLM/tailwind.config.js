// tailwind.config.js
const defaultTheme = require('tailwindcss/defaultTheme');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // ★★★ フォントファミリーを拡張 ★★★
      fontFamily: {
        sans: ['Roboto', ...defaultTheme.fontFamily.sans],
      },
      // ついでにGemini風の色も追加しておくと便利
      colors: {
        'gemini-blue': '#1a73e8',
        'gemini-bg-light': '#f0f4f9',
      }
    },
  },
  plugins: [],
}