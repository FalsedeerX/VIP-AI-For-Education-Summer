// tailwind.config.js
const { fontFamily } = require("tailwindcss/defaultTheme");

module.exports = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",   // ← fixed
    "./src/ui/**/*.{js,ts,jsx,tsx}",
    "./src/styles/**/*.css",
  ],
  theme: {
    extend: {
      colors: {
        "purdue-gold": "#CFB991",
        "purdue-black": "#000000",
      },
      fontFamily: {
        sans: ["ui-sans-serif", ...fontFamily.sans],
      },
    },
  },
  plugins: [],
};
