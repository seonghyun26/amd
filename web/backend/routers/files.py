"""File management endpoints: upload, list, download."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse

from md_agent.utils.file_utils import list_files
from web.backend.session_manager import get_session

router = APIRouter()


@router.get("/sessions/{session_id}/files")
async def list_session_files(session_id: str, pattern: str = "*", recursive: bool = True):
    session = get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    files = list_files(session.work_dir, pattern=pattern, recursive=recursive)
    return {"files": files, "work_dir": session.work_dir}


@router.post("/sessions/{session_id}/files/upload")
async def upload_file(session_id: str, file: UploadFile):
    session = get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    dest = Path(session.work_dir) / (file.filename or "upload")
    dest.parent.mkdir(parents=True, exist_ok=True)
    content = await file.read()
    dest.write_bytes(content)
    return {"saved_path": str(dest), "size_bytes": len(content)}


@router.get("/sessions/{session_id}/files/download")
async def download_file(session_id: str, path: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    # Safety: resolve and ensure path is within work_dir
    work = Path(session.work_dir).resolve()
    target = Path(path).resolve()
    if not str(target).startswith(str(work)):
        raise HTTPException(403, "Path outside session work directory")
    if not target.exists():
        raise HTTPException(404, "File not found")

    return FileResponse(str(target), filename=target.name)
