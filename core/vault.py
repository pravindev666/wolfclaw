import os
import base64
import json
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

VAULT_DIR = Path("data/vault")
VAULT_DIR.mkdir(parents=True, exist_ok=True)
KEY_FILE = VAULT_DIR / ".master.key"
VAULT_FILE = VAULT_DIR / "secrets.enc"

def _generate_master_key():
    """Generates a master key derived from machine-specific identifiers (simulated as simple for now)."""
    # In a production-grade 'Sovereign OS', we would use TPM or OS Keyring
    # For now, we generate a random key once if not present.
    if not KEY_FILE.exists():
        key = AESGCM.generate_key(bit_length=256)
        with open(KEY_FILE, "wb") as f:
            f.write(base64.b64encode(key))
    
    with open(KEY_FILE, "rb") as f:
        return base64.b64decode(f.read())

def _load_vault_file():
    if not VAULT_FILE.exists():
        return {}
    try:
        with open(VAULT_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def _save_vault_file(secrets):
    with open(VAULT_FILE, "w") as f:
        json.dump(secrets, f)

def encrypt_secret(label: str, value: str, category: str = "general", hint: str = "", secret_id: str = None):
    """Encrypts and stores a generic secret in the vault."""
    if not secret_id:
        import uuid
        secret_id = str(uuid.uuid4())[:8]
        
    master_key = _generate_master_key()
    aesgcm = AESGCM(master_key)
    nonce = os.urandom(12)
    
    # Authenticated Data for integrity
    aad = f"{secret_id}|{category}".encode()
    encrypted = aesgcm.encrypt(nonce, value.encode(), aad)
    
    secrets = _load_vault_file()
    secrets[secret_id] = {
        "label": label,
        "category": category,
        "hint": hint,
        "nonce": base64.b64encode(nonce).decode('utf-8'),
        "data": base64.b64encode(encrypted).decode('utf-8')
    }
    _save_vault_file(secrets)
    return secret_id

def decrypt_secret(secret_id: str) -> dict:
    """Decrypts and returns a specific secret with its metadata."""
    secrets = _load_vault_file()
    if secret_id not in secrets:
        return None
        
    try:
        master_key = _get_master_key_cached()
        secret = secrets[secret_id]
        nonce = base64.b64decode(secret["nonce"])
        encrypted_data = base64.b64decode(secret["data"])
        
        category = secret.get("category", "general")
        aad = f"{secret_id}|{category}".encode()
        
        aesgcm = AESGCM(master_key)
        decrypted = aesgcm.decrypt(nonce, encrypted_data, aad)
        
        return {
            "id": secret_id,
            "label": secret["label"],
            "category": category,
            "value": decrypted.decode('utf-8'),
            "hint": secret.get("hint", "")
        }
    except Exception as e:
        print(f"VAULT ERROR: Failed to decrypt {secret_id}: {e}")
        return None

def delete_secret(secret_id: str):
    """Removes a secret from the vault."""
    secrets = _load_vault_file()
    if secret_id in secrets:
        del secrets[secret_id]
        _save_vault_file(secrets)
        return True
    return False

def list_all_secrets():
    """Returns all secrets (metadata only) from the vault."""
    secrets = _load_vault_file()
    return [
        {
            "id": k,
            "label": v.get("label", k.replace("provider_", "").capitalize()),
            "category": v.get("category", "general"),
            "hint": v.get("hint", "")
        }
        for k, v in secrets.items()
    ]

# Maintain legacy provider-based helpers for llm_engine
def encrypt_key(provider: str, key_value: str):
    """Bridge function for provider-based keys."""
    return encrypt_secret(provider, key_value, category="api_key", secret_id=f"provider_{provider}")

def decrypt_key(provider: str) -> str:
    """Bridge function for provider-based keys."""
    sec = decrypt_secret(f"provider_{provider}")
    return sec["value"] if sec else ""

_master_key_cache = None
def _get_master_key_cached():
    global _master_key_cache
    if _master_key_cache is None:
        _master_key_cache = _generate_master_key()
    return _master_key_cache

def list_vaulted_providers():
    """Returns a list of providers that have keys in the vault."""
    secrets = _load_vault_file()
    return [k.replace("provider_", "") for k in secrets.keys() if k.startswith("provider_")]
