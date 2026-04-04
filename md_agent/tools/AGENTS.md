<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# tools

## Purpose
Tool implementations that the Claude agent calls during the agentic loop. Each module wraps an external system (GROMACS, PLUMED, WandB, academic APIs) behind Python methods that accept typed kwargs and return dicts.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Package init |
| `gromacs_tools.py` | `GROMACSRunner` — subprocess wrappers for `grompp`, `mdrun` (non-blocking Popen), `wait_mdrun`, `convert_tpr`, `check_gromacs_energy`, `run_gmx_command`. Supports Docker execution via `GMX_DOCKER_IMAGE` env var. |
| `plumed_tools.py` | `PlumedGenerator` — Jinja2 template rendering for metadynamics, umbrella, steered MD `.dat` files; `validate_plumed_input()` and `analyze_hills()` |
| `wandb_tools.py` | `MDMonitor` (daemon thread for background polling) + module-level helpers: `wandb_init_run`, `wandb_log_from_edr`, `wandb_log_colvar`, `wandb_start_background_monitor`, `wandb_stop_monitor` |
| `paper_tools.py` | `PaperRetriever` (Semantic Scholar + ArXiv search/download) and `MDSettingsExtractor` (nested Claude call to extract MD parameters from paper text as structured JSON) |

## For AI Agents

### Working In This Directory
- **`mdrun` is non-blocking** — `Popen` returns immediately; always call `wandb_start_background_monitor` right after, then `wait_mdrun` to block
- `atexit` handler in `GROMACSRunner` terminates mdrun if Python crashes
- `grompp` stderr is inspected — zero return code with "ERROR" in stderr is reclassified as failure
- `MDMonitor` is a singleton (`_active_monitor`) — only one background monitor at a time
- `MDMonitor` uses mtime guards to skip unchanged files and bookmarks to avoid double-logging
- `PlumedGenerator` uses `StrictUndefined` — missing template variables raise immediately
- `MDSettingsExtractor` makes a nested Claude API call — results go through `normalize_extracted_settings()` for unit conversion

### Testing Requirements
- Tested in `tests/test_gromacs_tools.py`, `test_plumed_tools.py`, `test_wandb_tools.py`, `test_paper_tools.py`
- All subprocess calls mocked — never spawns real GROMACS processes in tests
- Use `tmp_path` for file I/O

### Common Patterns
- Tool methods return `dict` — serialized to JSON by the agent loop
- Docker wrapping: `docker run --rm -w /work -v {work_dir}:/work {image} gmx ...`
- Retry with `tenacity` for Semantic Scholar API (rate-limited)
- `GMXResult` dataclass truncates stdout/stderr to 4000 chars to avoid token bloat

## Dependencies

### Internal
- `md_agent/utils/parsers.py` — File parsing, unit conversion
- `templates/plumed/` — Jinja2 templates for PLUMED generation

### External
- `jinja2` — Template rendering (PLUMED)
- `wandb` — Experiment tracking
- `pyedr` — GROMACS `.edr` file parsing
- `requests` / `tenacity` — HTTP calls to academic APIs
- `pdfplumber` — PDF text extraction
- `anthropic` — Nested Claude call in `MDSettingsExtractor`

<!-- MANUAL: -->
