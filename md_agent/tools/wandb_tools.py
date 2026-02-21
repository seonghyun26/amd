"""WandB logging tools: background monitor thread + explicit log helpers."""

from __future__ import annotations

import threading
from pathlib import Path
from typing import Any, Optional

import wandb

from md_agent.utils.parsers import (
    count_hills,
    get_file_mtime,
    parse_colvar_file,
    parse_edr_with_pyedr,
    parse_gromacs_log_progress,
)


# ── Background monitor ─────────────────────────────────────────────────

class MDMonitor:
    """Daemon thread that periodically tails MD output files and logs to wandb.

    Must be started AFTER ``wandb.init()`` is called.

    Design principles:
    - daemon=True: never prevents interpreter exit
    - Never raises inside the poll loop (logs exceptions as metrics)
    - Uses file mtime guards to skip unchanged files
    - Bookmarks last-seen step/line to avoid double-logging
    """

    def __init__(
        self,
        log_file: str,
        edr_file: str,
        colvar_file: Optional[str] = None,
        hills_file: Optional[str] = None,
        energy_terms: Optional[list[str]] = None,
        poll_interval_s: float = 30.0,
        dt: float = 0.002,  # ps — used to convert COLVAR time→step
    ) -> None:
        self.log_file = str(log_file)
        self.edr_file = str(edr_file)
        self.colvar_file = str(colvar_file) if colvar_file else None
        self.hills_file = str(hills_file) if hills_file else None
        self.energy_terms = energy_terms or [
            "Potential", "Kinetic En.", "Temperature", "Pressure"
        ]
        self.poll_interval = poll_interval_s
        self.dt = dt

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        # Bookmarks
        self._last_edr_step: int = 0
        self._last_colvar_line: int = 0
        self._last_hills_count: int = 0

        # mtime guards
        self._edr_mtime: float = 0.0
        self._colvar_mtime: float = 0.0
        self._hills_mtime: float = 0.0

    def start(self) -> None:
        if wandb.run is None:
            raise RuntimeError("wandb.init() must be called before MDMonitor.start()")
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="MDMonitor",
        )
        self._thread.start()

    def stop(self, final_flush: bool = True) -> None:
        """Signal the monitor to stop and optionally do a final log flush."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=60)
        if final_flush:
            self._do_poll()

    def _monitor_loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                self._do_poll()
            except Exception as exc:
                try:
                    wandb.log({"monitor_error": str(exc)})
                except Exception:
                    pass
            self._stop_event.wait(timeout=self.poll_interval)

    def _do_poll(self) -> None:
        self._poll_edr()
        self._poll_colvar()
        self._poll_hills()
        self._poll_log_progress()

    def _poll_edr(self) -> None:
        mtime = get_file_mtime(self.edr_file)
        if mtime <= self._edr_mtime:
            return
        self._edr_mtime = mtime

        data = parse_edr_with_pyedr(
            self.edr_file,
            terms=self.energy_terms,
            from_step=self._last_edr_step,
        )
        for step, metrics in sorted(data.items()):
            wandb.log({"md_step": step, **metrics})
            self._last_edr_step = max(self._last_edr_step, step)

    def _poll_colvar(self) -> None:
        if not self.colvar_file:
            return
        mtime = get_file_mtime(self.colvar_file)
        if mtime <= self._colvar_mtime:
            return
        self._colvar_mtime = mtime

        rows = parse_colvar_file(self.colvar_file, from_line=self._last_colvar_line)
        for row in rows:
            time_ps = row.get("time", 0.0)
            step = int(time_ps / self.dt)
            cv_data = {k: v for k, v in row.items() if k != "time"}
            wandb.log({"md_step": step, "time_ps": time_ps, **cv_data})
        self._last_colvar_line += len(rows)

    def _poll_hills(self) -> None:
        if not self.hills_file:
            return
        mtime = get_file_mtime(self.hills_file)
        if mtime <= self._hills_mtime:
            return
        self._hills_mtime = mtime

        total = count_hills(self.hills_file)
        if total > self._last_hills_count:
            wandb.log({"hills_deposited": total})
            self._last_hills_count = total

    def _poll_log_progress(self) -> None:
        info = parse_gromacs_log_progress(self.log_file)
        if info and info.get("ns_per_day") is not None:
            wandb.log({"ns_per_day": info["ns_per_day"]})


# ── Singleton monitor handle ───────────────────────────────────────────

_active_monitor: Optional[MDMonitor] = None


# ── Tool functions (called by the Claude agent via tool dispatch) ───────

def wandb_init_run(
    project: str,
    run_name: str,
    config: dict[str, Any],
    entity: Optional[str] = None,
    tags: Optional[list[str]] = None,
    notes: str = "",
    resume: str = "auto",
    input_files: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Initialize a wandb run and log input files as an Artifact."""
    run = wandb.init(
        project=project,
        entity=entity,
        name=run_name,
        config=config,
        tags=tags or [],
        notes=notes,
        resume=resume,
    )

    if input_files:
        artifact = wandb.Artifact(name=f"{run_name}_inputs", type="md_inputs")
        for fpath in input_files:
            if Path(fpath).exists():
                artifact.add_file(fpath)
        wandb.log_artifact(artifact)

    return {
        "run_id": run.id,
        "run_url": run.get_url(),
        "project": project,
        "name": run_name,
    }


