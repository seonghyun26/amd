<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# components

## Purpose
React components organized by feature area. Each subdirectory groups related UI components for a specific part of the application.

## Key Files

| File | Description |
|------|-------------|
| `ThemeProvider.tsx` | Dark/light theme context provider |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `agents/` | `AgentModal.tsx` — modal for specialist agent delegation (paper_config, analysis, cv_suggester) |
| `chat/` | Chat panel: `ChatWindow.tsx` (message list), `ChatInput.tsx` (input box + send), `MessageBubble.tsx` (single message), `ThinkingBlock.tsx` (collapsible thinking), `ToolCallCard.tsx` (tool call visualization) |
| `config/` | `ConfigBuilder.tsx` — session configuration form (method, system, gromacs preset selection) |
| `files/` | `FileBrowser.tsx` (directory listing for work_dir), `FileUpload.tsx` (drag-and-drop upload) |
| `sidebar/` | `SessionSidebar.tsx` — left panel with session list, new session button, session deletion |
| `status/` | `SimulationStatus.tsx` — real-time simulation progress display (step, ns/day, ETA) |
| `viz/` | Visualization components: `MoleculeViewer.tsx` (NGL 3D), `TrajectoryViewer.tsx`, `ColvarPlot.tsx`, `EnergyPlot.tsx`, `RamachandranPlot.tsx`, `CVSetupModal.tsx`, `InlineCVPicker.tsx`, `CustomCVResultCard.tsx`, `MiniStructureViewer.tsx` |
| `workspace/` | `MDWorkspace.tsx` (center panel orchestrator), `helpers.ts`, `ui.tsx` (shared workspace UI primitives) |

## For AI Agents

### Working In This Directory
- Each component is a `"use client"` React functional component
- Chat components handle SSE event types from `@/lib/types.ts`: `text_delta`, `thinking`, `tool_start`, `tool_result`, `agent_done`, `error`
- Viz components use NGL for 3D molecular rendering and Plotly for charts
- `MDWorkspace` is the central orchestrator — manages tabs/views for config, file browser, visualization, and simulation status
- All API calls go through `@/lib/api.ts` — never call `fetch` directly

### Common Patterns
- Props interfaces defined above component
- `useSessionStore()` hook for global state access
- Conditional rendering with `&&` and ternary operators
- Tailwind classes with `dark:` variants for theme support
- `lucide-react` icons used throughout

## Dependencies

### Internal
- `@/lib/api.ts` — Backend API calls
- `@/lib/types.ts` — Shared TypeScript types
- `@/store/sessionStore.ts` — Global state

### External
- `ngl` — 3D molecular viewer
- `plotly.js` / `react-plotly.js` — Interactive charts
- `lucide-react` — Icons

<!-- MANUAL: -->
