<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# src

## Purpose
Next.js application source: pages, React components, API client library, state store, and global styles. Organized by feature with a shared `lib/` for cross-cutting utilities.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `app/` | Next.js App Router pages: root layout, main page, login page |
| `components/` | React components organized by feature area (see `components/AGENTS.md`) |
| `lib/` | Shared utilities: API client, auth, SSE, types, theming (see `lib/AGENTS.md`) |
| `store/` | Zustand state stores |

## Key Files in `app/`

| File | Description |
|------|-------------|
| `app/layout.tsx` | Root layout with ThemeProvider and global CSS |
| `app/page.tsx` | Main page — three-panel layout: SessionSidebar, MDWorkspace, ChatWindow |
| `app/login/page.tsx` | Login page with username/password form |
| `app/globals.css` | Tailwind base styles and custom CSS |

## Key Files in `store/`

| File | Description |
|------|-------------|
| `store/sessionStore.ts` | Zustand store — session list, active session, chat messages, sim progress, streaming state; actions for CRUD and SSE event processing |

## For AI Agents

### Working In This Directory
- All components use `"use client"` directive (static export, no RSC)
- Main page layout: sidebar (session list) | center (MD workspace with config/viz/status) | right (collapsible chat panel)
- SSE events from backend are processed in `sessionStore.ts` to update chat messages in real time
- `dynamic(() => import(...), { ssr: false })` for components that use browser-only APIs (NGL, chat)
- Path alias `@/` resolves to `src/`

### Common Patterns
- `SessionSummary` type tracks session metadata including `run_status` and `result_cards`
- Chat messages use a `MessageBlock[]` discriminated union: `text`, `thinking`, `tool_call`, `error`
- Dark mode via `dark:` Tailwind classes throughout

## Dependencies

### Internal
- `lib/api.ts` — All backend communication
- `store/sessionStore.ts` — Global state

### External
- `react` / `next` — Framework
- `zustand` — State management
- `lucide-react` — Icons
- `tailwindcss` — Styling

<!-- MANUAL: -->
