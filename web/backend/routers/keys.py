"""API-key management router."""

from __future__ import annotations

import httpx
from fastapi import APIRouter
from pydantic import BaseModel

from web.backend.db import get_api_keys, set_api_key

router = APIRouter()


class SetKeyRequest(BaseModel):
    api_key: str


@router.get("/users/{username}/api-keys")
async def list_api_keys(username: str):
    return {"keys": get_api_keys(username)}


@router.put("/users/{username}/api-keys/{service}")
async def upsert_api_key(username: str, service: str, req: SetKeyRequest):
    set_api_key(username, service, req.api_key)
    return {"updated": True}


@router.post("/users/{username}/api-keys/{service}/verify")
async def verify_api_key(username: str, service: str):
    """Quick-check that a stored API key is valid by making a lightweight API call."""
    keys = get_api_keys(username)
    key = keys.get(service, "")
    if not key:
        return {"valid": False, "error": "No key stored"}

    try:
        if service == "anthropic":
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    "https://api.anthropic.com/v1/models",
                    headers={
                        "x-api-key": key,
                        "anthropic-version": "2023-06-01",
                    },
                )
            return {"valid": r.status_code == 200, "error": None if r.status_code == 200 else f"HTTP {r.status_code}"}

        if service == "openai":
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {key}"},
                )
            return {"valid": r.status_code == 200, "error": None if r.status_code == 200 else f"HTTP {r.status_code}"}

        if service == "deepseek":
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    "https://api.deepseek.com/v1/models",
                    headers={"Authorization": f"Bearer {key}"},
                )
            return {"valid": r.status_code == 200, "error": None if r.status_code == 200 else f"HTTP {r.status_code}"}

        if service == "wandb":
            async with httpx.AsyncClient(timeout=10) as client:
                r = await client.get(
                    "https://api.wandb.ai/auth",
                    headers={"Authorization": f"Bearer {key}"},
                )
            return {"valid": r.status_code == 200, "error": None if r.status_code == 200 else f"HTTP {r.status_code}"}

        return {"valid": False, "error": f"Unknown service: {service}"}

    except Exception as exc:
        return {"valid": False, "error": str(exc)}
