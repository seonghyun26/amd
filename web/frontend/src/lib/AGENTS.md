<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# lib

## Purpose
Shared utility modules for the frontend: API client, authentication, SSE streaming, type definitions, theming, and NGL viewer helpers. Every component imports from here rather than calling browser APIs directly.

## Key Files

| File | Description |
|------|-------------|
| `api.ts` | REST API client — `authFetch()` wrapper (injects JWT), functions for sessions, config, files, analysis, chat, simulation control. **Hot path (29x edits).** |
| `types.ts` | TypeScript type definitions: `SSEEvent` (discriminated union mirroring backend events), `ChatMessage`, `MessageBlock`, `SimProgress`, `SessionConfig`, `ConfigOptions` |
| `auth.ts` | JWT token storage (`localStorage`), `isAuthenticated()`, `getToken()`, `getUsername()`, `logout()` |
| `sse.ts` | SSE client utilities for consuming `text/event-stream` responses |
| `agentStream.ts` | Higher-level agent streaming: connects SSE to Zustand store message updates |
| `ngl.ts` | NGL viewer initialization and helper functions for molecular rendering |
| `theme.ts` | Dark/light mode detection and persistence |
| `colors.ts` | Color palette constants for charts and UI |
| `utils.ts` | General utilities: `uuid()` generator, formatting helpers |

## For AI Agents

### Working In This Directory
- `api.ts` is the **single point of contact** with the backend — all REST calls go through here
- `authFetch()` automatically injects `Authorization: Bearer <jwt>` header
- `types.ts` SSEEvent union must stay in sync with backend SSE event types in `MDAgent.stream_run()`
- `auth.ts` stores JWT in `localStorage` under a fixed key — `isAuthenticated()` checks both token existence and expiry
- `agentStream.ts` processes SSE events and dispatches to Zustand store actions (addBlock, updateBlock, etc.)

### Testing Requirements
- Type-check with `npx tsc --noEmit`
- SSE event types must match backend exactly

### Common Patterns
- `async function name(): Promise<T>` for all API functions
- Error handling: `json<T>()` helper throws on non-ok responses with detail extraction
- `getToken()` returns `string | null` — callers check for null before authenticated operations

## Dependencies

### Internal
- Consumed by all `components/` and `store/sessionStore.ts`

### External
- `ngl` — Molecular viewer library (initialized in `ngl.ts`)

<!-- MANUAL: -->
