# Alanine Dipeptide — Well-tempered Metadynamics

Classic benchmark: explore the phi/psi Ramachandran landscape of alanine
dipeptide (ACE-ALA-NME) using well-tempered metadynamics.

## System

| Property | Value |
|---|---|
| Molecule | Acetyl-L-Alanyl-N-methylamide (ACE-ALA-NME) |
| Force field | CHARMM36m |
| Solvent | Vacuum (dodecahedron periodic box, 1.5 nm clearance) |
| Temperature | 300 K (V-rescale thermostat) |
| Electrostatics | PME |
| Timestep | 2 fs |
| CVs | φ (phi) and ψ (psi) backbone dihedrals |

## Collective Variable Atom Indices (1-based, PLUMED convention)

After `gmx pdb2gmx` adds hydrogen atoms the atom order is:

```
ACE:  HH31(1) HH32(2) HH33(3) CAY(4) CY(5)  OY(6)
ALA:  N(7)    HN(8)   CA(9)   HA(10) CB(11) HB1(12) HB2(13) HB3(14) C(15) O(16)
NME:  N(17)   HN(18)  CAT(19) HT1(20) HT2(21) HT3(22)

phi = TORSION ATOMS=5,7,9,15    # CY(ACE) – N(ALA) – CA(ALA) – C(ALA)
psi = TORSION ATOMS=7,9,15,17   # N(ALA) – CA(ALA) – C(ALA) – N(NME)
```

## Prerequisites

| Software | Install |
|---|---|
| Python 3.10+ | `conda create -n mda python=3.11` |
| GROMACS 2021+ | [gromacs.org](https://www.gromacs.org/Downloads.html) |
| PLUMED 2.9+ | [plumed.org](https://www.plumed.org) — patch GROMACS: `plumed patch -p` |
| Anthropic API key | `export ANTHROPIC_API_KEY=sk-ant-...` |
| WandB (optional) | `wandb login` |

```bash
# From repo root
pip install -e .
```

## Step 1 — Prepare the System (run once)

```bash
bash prepare.sh
```

This script runs in the current directory (`examples/alanine_dipeptide/`) and
produces:
1. `gmx pdb2gmx` — CHARMM36m topology from `ala2.pdb` (heavy atoms only, `-ignh`)
2. `gmx editconf` — dodecahedron box (1.5 nm from solute to edge)
3. `gmx grompp` + `gmx mdrun` — steepest-descent energy minimization (5000 steps)
4. Copies `em.gro` → `ala2.gro`

Outputs: `ala2.gro` (minimized coordinates) and `topol.top`.

## Step 2 — Run Metadynamics

```bash
# Default (10 ns demo run)
python run_metadynamics.py

# Full 100 ns production run
python run_metadynamics.py --nsteps 50000000

# Custom output directory, no WandB
python run_metadynamics.py --work-dir ./my_run --no-wandb
```

The MD Agent will:
1. Validate the Hydra config
2. Generate `md.mdp` from the Hydra config
3. Generate `plumed.dat` (phi/psi well-tempered metadynamics, WT-bias factor 10)
4. Run `gmx grompp` → `gmx mdrun`
5. Monitor energy and CVs in WandB (background thread)
6. Run `plumed sum_hills` to compute the free energy surface (FES)
7. Return a summary identifying the C7eq, C7ax, and alpha-helix basins

## Expected Output

```
outputs/ala_dipeptide_<timestamp>/
├── md.mdp          # GROMACS MDP file
├── plumed.dat      # PLUMED input (phi/psi WT-metadynamics)
├── topol.tpr       # GROMACS run input
├── md.log          # GROMACS log
├── md.edr          # Energy file
├── md.xtc          # Trajectory (compressed)
├── COLVAR          # phi, psi values vs time
├── HILLS           # Gaussian hill deposition history
└── fes.dat         # Free energy surface (from sum_hills)
```

## Metadynamics Parameters

Configured in `conf/method/ala_metadynamics.yaml`:

| Parameter | Value |
|---|---|
| HILLS height | 1.2 kJ/mol |
| HILLS sigma (each CV) | 0.35 rad |
| Deposition pace | every 500 steps (1 ps) |
| Bias factor | 10 (well-tempered) |
| Simulation length | 5 000 000 steps (10 ns) |

## Analysing the FES

The agent calls `plumed sum_hills` automatically. To reanalyse manually:

```bash
plumed sum_hills --hills outputs/<run>/HILLS --outfile fes.dat --mintozero
```

Plot with Python:

```python
import numpy as np
import matplotlib.pyplot as plt

data = np.loadtxt("outputs/<run>/fes.dat", comments="#")
phi, psi, fes = data[:, 0], data[:, 1], data[:, 2]
# Grid dimensions depend on --bin flag (default 100×100)
n = int(len(phi)**0.5)
F = fes.reshape(n, n)
plt.contourf(phi.reshape(n, n), psi.reshape(n, n), F, levels=30, cmap="RdYlBu_r")
plt.colorbar(label="Free Energy (kJ/mol)")
plt.xlabel("phi (rad)")
plt.ylabel("psi (rad)")
plt.title("Alanine Dipeptide FES")
plt.savefig("ramachandran_fes.png", dpi=150)
```

## Hydra Overrides (main.py)

```bash
# From repo root, override any parameter:
python main.py \
    system=ala_dipeptide \
    method=ala_metadynamics \
    "plumed/collective_variables=ala_dipeptide_cvs" \
    gromacs=ala_vacuum \
    method.nsteps=2000000 \
    method.hills.height=2.0 \
    gromacs.temperature=310
```

## Or via the `mda` CLI

```bash
mda --example ala_dipeptide
```
