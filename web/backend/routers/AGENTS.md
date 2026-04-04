<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# routers

## Purpose
FastAPI router modules — one per feature area. Each router defines a set of REST or SSE endpoints under the `/api` prefix. Registered in `web/backend/main.py`.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Package init |
| `auth.py` | `POST /auth/login` — username/password login, returns JWT token |
| `chat.py` | `POST /sessions/{id}/chat` — SSE streaming endpoint; forwards user messages to `MDAgent.stream_run()` and yields real-time events |
| `config.py` | `GET /config/options` — lists available Hydra config presets (methods, systems, gromacs, plumed CVs) |
| `files.py` | File upload/download/listing for session work directories |
| `simulate.py` | Simulation control: start, stop, status, progress polling |
| `analysis.py` | Post-simulation analysis endpoints: energy plots, Ramachandran, COLVAR visualization |
| `trajectory.py` | Trajectory file serving for NGL 3D viewer (`.xtc`, `.gro`) |
| `agents.py` | Specialist agent delegation endpoints |
| `keys.py` | API key management (store/retrieve Anthropic key per user) |
| `server.py` | Server status and health endpoints |

## For AI Agents

### Working In This Directory
- Every router uses `APIRouter(tags=[...])` for OpenAPI grouping
- SSE endpoints return `StreamingResponse(media_type="text/event-stream")`
- Chat router is the most complex — handles SSE event translation from `MDAgent.stream_run()` generator
- File download and NGL trajectory endpoints are public (no JWT) — listed in `_PUBLIC_FRAGMENTS` in `main.py`
- Session ID is a path parameter on most endpoints: `/sessions/{session_id}/...`
- Use `session_manager.get_session()` to retrieve the `Session` object (creates if missing)

### Testing Requirements
- `pytest tests/test_web_config.py tests/test_web_session.py -v`
- Use `httpx.AsyncClient` or FastAPI `TestClient` for endpoint tests
- Mock `MDAgent` to avoid real API calls

### Common Patterns
- `@router.post(...)` / `@router.get(...)` with type-annotated request/response models
- `async with session.lock:` to serialize per-session agent calls
- `StreamingResponse` wrapping async generators for SSE
- JSON response bodies with consistent error format: `{"detail": "..."}`

## Dependencies

### Internal
- `web/backend/session_manager.py` — Session retrieval and lifecycle
- `web/backend/jwt_auth.py` — Token verification (via middleware, not per-router)
- `web/backend/analysis_utils.py` — Plot generation helpers
- `md_agent/agent.py` — `MDAgent` instances accessed through sessions

### External
- `fastapi` — Router, Request, Response classes
- `matplotlib` — Server-side plot rendering (analysis endpoints)

<!-- MANUAL: -->
