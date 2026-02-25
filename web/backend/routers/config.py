"""Config endpoints: list available options, update session config."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException
from omegaconf import OmegaConf
from pydantic import BaseModel

from web.backend.session_manager import _repo_conf_dir, get_session

router = APIRouter()


@router.get("/config/options")
async def get_config_options():
    """Return available Hydra config group options."""
    conf_dir = Path(_repo_conf_dir())

    def list_group(subdir: str) -> list[str]:
        d = conf_dir / subdir
        if not d.is_dir():
            return []
        return [f.stem for f in sorted(d.glob("*.yaml"))]

    return {
        "methods": list_group("method"),
        "systems": list_group("system"),
        "gromacs": list_group("gromacs"),
        "plumed_cvs": list_group("plumed/collective_variables"),
    }


class ConfigUpdateRequest(BaseModel):
    updates: dict  # flat or nested dict of overrides


@router.post("/sessions/{session_id}/config")
async def update_session_config(session_id: str, req: ConfigUpdateRequest):
    session = get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    cfg = session.agent.cfg
    OmegaConf.update(cfg, ".", req.updates, merge=True)
    return {"updated": True, "config": OmegaConf.to_container(cfg, resolve=True)}


@router.get("/sessions/{session_id}/config")
async def get_session_config(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    cfg = session.agent.cfg
    return {"config": OmegaConf.to_container(cfg, resolve=True)}
