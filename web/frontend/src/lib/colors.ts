/**
 * Central color palette for AMD.
 * Import from here instead of hardcoding Tailwind color classes.
 */

export const palette = {
  // Brand
  brand: {
    primary:   "blue-600",
    secondary: "indigo-600",
    accent:    "violet-500",
    gradient:  "from-blue-500 to-indigo-600",
  },

  // Surfaces — light / dark pairs (light, dark)
  surface: {
    app:       { light: "gray-50",  dark: "gray-950" },
    sidebar:   { light: "white",    dark: "gray-950" },
    card:      { light: "white",    dark: "gray-900" },
    input:     { light: "white",    dark: "gray-800" },
    elevated:  { light: "gray-100", dark: "gray-800" },
    overlay:   { light: "gray-200", dark: "gray-800" },
  },

  // Borders
  border: {
    subtle:  { light: "gray-200",  dark: "gray-800" },
    default: { light: "gray-300",  dark: "gray-700" },
  },

  // Text
  text: {
    primary:   { light: "gray-900", dark: "gray-100" },
    secondary: { light: "gray-600", dark: "gray-400" },
    muted:     { light: "gray-400", dark: "gray-600" },
    inverse:   { light: "white",    dark: "gray-900" },
  },

  // Status
  status: {
    success:  "emerald-500",
    warning:  "amber-500",
    error:    "red-500",
    info:     "blue-500",
    running:  "green-400",
    paused:   "amber-400",
    finished: "blue-400",
    failed:   "red-500",
    idle:     "gray-600",
  },

  // Interactive
  interactive: {
    hover:     { light: "gray-100",  dark: "gray-800" },
    active:    { light: "gray-200",  dark: "gray-700" },
    focus:     "blue-500",
    danger:    "red-600",
    dangerHv:  "red-500",
  },
} as const;

/** Semantic CSS variable names used in globals.css for theme switching. */
export const cssVars = {
  bg:         "--color-bg",
  bgCard:     "--color-bg-card",
  bgInput:    "--color-bg-input",
  bgElevated: "--color-bg-elevated",
  border:     "--color-border",
  borderSub:  "--color-border-subtle",
  text1:      "--color-text-primary",
  text2:      "--color-text-secondary",
  text3:      "--color-text-muted",
  scrollThumb:    "--color-scroll-thumb",
  scrollThumbHv:  "--color-scroll-thumb-hover",
} as const;
