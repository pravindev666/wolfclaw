"""
Phase 14 — Local Vault / Secrets Manager
Encrypted local storage for sensitive values (API keys, passwords, env vars).
"""
import uuid
import json
import hashlib
import base64
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from core import vault as secure_vault

router = APIRouter()

class VaultEntry(BaseModel):
    label: str
    value: str
    category: str = "general"  # general, api_key, password, ssh_key, env_var
    hint: str = ""

@router.post("/vault")
async def add_secret(entry: VaultEntry):
    secret_id = secure_vault.encrypt_secret(
        label=entry.label,
        value=entry.value,
        category=entry.category,
        hint=entry.hint
    )
    return {"id": secret_id, "label": entry.label, "status": "stored"}

@router.get("/vault")
async def list_secrets():
    secrets = secure_vault.list_all_secrets()
    # Filter out provider-based keys if we want a clean general vault list
    # or just show everything. The user said "Looks like dummy", so let's show all.
    return {"secrets": secrets}

@router.get("/vault/{entry_id}")
async def get_secret(entry_id: str):
    sec = secure_vault.decrypt_secret(entry_id)
    if not sec:
        raise HTTPException(status_code=404, detail="Secret not found.")
    return sec

@router.delete("/vault/{entry_id}")
async def delete_secret(entry_id: str):
    success = secure_vault.delete_secret(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Secret not found.")
    return {"status": "deleted"}
