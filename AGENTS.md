<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# amd-agent

## Purpose
Claude Opus 4.6-powered agent for autonomous enhanced-sampling molecular dynamics simulations using GROMACS and PLUMED. Supports metadynamics, umbrella sampling, and steered MD — with paper reproduction, real-time WandB monitoring, and a web UI for interactive control.

## Key Files

| File | Description |
|------|-------------|
| `main.py` | Hydra entry point — dispatches `run`, `reproduce_paper`, or `interactive` mode |
| `pyproject.toml` | Project metadata, dependencies, and `amd` / `amd-web` console scripts |
| `requirements.txt` | Pinned dependencies |
| `start.sh` | Quick-start shell script |
| `.env` | Environment variables (ANTHROPIC_API_KEY, etc.) — **never commit secrets** |
| `CLAUDE.md` | Agent coding instructions and architecture reference |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `md_agent/` | Core Python package: agent loop, tools, config, utilities (see `md_agent/AGENTS.md`) |
| `web/` | Full-stack web UI: FastAPI backend + Next.js frontend (see `web/AGENTS.md`) |
| `conf/` | Hydra YAML config groups: method, gromacs, plumed, system, wandb (see `conf/AGENTS.md`) |
| `templates/` | Jinja2 templates for PLUMED `.dat` file generation (see `templates/AGENTS.md`) |
| `data/` | Static data: forcefields, pre-trained models, molecule PDB files (see `data/AGENTS.md`) |
| `tests/` | Pytest test suite — mocked subprocess calls, no binary deps required (see `tests/AGENTS.md`) |
| `gromacs-plumed-docker/` | Docker build for GROMACS+PLUMED container with K8s support (see `gromacs-plumed-docker/AGENTS.md`) |
| `images/` | Screenshots for README documentation |
| `.github/` | CI/CD workflows (ci.yml, release.yml) |
| `notebook/` | Jupyter visualization notebook |

## For AI Agents

### Working In This Directory
- Run `pytest tests/ -v` to validate changes
- Format with `black md_agent/ tests/` and lint with `ruff check md_agent/ tests/`
- The agent uses Hydra — all config is composed from `conf/` YAML files
- The `.env` file must have `ANTHROPIC_API_KEY` set for the agent to function
- Use conda environment `amd` for all Python execution (has torch and other deps)
- **Only GPU 7 is available** — GPUs 0-3 are off-limits

### Testing Requirements
- Tests mock `subprocess.Popen` — no GROMACS/PLUMED binaries needed
- Run full suite: `pytest tests/ -v`
- Run single file: `pytest tests/test_gromacs_tools.py -v`

### Common Patterns
- Hydra `@hydra.main` for CLI config composition
- Claude Anthropic SDK agentic loop with tool use
- `DictConfig` / `OmegaConf` for config manipulation throughout
- Pydantic v2 models for validation at system boundaries

## Dependencies

### External
- `anthropic` — Claude API client (agent core + paper extraction)
- `hydra-core` / `omegaconf` — Configuration management
- `langchain` / `langchain-anthropic` — Specialist sub-agents
- `wandb` — Experiment tracking and monitoring
- `jinja2` — PLUMED template rendering
- `pydantic` — Schema validation
- `pyedr` / `mdtraj` — GROMACS file parsing
- `fastapi` / `uvicorn` — Web backend (optional `[web]` extra)
- `next.js` / `react` / `tailwindcss` — Web frontend

<!-- MANUAL: -->
