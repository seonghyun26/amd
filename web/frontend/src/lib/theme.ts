"use client";

import { createContext, useContext } from "react";

export type Theme = "light" | "dark";

export interface ThemeCtx {
  theme: Theme;
  setTheme: (t: Theme) => void;
  toggle: () => void;
}

export const ThemeContext = createContext<ThemeCtx>({
  theme: "dark",
  setTheme: () => {},
  toggle: () => {},
});

export function useTheme() {
  return useContext(ThemeContext);
}

const STORAGE_KEY = "amd-theme";

export function getStoredTheme(): Theme {
  if (typeof window === "undefined") return "dark";
  return (localStorage.getItem(STORAGE_KEY) as Theme) || "dark";
}

export function storeTheme(t: Theme) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, t);
}

/** Apply the theme class to <html> and update CSS variables. */
export function applyTheme(t: Theme) {
  const html = document.documentElement;
  html.classList.remove("light", "dark");
  html.classList.add(t);
  storeTheme(t);
}
