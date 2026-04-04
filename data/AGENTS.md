<!-- Parent: ../AGENTS.md -->
<!-- Generated: 2026-04-04 | Updated: 2026-04-04 -->

# data

## Purpose
Static data files used by simulations: GROMACS force field parameter files, pre-trained PyTorch models for collective variable prediction, and molecule structure files (PDB/GRO/TOP).

## Subdirectories

| Directory | Purpose |
|-----------|---------|
| `forcefields/` | CHARMM27 and CHARMM36m force field files (`.itp`, `.atp`, `.rtp`, etc.) |
| `model/` | Pre-trained PyTorch models (`.pt` JIT files) for BBA, chignolin, trp-cage, villin — TAE, TDA, TICA, VDE variants |
| `molecule/` | Molecular structures: alanine dipeptide (PDB), BBA, chignolin (PDB + topology), trp-cage, villin |

## For AI Agents

### Working In This Directory
- These are **read-only reference data** — do not modify force field files
- Molecule PDB files are referenced by system configs in `conf/system/`
- Chignolin has full topology (`.top`, `.gro`, `posre.itp`) ready for simulation
- Model `.pt` files are TorchScript JIT-compiled — load with `torch.jit.load()`
- Force field directories follow GROMACS naming convention (`*.ff/`)

### Common Patterns
- PDB filenames encode conformational state: `*-folded.pdb`, `*-unfolded.pdb`
- Alanine dipeptide has `c5.pdb` and `c7ax.pdb` (named after backbone conformations)

## Dependencies

### Internal
- Referenced by `conf/system/*.yaml` configs
- Used by `GROMACSRunner` during simulation setup

<!-- MANUAL: -->
