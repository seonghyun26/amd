<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# conf

## Purpose
Hydra YAML configuration groups that compose into a single `DictConfig` at runtime. Each subdirectory is a config group with named presets. The root `config.yaml` defines defaults and top-level settings (mode, run, paper).

## Key Files

| File | Description |
|------|-------------|
| `config.yaml` | Root config — defaults composition, mode selection (`run`/`reproduce_paper`/`interactive`), work_dir, paper extraction settings |

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `method/` | Enhanced sampling method presets: `metadynamics`, `umbrella`, `steered`, `plain_md`, `ala_metadynamics` |
| `gromacs/` | GROMACS MDP parameter presets: `default`, `nvt`, `npt`, `tip3p`, `vacuum` |
| `plumed/` | PLUMED settings including `hills.yaml` and `collective_variables/` subgroup |
| `system/` | Molecular system definitions: `protein`, `ala_dipeptide`, `chignolin`, `membrane` |
| `wandb/` | WandB logging configuration |

## For AI Agents

### Working In This Directory
- Hydra composes configs via `defaults:` list in `config.yaml` — order matters
- Keys use underscores (Hydra convention); `MDP_KEY_MAP` in `hydra_utils.py` converts to GROMACS hyphen-keys
- Only keys in `MDP_KEY_MAP` are written to `.mdp` files — adding a new GROMACS param requires updating that map
- Override any value from CLI: `python main.py method=umbrella gromacs.temperature=320`
- `_self_` in defaults list controls merge priority

### Testing Requirements
- Config loading tested in `tests/test_hydra_utils.py`
- Validate YAML syntax before committing

### Common Patterns
- Each config group file can define `_target_name` for display purposes
- `extra_params` dict in method configs allows arbitrary MDP overrides
- System configs define `name`, `topology`, `coordinates`, `forcefield`

## Dependencies

### Internal
- Loaded by `md_agent/config/hydra_utils.py` and `web/backend/session_manager.py`
- Referenced in `main.py` via `@hydra.main(config_path="conf")`

<!-- MANUAL: -->
