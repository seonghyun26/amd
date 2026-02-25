"""Analysis helpers for plot endpoints. Reuses md_agent parsers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from md_agent.utils.parsers import (
    parse_colvar_file,
    parse_edr_with_pyedr,
    parse_gromacs_log_progress,
)


def colvar_to_columns(colvar_path: str) -> dict[str, list[float]]:
    """Parse COLVAR file and transpose rows → column arrays for Plotly."""
    rows = parse_colvar_file(colvar_path)
    if not rows:
        return {}
    keys = list(rows[0].keys())
    return {k: [r[k] for r in rows] for k in keys}


def fes_dat_to_heatmap(fes_path: str) -> dict[str, Any]:
    """Parse plumed sum_hills fes.dat into {x, y, z} for Plotly heatmap.

    fes.dat format (2D):
        # phi psi file.bias
        -3.14  -3.14  12.5
        -3.14  -3.08  11.2
        ...
        (blank line between phi blocks)

    Returns {"x": [...unique phi...], "y": [...unique psi...], "z": [[...]]}
    """
    if not Path(fes_path).exists():
        return {}

    x_vals: list[float] = []
    y_vals: list[float] = []
    z_vals: list[float] = []

    with open(fes_path) as fh:
        for line in fh:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if len(parts) >= 3:
                try:
                    x_vals.append(float(parts[0]))
                    y_vals.append(float(parts[1]))
                    z_vals.append(float(parts[2]))
                except ValueError:
                    pass

    if not x_vals:
        return {}

    # Build unique sorted axis values
    unique_x = sorted(set(x_vals))
    unique_y = sorted(set(y_vals))

    # Build 2D z matrix: z[i_y][i_x]
    x_idx = {v: i for i, v in enumerate(unique_x)}
    y_idx = {v: i for i, v in enumerate(unique_y)}
    import math
    z_matrix = [[math.nan] * len(unique_x) for _ in range(len(unique_y))]
    for xi, yi, zi in zip(x_vals, y_vals, z_vals):
        ix = x_idx.get(xi)
        iy = y_idx.get(yi)
        if ix is not None and iy is not None:
            z_matrix[iy][ix] = zi

    return {"x": unique_x, "y": unique_y, "z": z_matrix}


def edr_to_timeseries(edr_path: str, terms: list[str] | None = None) -> dict[str, Any]:
    """Parse .edr and return {step: [steps], <term>: [values], ...} for Plotly."""
    default_terms = [
        "Potential Energy", "Kinetic En.", "Total Energy",
        "Temperature", "Pressure",
    ]
    terms = terms or default_terms
    data = parse_edr_with_pyedr(edr_path, terms)
    if not data:
        return {}

    steps = sorted(data.keys())
    result: dict[str, list] = {"step": steps}
    for term in terms:
        result[term] = [data[s].get(term) for s in steps]
    return result


def get_log_progress(log_path: str) -> dict[str, Any]:
    """Return latest step/time/ns_per_day from GROMACS log."""
    info = parse_gromacs_log_progress(log_path)
    return info or {}
