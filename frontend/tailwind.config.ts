import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: "#1a3a5c",
          50: "#e8eef5",
          100: "#c5d5e7",
          200: "#9fb9d8",
          300: "#779cc9",
          400: "#5886bd",
          500: "#3a70b1",
          600: "#2e5e9a",
          700: "#234a7e",
          800: "#1a3a5c",
          900: "#0f2238",
        },
        brand: {
          blue: "#2e86ab",
          accent: "#e84855",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      animation: {
        "progress-pulse": "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
    },
  },
  plugins: [],
};

export default config;
