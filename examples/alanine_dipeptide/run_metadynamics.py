"""
Alanine Dipeptide — Well-tempered Metadynamics Example
=======================================================
Run well-tempered metadynamics on alanine dipeptide in vacuum (dodecahedron
periodic box, CHARMM36m force field) using phi and psi dihedral angles as
collective variables.

Prerequisites
-------------
1. GROMACS 2021+ and PLUMED 2.9+ (with GROMACS patch) installed.
2. System prepared with prepare.sh (run once, output stays in this directory):
       bash prepare.sh
   This creates ala2.gro and topol.top here.
3. Python environment: pip install -e ../..  (from repo root)
4. ANTHROPIC_API_KEY exported in environment.
5. Optional: wandb login (for experiment tracking).

Usage
-----
    python run_metadynamics.py [options]

    # Quick 1-ns test:
    python run_metadynamics.py --nsteps 500000

    # Full 100-ns production run:
    python run_metadynamics.py --nsteps 50000000

    # Custom work directory:
    python run_metadynamics.py --work-dir /scratch/my_ala_run
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ── Repo root on sys.path so we can import md_agent without installing ───────
_HERE = Path(__file__).resolve().parent          # examples/alanine_dipeptide/
_REPO_ROOT = _HERE.parents[1]                    # repo root
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra
from omegaconf import OmegaConf

from md_agent.agent import MDAgent

# ── Config ────────────────────────────────────────────────────────────────────

_CONF_DIR = str(_REPO_ROOT / "conf")

ALA_OVERRIDES = [
    "system=ala_dipeptide",
    "method=ala_metadynamics",
    "plumed/collective_variables=ala_dipeptide_cvs",
    "gromacs=ala_vacuum",
]


def build_cfg(work_dir: str, nsteps: int | None):
    GlobalHydra.instance().clear()
    with initialize_config_dir(config_dir=_CONF_DIR, job_name="ala_dipeptide"):
        overrides = ALA_OVERRIDES + [f"run.work_dir={work_dir}"]
        if nsteps is not None:
            overrides.append(f"method.nsteps={nsteps}")
        cfg = compose(config_name="config", overrides=overrides)
    return cfg


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Alanine dipeptide well-tempered metadynamics (CHARMM36m, vacuum)"
    )
    parser.add_argument(
        "--work-dir",
        default=None,
        help="Output directory (default: outputs/ala_dipeptide_<timestamp>)",
    )
    parser.add_argument(
        "--nsteps",
        type=int,
        default=None,
        help="Override number of MD steps (default from config: 5 000 000 = 10 ns)",
    )
    parser.add_argument(
        "--no-wandb",
        action="store_true",
        help="Disable WandB logging",
    )
    args = parser.parse_args()

    # ── Verify system files produced by prepare.sh ───────────────────────────
    gro = _HERE / "ala2.gro"
    top = _HERE / "topol.top"
    if not gro.exists() or not top.exists():
        print(
            "ERROR: system files not found.\n"
            "       Run  bash prepare.sh  first to build the GROMACS system."
        )
        sys.exit(1)

    # ── Set up output directory ──────────────────────────────────────────────
    if args.work_dir is None:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        work_dir = str(_REPO_ROOT / "outputs" / f"ala_dipeptide_{ts}")
    else:
        work_dir = str(Path(args.work_dir).resolve())

    print(f"==> Work directory : {work_dir}")
    print(f"==> System files   : {_HERE}")
    print(f"==> nsteps         : {args.nsteps or 5_000_000}")

    # ── Build Hydra config ───────────────────────────────────────────────────
    cfg = build_cfg(work_dir, args.nsteps)

    if args.no_wandb:
        OmegaConf.update(cfg, "wandb.project", None)

    print("\n==> Resolved config:")
    print(OmegaConf.to_yaml(cfg))

    # ── Copy system files into work_dir ──────────────────────────────────────
    Path(work_dir).mkdir(parents=True, exist_ok=True)
    shutil.copy(gro, Path(work_dir) / "ala2.gro")
    shutil.copy(top, Path(work_dir) / "topol.top")

    # Copy any additional itp files referenced in topol.top
    for itp in _HERE.glob("*.itp"):
        shutil.copy(itp, Path(work_dir) / itp.name)

    # ── Build the natural-language prompt ────────────────────────────────────
    #
    # CHARMM36m atom numbering after pdb2gmx (1-based, PLUMED convention):
    #   ACE: HH31(1) HH32(2) HH33(3) CAY(4) CY(5) OY(6)
    #   ALA: N(7) HN(8) CA(9) HA(10) CB(11) HB1(12) HB2(13) HB3(14) C(15) O(16)
    #   NME: N(17) HN(18) CAT(19) HT1(20) HT2(21) HT3(22)
    #   phi = CY(5) – N(7) – CA(9) – C(15)
    #   psi = N(7)  – CA(9) – C(15) – N_NME(17)
    #
    prompt = (
        "Run a well-tempered metadynamics simulation of alanine dipeptide in vacuum "
        "(CHARMM36m force field, dodecahedron periodic box). "
        f"Work directory: {work_dir}. "
        "Collective variables: "
        "  phi = TORSION ATOMS=5,7,9,15   (CY_ACE – N_ALA – CA_ALA – C_ALA), "
        "  psi = TORSION ATOMS=7,9,15,17  (N_ALA – CA_ALA – C_ALA – N_NME). "
        "All atom indices are 1-based (PLUMED convention). "
        "System files ala2.gro and topol.top are already in the work directory. "
        "Follow this workflow exactly: "
        "1. validate_config — check loaded Hydra config. "
        "2. generate_mdp_from_config → md.mdp. "
        "3. generate_plumed_metadynamics with phi (atoms 5,7,9,15) and psi (atoms 7,9,15,17); "
        "   hills_height=1.2, hills_sigma=[0.35,0.35], hills_pace=500, biasfactor=10, "
        "   temperature=300. "
        "4. run_grompp with md.mdp, topol.top, ala2.gro → topol.tpr. "
        "5. wandb_init_run (skip if wandb.project is null). "
        "6. run_mdrun with topol.tpr and plumed.dat. "
        "7. wandb_start_background_monitor immediately after mdrun starts. "
        "8. wait_mdrun until completion. "
        "9. analyze_hills → compute the free energy surface (FES). "
        "10. wandb_stop_monitor. "
        "11. Summarise the Ramachandran FES: identify the C7eq, C7ax, and alpha-helix basins."
    )

    # ── Run the agent ────────────────────────────────────────────────────────
    agent = MDAgent(cfg=cfg, work_dir=work_dir)
    print("\n==> Starting MD Agent...\n")
    result = agent.run(prompt)
    print("\n==> Agent summary:")
    print(result)


if __name__ == "__main__":
    main()
