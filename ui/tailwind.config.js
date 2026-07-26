/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        terminal: {
          bg: "#0D0D0D",
          surface: "#141414",
          "surface-hover": "#1A1A1A",
          border: "#2A2A2A",
          gain: "#00D4AA",
          loss: "#FF4757",
          warning: "#FFB800",
          neutral: "#808086",
          text: "#FFFFFF",
          "text-secondary": "#AAAAAA",
          "text-tertiary": "#828282",
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', "ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "monospace"],
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Helvetica", "Arial", "sans-serif"],
      },
      borderRadius: {
        none: "0",
        sm: "0",
        DEFAULT: "0",
        md: "0",
        lg: "0",
        xl: "0",
        "2xl": "0",
        "3xl": "0",
      },
      spacing: {
        "1": "4px",
        "2": "8px",
        "3": "12px",
        "4": "16px",
        "6": "24px",
        "8": "32px",
        "12": "48px",
      },
      fontSize: {
        "data-display": ["28px", { lineHeight: "1.0", fontWeight: "600", fontFamily: '"JetBrains Mono", monospace' }],
        "data-body": ["14px", { lineHeight: "1.3", fontFamily: '"JetBrains Mono", monospace' }],
        "data-micro": ["10px", { lineHeight: "1.0", fontFamily: '"JetBrains Mono", monospace' }],
      },
      transitionDuration: {
        "100": "100ms",
        "150": "150ms",
      },
    },
  },
  plugins: [],
};
