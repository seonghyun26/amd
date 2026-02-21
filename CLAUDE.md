# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the agent (default: metadynamics mode)
python main.py

# Override any config param on the command line
python main.py method=umbrella gromacs.temperature=320

# Reproduce a paper
python main.py mode=reproduce_paper paper.arxiv_id=2301.12345

# Interactive REPL
python main.py mode=interactive

# Run all tests
pytest tests/ -v

# Run a single test file or test
pytest tests/test_gromacs_tools.py -v
pytest tests/test_gromacs_tools.py::TestMdrun::test_plumed_flag_included -v

# Format and lint
black md_agent/ tests/
ruff check md_agent/ tests/
```

## Architecture

### Entry point and modes (`main.py`)
Hydra entry point decorated with `@hydra.main`. Reads `cfg.mode` to dispatch:
- `run` — builds a natural-language prompt from the config and calls `agent.run(prompt)`
- `reproduce_paper` — builds a prompt from `cfg.paper.*` (arxiv_id / query / pdf_path / text)
- `interactive` — REPL loop calling `agent.run(user_input)` on each line

### Agent core (`md_agent/agent.py`)
`MDAgent` wraps a Claude Opus 4.6 agentic loop with **25 tools**. Key design:
- Uses `thinking: {"type": "adaptive"}` on every API call
- The `TOOLS` list (JSON schema) and `_handlers` dict (Python callables) are defined in the same file and must stay in sync
- Tool results are JSON-serialised (`json.dumps(..., default=str)`) before being sent back
- The loop continues until `stop_reason == "end_turn"`; all tool calls within a single response are batched and executed before the next API call

### Tool modules
| Module | Class/Functions | Responsibility |
|---|---|---|
| `tools/gromacs_tools.py` | `GROMACSRunner` | Wraps `gmx` subprocess calls. `mdrun` is **non-blocking** (`Popen`); all others block. `atexit` terminates mdrun on crash. |
| `tools/plumed_tools.py` | `PlumedGenerator` | Renders PLUMED `.dat` files via Jinja2 templates in `templates/plumed/`. Uses `StrictUndefined` — all template variables must be present. |
| `tools/wandb_tools.py` | `MDMonitor`, module-level functions | Background daemon thread polls `.edr`/`COLVAR`/`HILLS`/`.log` using mtime guards and logs to wandb. Singleton `_active_monitor` — only one monitor at a time. |
| `tools/paper_tools.py` | `PaperRetriever`, `MDSettingsExtractor` | Fetches papers from Semantic Scholar / ArXiv; uses a nested Claude Opus 4.6 call to extract MD settings as structured JSON. |

### Configuration (`conf/` + `md_agent/config/`)
- Hydra loads `conf/config.yaml` and composites config groups (`method`, `gromacs`, `plumed/collective_variables`, `system`, `wandb`)
- `hydra_utils.py` contains `MDP_KEY_MAP` — the explicit whitelist of Hydra underscore-keys → GROMACS hyphen-keys written to `.mdp` files. Only keys in this map appear in generated MDP files.
- `generate_mdp_from_config()` priority: `extra_params` > `method.nsteps` > `gromacs.*` defaults
- `schemas.py` defines Pydantic v2 models (`CVSchema`, `GromacsSchema`, `MetadynamicsSchema`, etc.) used to validate both Hydra configs and paper-extracted settings

### Output directory
Hydra writes outputs to `outputs/YYYY-MM-DD_HH-MM-SS/` by default (set in `conf/config.yaml` as `run.work_dir`). All GROMACS and PLUMED files go under `work_dir`.

## Critical conventions

- **PLUMED atom indices are 1-based**, not 0-based. This is enforced in the system prompt and must be respected in all CV definitions.
- **`mdrun` is non-blocking** — always call `wandb_start_background_monitor` immediately after `run_mdrun`, then `wait_mdrun` to block for completion.
- **Paper reproduction always requires user confirmation** — `auto_run_after_extract: false` in config; the agent is instructed never to auto-launch multi-hour simulations.
- **`grompp` stderr is inspected** — a zero return code with "ERROR" in stderr is reclassified as failure in `_classify_grompp_output`.
- **Jinja2 templates use `StrictUndefined`** — missing context variables raise immediately rather than silently rendering as empty.
- **Unit normalization happens at extraction time** — `normalize_extracted_settings()` in `parsers.py` converts kcal/mol → kJ/mol and Å → nm before any Pydantic validation.

## Testing approach
Tests mock `subprocess.Popen` (via `pytest-mock`/`unittest.mock`) to avoid requiring GROMACS/PLUMED binaries. Each tool module has a corresponding test file in `tests/`. `tmp_path` pytest fixtures are used for file I/O.
