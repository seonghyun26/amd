<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# config

## Purpose
Hydra configuration utilities and Pydantic validation schemas. Handles MDP file generation from Hydra configs, config loading/saving, and validates both user-provided and paper-extracted simulation parameters.

## Key Files

| File | Description |
|------|-------------|
| `__init__.py` | Package init — re-exports key functions |
| `hydra_utils.py` | `MDP_KEY_MAP` (underscore→hyphen whitelist), `generate_mdp_from_config()`, `load_config()`, `save_config()` |
| `schemas.py` | Pydantic v2 models: `CVSchema`, `MetadynamicsSchema`, `UmbrellaSchema`, `GromacsSchema`, etc.; `validate_extracted_settings()` |

## For AI Agents

### Working In This Directory
- `MDP_KEY_MAP` is the **single source of truth** for which Hydra keys become MDP parameters — adding a new GROMACS setting requires updating this dict
- MDP generation priority: `extra_params` > `method.nsteps` > `gromacs.*` defaults
- List-valued MDP keys (`tc_grps`, `tau_t`, `ref_t`) are space-joined automatically
- Pydantic schemas validate at system boundaries (paper extraction, web API) — internal code trusts the Hydra config
- `CV_TYPES = {"DISTANCE", "TORSION", "ANGLE", "RMSD", "COORDINATION"}` — exhaustive set

### Testing Requirements
- Tested in `tests/test_hydra_utils.py`
- Test MDP output format, key mapping, and priority resolution
- Test schema validation with valid and invalid inputs

### Common Patterns
- `OmegaConf.to_container(cfg, resolve=True)` to convert DictConfig to plain dict
- `field_validator` / `model_validator` for cross-field constraints (e.g., RMSD requires reference)
- `validate_extracted_settings()` returns `(bool, list[str])` — ok flag + error messages

## Dependencies

### Internal
- Consumed by `md_agent/agent.py` (tool handlers), `web/backend/session_manager.py`
- Reads from `conf/` YAML files via Hydra

### External
- `hydra-core` / `omegaconf` — Config composition and manipulation
- `pydantic` v2 — Schema validation

<!-- MANUAL: -->
