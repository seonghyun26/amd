<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# templates

## Purpose
Jinja2 templates for generating PLUMED and MDP input files. The PLUMED templates are rendered by `PlumedGenerator` with strict variable checking.

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `plumed/` | PLUMED `.dat.jinja2` templates: `metadynamics`, `steered`, `umbrella` |
| `mdp/` | MDP templates (currently empty — MDP generation uses `hydra_utils.py` directly) |

## For AI Agents

### Working In This Directory
- Templates use `StrictUndefined` — every variable **must** be provided in the render context or it will raise immediately
- PLUMED atom indices are **1-based** in all templates
- All templates include `FLUSH STRIDE=100` for real-time monitoring
- Template path is resolved relative to `md_agent/tools/plumed_tools.py` via `Path(__file__).parent.parent.parent / "templates" / "plumed"`

### Testing Requirements
- Template rendering tested in `tests/test_plumed_tools.py`
- Any new template variable must be added to both the template and the corresponding `generate_*` method in `PlumedGenerator`

### Common Patterns
- Jinja2 `trim_blocks` and `lstrip_blocks` enabled for clean output
- CV definitions are passed as list-of-dicts with `name`, `type`, `atoms` keys

## Dependencies

### Internal
- Rendered by `md_agent/tools/plumed_tools.py` (`PlumedGenerator`)

### External
- `jinja2` with `StrictUndefined`

<!-- MANUAL: -->
