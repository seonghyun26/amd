<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# backend

## Purpose
FastAPI application serving the web UI API. Manages browser sessions (each with its own MDAgent), handles JWT authentication, provides REST endpoints for config/files/analysis, and streams agent responses via SSE.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Package init |
| `main.py` | FastAPI app factory — CORS, JWT middleware, router registration, static file serving, `start()` entry point |
| `session_manager.py` | `SessionManager` with LRU-bounded `Session` objects — one `MDAgent` per session, never evicts sessions with active simulations |
| `session_store.py` | Persistent session metadata storage (JSON-backed) |
| `db.py` | Database utilities |
| `jwt_auth.py` | JWT token creation and verification |
| `analysis_utils.py` | Server-side analysis helpers (energy parsing, plotting) |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `routers/` | FastAPI router modules — one per feature area (see `routers/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- Public paths (no auth): `/api/auth/login`, `/health`, `/docs`, file downloads, NGL trajectories
- All other `/api/*` paths require `Authorization: Bearer <jwt>` header
- `SessionManager` uses `OrderedDict` for LRU — oldest idle sessions evicted first
- Sessions with active simulations (`sim_status`) are protected from eviction
- Evicted sessions can be restored from disk transparently
- Hydra config is composed per-session via `_load_hydra_cfg()` with `GlobalHydra.instance().clear()`
- Static frontend served from `web/frontend/out/` — must be built with `next export` first

### Testing Requirements
- `pytest tests/test_web_session.py tests/test_web_config.py -v`
- Mock `MDAgent` and `subprocess` in tests

### Common Patterns
- `@router.post("/api/...")` with Pydantic request/response models
- SSE streaming via `StreamingResponse` with `text/event-stream` content type
- `asyncio.Lock` per session to prevent concurrent agent calls
- `authFetch` on frontend side injects JWT automatically

## Dependencies

### Internal
- `md_agent/agent.py` — Creates `MDAgent` instances per session
- `md_agent/config/` — Hydra config loading
- `md_agent/utils/parsers.py` — Progress parsing

### External
- `fastapi` / `uvicorn` — Web framework
- `python-multipart` — File upload handling
- `matplotlib` — Server-side plot generation

<!-- MANUAL: -->