def wandb_log_from_edr(
    edr_file: str,
    energy_terms: list[str],
    step_offset: int = 0,
) -> dict[str, Any]:
    """Parse an .edr file and log all energy terms to wandb (explicit call)."""
    data = parse_edr_with_pyedr(edr_file, terms=energy_terms, from_step=step_offset)
    logged = 0
    for step, metrics in sorted(data.items()):
        wandb.log({"md_step": step, **metrics})
        logged += 1
    return {"logged_steps": logged, "last_step": max(data.keys(), default=step_offset)}


def wandb_log_colvar(
    colvar_file: str,
    step_col: str = "time",
    from_step: int = 0,
    dt: float = 0.002,
) -> dict[str, Any]:
    """Parse a PLUMED COLVAR file and log all CV values to wandb."""
    rows = parse_colvar_file(colvar_file, from_line=from_step)
    logged = 0
    for row in rows:
        time_ps = row.get(step_col, 0.0)
        step = int(time_ps / dt)
        cv_data = {k: v for k, v in row.items() if k != step_col}
        wandb.log({"md_step": step, "time_ps": time_ps, **cv_data})
        logged += 1
    return {"logged_rows": logged}


def wandb_start_background_monitor(
    log_file: str,
    edr_file: str,
    colvar_file: Optional[str] = None,
    hills_file: Optional[str] = None,
    energy_terms: Optional[list[str]] = None,
    poll_interval_s: float = 30.0,
    dt: float = 0.002,
) -> dict[str, Any]:
    """Start the background MD monitor thread."""
    global _active_monitor
    if _active_monitor is not None:
        return {"error": "A monitor is already running. Call wandb_stop_monitor first."}

    _active_monitor = MDMonitor(
        log_file=log_file,
        edr_file=edr_file,
        colvar_file=colvar_file,
        hills_file=hills_file,
        energy_terms=energy_terms,
        poll_interval_s=poll_interval_s,
        dt=dt,
    )
    _active_monitor.start()
    return {
        "status": "started",
        "monitoring": {
            "edr": edr_file,
            "colvar": colvar_file,
            "hills": hills_file,
            "poll_interval_s": poll_interval_s,
        },
    }


def wandb_stop_monitor(final_log: bool = True) -> dict[str, Any]:
    """Stop the background monitor, optionally flush remaining data, and finish wandb."""
    global _active_monitor
    if _active_monitor is None:
        return {"status": "no monitor was running"}

    _active_monitor.stop(final_flush=final_log)
    _active_monitor = None
    wandb.finish()
    return {"status": "stopped", "final_flush": final_log}
