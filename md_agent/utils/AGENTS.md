<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# utils

## Purpose
Shared utility functions for file I/O, GROMACS/PLUMED output parsing, and unit conversion. Used by both tool modules and the web backend.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Package init |
| `file_utils.py` | `read_file()` (with head/tail support) and `list_files()` (glob-based directory listing) — exposed as agent tools |
| `parsers.py` | `parse_edr_with_pyedr()`, `parse_colvar_file()`, `parse_gromacs_log_progress()`, `count_hills()`, `get_file_mtime()`, `convert_units()`, `normalize_extracted_settings()` |

## For AI Agents

### Working In This Directory
- `normalize_extracted_settings()` converts kcal/mol → kJ/mol and Angstrom → nm **at extraction time** before Pydantic validation
- `parse_gromacs_log_progress()` is used by both `MDMonitor` and `session_manager.py` for progress tracking
- `convert_units()` supports energy (kcal↔kJ) and length (Angstrom↔nm) pairs only
- `read_file()` and `list_files()` are registered as agent tools in `agent.py`

### Testing Requirements
- Parser functions tested indirectly through tool tests
- Unit conversion tested with known conversion factors

### Common Patterns
- File mtime checks (`get_file_mtime`) to avoid re-parsing unchanged files
- `parse_colvar_file()` returns pandas DataFrame from PLUMED COLVAR format
- Settings normalization pops `*_unit` keys and applies conversion in-place

## Dependencies

### Internal
- Used by `md_agent/tools/wandb_tools.py`, `md_agent/tools/paper_tools.py`, `web/backend/session_manager.py`

### External
- `pyedr` — Binary `.edr` file reading
- `pandas` — COLVAR file parsing
- `numpy` — Numerical operations

<!-- MANUAL: -->
