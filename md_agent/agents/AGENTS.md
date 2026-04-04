<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# agents

## Purpose
LangChain-based specialist sub-agents that handle complex, focused tasks delegated by the main `MDAgent`. Each agent has its own system prompt and tool set, runs autonomously, and returns a structured report.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Package init |
| `base.py` | `build_executor()` — shared LangChain `AgentExecutor` factory using Claude Opus 4.6; `stream_executor()` for SSE streaming |
| `paper_agent.py` | `PaperConfigAgent` — extracts MD simulation parameters from published papers |
| `analysis_agent.py` | `AnalysisAgent` — analyzes simulation results: convergence, FES quality, sampling adequacy |
| `cv_agent.py` | `CVAgent` — recommends collective variables based on molecular system and sampling goals |

## For AI Agents

### Working In This Directory
- All agents use `build_executor()` from `base.py` — shared Claude model and prompt pattern
- Agents are invoked via `delegate_to_specialist` tool in the main agent loop
- Each agent defines its own `tools` list (LangChain tools, not raw JSON schemas)
- `stream_executor()` converts LangChain `astream_events` to the SSE event dict format used by the web UI
- Temperature is set to 1 (Claude default) with max_tokens=8192

### Testing Requirements
- Mock the Anthropic API client in tests
- Test agent output parsing, not LLM responses

### Common Patterns
- `ChatPromptTemplate.from_messages([("system", ...), ("human", "{input}"), ("placeholder", "{agent_scratchpad}")])` pattern
- `AgentExecutor` with `max_iterations=12` and `return_intermediate_steps=True`
- Lazy imports in `MDAgent._delegate_to_specialist()` to avoid circular deps

## Dependencies

### Internal
- `md_agent/tools/` — Paper and analysis agents reuse tool implementations
- `md_agent/utils/parsers.py` — Unit normalization for extracted settings

### External
- `langchain` / `langchain-anthropic` / `langchain-core` — Agent framework
- `anthropic` — Underlying model API

<!-- MANUAL: -->
