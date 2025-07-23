// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#F1F2F3",
        surface: "#FFFFFF",
        primary: "#2E3192",
        secondary: "#C31815",
        accent: "#2A2A2A",
        divider: "rgba(42,42,42,0.1)",
      },
      boxShadow: {
        card: "0px 2px 24px rgba(42, 42, 42, 0.54)",
      },
      borderRadius: {
        lg: "8px",
      },
    },
  },
  plugins: [],
};
