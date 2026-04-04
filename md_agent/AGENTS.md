<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# md_agent

## Purpose
Core Python package containing the Claude-powered agentic loop, tool implementations for GROMACS/PLUMED/WandB, Hydra config utilities, and specialist sub-agents. This is the brain of the system — it receives natural-language instructions and autonomously orchestrates MD simulations.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Package init |
| `agent.py` | `MDAgent` class — system prompt, 25 tool definitions (JSON schema), tool dispatch table, and the agentic loop (`run()` / `stream_run()`) |
| `cli.py` | CLI entry point for the `amd` console script |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `agents/` | LangChain specialist sub-agents: paper_config, analysis, cv_suggester (see `agents/AGENTS.md`) |
| `config/` | Hydra utilities and Pydantic validation schemas (see `config/AGENTS.md`) |
| `tools/` | Tool implementations: GROMACS, PLUMED, WandB, paper retrieval (see `tools/AGENTS.md`) |
| `utils/` | Shared utilities: file I/O, parsers, unit conversion (see `utils/AGENTS.md`) |

## For AI Agents

### Working In This Directory
- `agent.py` is the most critical file — the `TOOLS` list and `_handlers` dict **must stay in sync**
- When adding a new tool: add JSON schema to `TOOLS`, implement handler, add to `_handlers` dict
- The system prompt in `agent.py` encodes domain expertise — update it when adding new capabilities
- All tool results are JSON-serialized with `json.dumps(..., default=str)` before returning to Claude

### Testing Requirements
- Each tool module has a corresponding `tests/test_*.py` file
- Tests mock subprocess calls — no GROMACS/PLUMED binaries needed
- Run: `pytest tests/ -v`

### Common Patterns
- Tool handlers return `dict` — serialized to JSON for Claude
- `stream_run()` yields SSE event dicts for the web UI
- `_execute_tool()` catches all exceptions and returns `{"error": ...}` — never crashes the loop

## Dependencies

### Internal
- `conf/` — Hydra config files loaded at startup
- `templates/plumed/` — Jinja2 templates used by `PlumedGenerator`

### External
- `anthropic` — Claude API (messages.create / messages.stream)
- `hydra-core` / `omegaconf` — Config composition
- `langchain` / `langchain-anthropic` — Sub-agent framework

<!-- MANUAL: -->
