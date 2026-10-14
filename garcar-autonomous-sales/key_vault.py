"""Key-Once Vault — auto-generate internal secrets, store only HMAC.

Raw key is returned once. Subsequent calls return the HMAC only.
Never write the raw key to disk, logs, or proof after first issue.
"""
import os, hmac, hashlib, secrets, json
from pathlib import Path
from typing import Optional

VAULT_PATH = Path(os.getenv("KEY_VAULT_PATH", "/tmp/garcar_key_vault.json"))

class KeyOnceVault:
    def __init__(self, path: Path = VAULT_PATH):
        self.path = path
        self._store = self._load()
    def _load(self):
        if self.path.exists():
            try: return json.loads(self.path.read_text())
            except Exception: return {}
        return {}
    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self._store, indent=2))
        os.chmod(self.path, 0o600)
    def issue(self, name: str) -> dict:
        if name in self._store:
            return {"name": name, "hmac": self._store[name]["hmac"], "issued": False}
        raw = secrets.token_urlsafe(48)
        h = hmac.new(b"garcar-vault", raw.encode(), hashlib.sha256).hexdigest()
        self._store[name] = {"hmac": h, "algo": "HMAC-SHA256"}
        self._save()
        return {"name": name, "raw_key": raw, "hmac": h, "issued": True}
    def verify(self, name: str, raw: str) -> bool:
        entry = self._store.get(name)
        if not entry: return False
        h = hmac.new(b"garcar-vault", raw.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(h, entry["hmac"])
    def get_hmac(self, name: str):
        entry = self._store.get(name)
        return entry["hmac"] if entry else None

def bootstrap_gate_secret() -> str:
    existing = os.getenv("GATE_SIGNING_SECRET")
    if existing and existing != "change_this_to_64_byte_production_secret":
        return existing
    vault = KeyOnceVault()
    result = vault.issue("gate_signing")
    if result.get("issued"):
        os.environ["GATE_SIGNING_SECRET"] = result["raw_key"]
        return result["raw_key"]
    return os.getenv("GATE_SIGNING_SECRET", "")

if __name__ == "__main__":
    vault = KeyOnceVault()
    r = vault.issue("gate_signing")
    print(json.dumps({"name": r["name"], "issued": r["issued"], "hmac": r["hmac"][:16] + "..."}))
    if r.get("issued"):
        print("RAW KEY SHOWN ONCE — store it now. It will not be recoverable.")
