<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# frontend

## Purpose
Next.js 14 single-page application providing a three-panel UI for interactive MD simulation management: session sidebar (left), MD workspace (center), and AI chat assistant (right). Uses Tailwind CSS for styling and Zustand for state management.

## Key Files

| File | Description |
|------|-------------|
| `package.json` | Dependencies and scripts — `next dev`, `next build`, `next export` |
| `next.config.mjs` | Next.js configuration (static export enabled) |
| `tailwind.config.ts` | Tailwind theme customization |
| `tsconfig.json` | TypeScript configuration |
| `postcss.config.mjs` | PostCSS with Tailwind plugin |
| `watch.mjs` | Dev file watcher for auto-rebuild |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `src/` | Application source code (see `src/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- Dev server: `npm run dev` (port 3000)
- Production build: `npm run build && npx next export` → output in `out/`
- The `out/` directory is served by FastAPI's `StaticFiles` in production
- `"use client"` directive required on all components (no server components in static export)
- Path alias `@/` maps to `src/`

### Testing Requirements
- Type check: `npx tsc --noEmit`
- Lint: check `package.json` for lint scripts

### Common Patterns
- `dynamic(() => import(...), { ssr: false })` for client-only components (chat, NGL viewer)
- `authFetch()` wrapper for all API calls (injects JWT)
- Zustand store with `persist` middleware for session state
- Dark mode support via Tailwind `dark:` variants

## Dependencies

### External
- `next` 14.x — Framework
- `react` 18.x — UI library
- `tailwindcss` — Utility-first CSS
- `zustand` — State management
- `lucide-react` — Icons
- `ngl` — Molecular structure viewer (3D)
- `plotly.js` — Interactive charts

<!-- MANUAL: -->
