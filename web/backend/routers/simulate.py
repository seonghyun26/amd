"""Direct simulation launcher — grompp + mdrun via Docker, no AI."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from omegaconf import OmegaConf

from web.backend.session_manager import get_session

router = APIRouter()

_COORD_EXTS = {".gro", ".pdb"}
_TOP_EXTS = {".top"}

# Subfolder within work_dir where mdrun writes its output files
_SIM_SUBDIR = "simulation"


def _find_file(work_dir: Path, extensions: set[str], preferred: str = "") -> str | None:
    if preferred and (work_dir / preferred).exists():
        return preferred
    for f in sorted(work_dir.iterdir()):
        if f.is_file() and f.suffix.lower() in extensions:
            return f.name
    return None


def _topology_has_molecules(top_path: Path) -> bool:
    """Return True only if the topology file has a populated [ molecules ] section."""
    try:
        if top_path.stat().st_size == 0:
            return False
        in_mol_section = False
        for line in top_path.read_text().splitlines():
            s = line.strip()
            if s.startswith("[") and "molecules" in s.lower():
                in_mol_section = True
                continue
            if s.startswith("[") and in_mol_section:
                break  # entered a new section — no molecules found
            if in_mol_section and s and not s.startswith(";"):
                return True  # found at least one non-comment molecule entry
    except Exception:
        pass
    return False


@router.post("/sessions/{session_id}/simulate")
async def start_simulation(session_id: str):
    """Generate MDP, run grompp, then launch mdrun in Docker — no AI involved.

    All GROMACS steps run with work_dir bind-mounted at /work inside the
    Docker container.  mdrun output files are written to work_dir/simulation/.
    """
    session = get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    work_dir = Path(session.work_dir)
    cfg = session.agent.cfg
    gmx = session.agent._gmx

    # 1. Generate md.mdp from current config
    from md_agent.config.hydra_utils import generate_mdp_from_config
    generate_mdp_from_config(cfg, str(work_dir / "md.mdp"))

    # 2. Find coordinate file (prefer system.coordinates, fall back to any .gro/.pdb)
    preferred_coord = OmegaConf.select(cfg, "system.coordinates") or ""
    coord_file = _find_file(work_dir, _COORD_EXTS, preferred_coord)
    if not coord_file:
        raise HTTPException(400, "No coordinate file (.gro or .pdb) found in session directory.")

    # 3. Find topology — re-run pdb2gmx if missing or empty (no molecules defined)
    preferred_top = OmegaConf.select(cfg, "system.topology") or ""
    top_file = _find_file(work_dir, _TOP_EXTS, preferred_top)

    needs_pdb2gmx = (
        not top_file
        or not _topology_has_molecules(work_dir / top_file)
    )

    if needs_pdb2gmx:
        forcefield  = OmegaConf.select(cfg, "system.forcefield")  or "amber99sb-ildn"
        water_model = OmegaConf.select(cfg, "system.water_model") or "none"

        def _run_pdb2gmx(ff: str) -> dict:
            return gmx.run_gmx_command(
                "pdb2gmx",
                ["-f", coord_file, "-o", "system.gro", "-p", "topol.top",
                 "-ff", ff, "-water", water_model, "-ignh"],
                work_dir=str(work_dir),
            )

        result = _run_pdb2gmx(forcefield)

        # If the configured force field doesn't define the residue (e.g. charmm27
        # lacks NME/ACE capping groups), fall back to amber99sb-ildn automatically.
        if result["returncode"] != 0:
            stderr = result.get("stderr", "")
            if "not found in residue topology database" in stderr and forcefield != "amber99sb-ildn":
                result = _run_pdb2gmx("amber99sb-ildn")
                if result["returncode"] == 0:
                    # Keep the session config in sync with the force field that worked
                    from omegaconf import OmegaConf as _OC
                    _OC.update(cfg, "system.forcefield", "amber99sb-ildn", merge=True)
                    forcefield = "amber99sb-ildn"

        if result["returncode"] != 0:
            raise HTTPException(500, f"pdb2gmx failed:\n{result.get('stderr', '')[-2000:]}")
        top_file   = "topol.top"
        coord_file = "system.gro"

    # 4. grompp → md.tpr (stays in work_dir root)
    index_file = OmegaConf.select(cfg, "system.index") or None
    has_index  = index_file and (work_dir / index_file).exists()
    grompp = gmx.grompp(
        mdp_file="md.mdp",
        topology_file=top_file,
        coordinate_file=coord_file,
        output_tpr="md.tpr",
        index_file=index_file if has_index else None,
        max_warnings=5,
    )
    if not grompp["success"]:
        raise HTTPException(500, f"grompp failed:\n{grompp.get('stderr', '')[-2000:]}")

    # 5. Create simulation output subfolder and launch mdrun (non-blocking)
    sim_dir = work_dir / _SIM_SUBDIR
    sim_dir.mkdir(exist_ok=True)
    output_prefix = f"{_SIM_SUBDIR}/md"
    mdrun = gmx.mdrun(tpr_file="md.tpr", output_prefix=output_prefix)

    return {
        "status": "running",
        "pid": mdrun["pid"],
        "expected_files": mdrun["expected_files"],
    }


@router.get("/sessions/{session_id}/simulate/status")
async def simulation_status(session_id: str):
    """Check whether mdrun is currently running for this session."""
    from web.backend.session_manager import get_simulation_status
    return get_simulation_status(session_id)


@router.post("/sessions/{session_id}/simulate/stop")
async def stop_simulation(session_id: str):
    """Terminate a running mdrun process."""
    from web.backend.session_manager import stop_session_simulation
    stopped = stop_session_simulation(session_id)
    return {"stopped": stopped}
