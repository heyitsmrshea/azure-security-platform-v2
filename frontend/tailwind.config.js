/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // Design System Colors - Dark Theme Only
      colors: {
        // Backgrounds
        background: {
          primary: '#0F172A',    // Slate 900 - deep navy (main background)
          secondary: '#1E293B',  // Slate 800 - cards/panels
          tertiary: '#334155',   // Slate 700 - borders/dividers
        },
        // Text
        foreground: {
          primary: '#F8FAFC',    // Slate 50 - headings, important text
          secondary: '#94A3B8',  // Slate 400 - labels, descriptions
          muted: '#64748B',      // Slate 500 - timestamps, less important
        },
        // Severity Colors
        severity: {
          critical: '#EF4444',   // Red 500
          high: '#F97316',       // Orange 500
          medium: '#EAB308',     // Yellow 500
          low: '#3B82F6',        // Blue 500
          info: '#6366F1',       // Indigo 500
        },
        // Status Colors
        status: {
          success: '#22C55E',    // Green 500
          warning: '#EAB308',    // Yellow 500
          error: '#EF4444',      // Red 500
          info: '#3B82F6',       // Blue 500
        },
        // Chart Colors
        chart: {
          primary: '#3B82F6',    // Blue 500
          secondary: '#22C55E',  // Green 500
          tertiary: '#8B5CF6',   // Violet 500
          quaternary: '#EC4899', // Pink 500
        },
        // Accent (for interactive elements)
        accent: {
          DEFAULT: '#3B82F6',    // Blue 500
          hover: '#2563EB',      // Blue 600
          muted: '#1E3A5F',      // Darker blue for backgrounds
        },
        // Border/divider colors
        divider: {
          DEFAULT: '#334155',    // Slate 700
          hover: '#475569',      // Slate 600
        },
      },
      // Typography
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        // Large KPIs
        'kpi': ['48px', { lineHeight: '1', fontWeight: '700' }],
        // Section Headers
        'section': ['20px', { lineHeight: '1.4', fontWeight: '600' }],
        // Labels (uppercase)
        'label': ['12px', { lineHeight: '1', fontWeight: '500', letterSpacing: '0.05em' }],
        // Body
        'body': ['14px', { lineHeight: '1.5', fontWeight: '400' }],
      },
      // Spacing for consistent card layouts
      spacing: {
        'card': '24px',
        'card-sm': '16px',
      },
      // Border radius
      borderRadius: {
        'card': '12px',
        'button': '8px',
      },
      // Box shadows (subtle for dark theme)
      boxShadow: {
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -2px rgba(0, 0, 0, 0.2)',
        'card-hover': '0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -4px rgba(0, 0, 0, 0.3)',
      },
      // Animations
      keyframes: {
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'fade-in': 'fade-in 0.3s ease-out',
        'slide-up': 'slide-up 0.3s ease-out',
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
