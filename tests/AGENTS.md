<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# tests

## Purpose
Pytest test suite for all tool modules, config utilities, and web components. Tests mock subprocess calls so no GROMACS/PLUMED binaries are required.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Package init |
| `test_gromacs_tools.py` | Tests for `GROMACSRunner` — grompp, mdrun, wait_mdrun, convert_tpr, energy checks |
| `test_plumed_tools.py` | Tests for `PlumedGenerator` — template rendering, validation, HILLS analysis |
| `test_wandb_tools.py` | Tests for `MDMonitor` and wandb log helpers |
| `test_paper_tools.py` | Tests for `PaperRetriever` and `MDSettingsExtractor` |
| `test_hydra_utils.py` | Tests for MDP generation, config loading/saving, `MDP_KEY_MAP` |
| `test_web_config.py` | Tests for web config API endpoints |
| `test_web_session.py` | Tests for web session management |

## For AI Agents

### Working In This Directory
- Run all: `pytest tests/ -v`
- Run single: `pytest tests/test_gromacs_tools.py::TestMdrun::test_plumed_flag_included -v`
- All subprocess calls are mocked via `pytest-mock` / `unittest.mock`
- Use `tmp_path` fixture for any file I/O in tests
- Tests do NOT require GROMACS, PLUMED, or WandB to be installed

### Testing Requirements
- Every new tool method should have corresponding tests
- Mock external APIs (Semantic Scholar, ArXiv) in paper tool tests
- Use `monkeypatch` for environment variables

### Common Patterns
- `@pytest.fixture` with `tmp_path` for isolated file operations
- `mocker.patch("subprocess.Popen")` / `mocker.patch("subprocess.run")` for GROMACS mocks
- Assert on both return values and side effects (file creation, subprocess args)

## Dependencies

### Internal
- Tests import from `md_agent.tools.*`, `md_agent.config.*`, `md_agent.utils.*`, `web.backend.*`

### External
- `pytest` / `pytest-mock` — Test framework
- `unittest.mock` — Subprocess mocking

<!-- MANUAL: -->
