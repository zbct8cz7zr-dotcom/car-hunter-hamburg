/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#1A1D21",
        paper: "#F5F3EE",
        navy: "#152A44",
        amber: "#C8842E",
        good: "#3F6B4E",
        bad: "#A8442F",
      },
      fontFamily: {
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
