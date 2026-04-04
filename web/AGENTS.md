<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# web

## Purpose
Full-stack web application for interactive MD simulation management. FastAPI backend exposes REST + SSE APIs; Next.js frontend provides a three-panel UI (session sidebar, MD workspace, AI chat). Launched via `amd-web` console script.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Package init |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `backend/` | FastAPI app with JWT auth, session management, and 10 router modules (see `backend/AGENTS.md`) |
| `frontend/` | Next.js 14 app with React components, Zustand store, and Tailwind styling (see `frontend/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- Backend runs on port 8000, frontend dev server on port 3000
- Production: frontend is statically exported (`next export`) and served by FastAPI's `StaticFiles`
- CORS origins configured via `AMD_CORS_ORIGINS` env var
- JWT authentication required for all `/api/*` endpoints except `/api/auth/login` and `/health`
- Each browser session maps to one `MDAgent` instance via `SessionManager`

### Testing Requirements
- Backend: `pytest tests/test_web_config.py tests/test_web_session.py -v`
- Frontend: `cd web/frontend && npm test` (if configured)

### Common Patterns
- SSE streaming for real-time agent responses (chat, simulation progress)
- Session-scoped agent instances with LRU eviction
- `authFetch()` wrapper injects JWT on all frontend API calls

## Dependencies

### Internal
- `md_agent/` — Backend creates `MDAgent` instances per session
- `conf/` — Hydra configs loaded for session initialization

### External
- `fastapi` / `uvicorn` — Backend framework
- `next.js` / `react` / `tailwindcss` — Frontend framework
- `zustand` — Frontend state management

<!-- MANUAL: -->
