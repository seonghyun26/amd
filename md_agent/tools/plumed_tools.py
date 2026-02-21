"""PLUMED input file generation via Jinja2 templates."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, StrictUndefined

_TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates" / "plumed"


def _make_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
        undefined=StrictUndefined,
    )


class PlumedGenerator:
    """Generates PLUMED input (.dat) files from Hydra config parameters."""

    def __init__(self) -> None:
        self._env = _make_env()

    def _render(self, template_name: str, context: dict[str, Any], output_path: str) -> str:
        template = self._env.get_template(template_name)
        content = template.render(**context)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(content)
        return output_path

    def _build_cv_names(self, cvs: list[dict[str, Any]]) -> str:
        return ",".join(cv["name"] for cv in cvs)

    # ── Public generators ───────────────────────────────────────────────

    def generate_metadynamics(
        self,
        output_path: str,
        cvs: list[dict[str, Any]],
        hills_height: float,
        hills_sigma: list[float],
        hills_pace: int,
        biasfactor: Optional[float] = None,
        temperature: float = 300.0,
        hills_file: str = "HILLS",
        colvar_file: str = "COLVAR",
        colvar_stride: int = 100,
    ) -> dict[str, Any]:
        """Render a PLUMED metadynamics input file.

        Args:
            cvs: List of CV dicts with keys: name, type, atoms (+ optional extras).
            hills_sigma: One sigma value per CV (in CV units).
            biasfactor: Well-tempered bias factor; None for standard metadynamics.
        """
        if len(hills_sigma) != len(cvs):
            return {
                "error": (
                    f"hills_sigma length ({len(hills_sigma)}) must equal "
                    f"number of CVs ({len(cvs)})"
                )
            }

        context = {
            "cvs": cvs,
            "cv_names": self._build_cv_names(cvs),
            "hills_height": hills_height,
            "hills_sigma": hills_sigma,
            "hills_pace": hills_pace,
            "biasfactor": biasfactor,
            "temperature": temperature,
            "hills_file": hills_file,
            "colvar_file": colvar_file,
            "colvar_stride": colvar_stride,
        }
        try:
            path = self._render("metadynamics.dat.jinja2", context, output_path)
            return {"output_path": path, "success": True}
        except Exception as exc:
            return {"error": str(exc), "success": False}

    def generate_umbrella(
        self,
        output_path: str,
        cv_definition: dict[str, Any],
        window_center: float,
        force_constant: float,
        colvar_file: str = "COLVAR",
        colvar_stride: int = 100,
    ) -> dict[str, Any]:
        """Render a PLUMED umbrella sampling restraint file for one window."""
        context = {
            "cv": cv_definition,
            "window_center": window_center,
            "force_constant": force_constant,
            "colvar_file": colvar_file,
            "colvar_stride": colvar_stride,
        }
        try:
            path = self._render("umbrella.dat.jinja2", context, output_path)
            return {"output_path": path, "window_center": window_center, "success": True}
        except Exception as exc:
            return {"error": str(exc), "success": False}

    def generate_steered(
        self,
        output_path: str,
        cv_definition: dict[str, Any],
        initial_value: float,
        final_value: float,
        force_constant: float,
        total_steps: int,
        colvar_file: str = "COLVAR",
        colvar_stride: int = 100,
    ) -> dict[str, Any]:
        """Render a PLUMED steered MD (moving restraint) file."""
        rate = (final_value - initial_value) / total_steps
        context = {
            "cv": cv_definition,
            "initial_value": initial_value,
            "final_value": final_value,
            "force_constant": force_constant,
            "total_steps": total_steps,
            "rate": rate,
            "colvar_file": colvar_file,
            "colvar_stride": colvar_stride,
        }
        try:
            path = self._render("steered.dat.jinja2", context, output_path)
            return {
                "output_path": path,
                "pull_rate_per_step": rate,
                "success": True,
            }
        except Exception as exc:
            return {"error": str(exc), "success": False}

    def validate_plumed_input(
        self,
        plumed_file: str,
        gro_file: Optional[str] = None,
    ) -> dict[str, Any]:
        """Dry-run PLUMED input validation using ``plumed driver --noatoms``.

        If a .gro file is provided, use ``--mf_gro`` for atom-count checks.
        Returns success flag and stderr message.
        """
        cmd = ["plumed", "driver", "--plumed", plumed_file, "--noatoms"]
        if gro_file:
            cmd = ["plumed", "driver", "--plumed", plumed_file, "--mf_gro", gro_file]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {
                "valid": result.returncode == 0,
                "stderr": result.stderr,
                "stdout": result.stdout,
            }
        except FileNotFoundError:
            return {"valid": None, "error": "plumed binary not found in PATH"}
        except subprocess.TimeoutExpired:
            return {"valid": None, "error": "plumed validation timed out"}

    def analyze_hills(
        self,
        hills_file: str,
        output_prefix: str = "fes",
        mintozero: bool = True,
        stride: Optional[int] = None,
    ) -> dict[str, Any]:
        """Run ``plumed sum_hills`` to compute the free energy surface."""
        cmd = [
            "plumed", "sum_hills",
            "--hills", hills_file,
            "--outfile", f"{output_prefix}.dat",
        ]
        if mintozero:
            cmd.append("--mintozero")
        if stride is not None:
            cmd += ["--stride", str(stride)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return {
                "returncode": result.returncode,
                "success": result.returncode == 0,
                "stderr": result.stderr,
                "fes_file": f"{output_prefix}.dat",
            }
        except FileNotFoundError:
            return {"error": "plumed binary not found in PATH"}
        except subprocess.TimeoutExpired:
            return {"error": "plumed sum_hills timed out"}
