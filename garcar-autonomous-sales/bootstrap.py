"""Bootstrap — auto-mint internal secrets and start the sales engine.

Internal keys (gate signing) are issued once via KeyOnceVault.
External secrets (Stripe, SMTP) remain host-only.
"""
import os, sys
from key_vault import KeyOnceVault

def bootstrap():
    vault = KeyOnceVault()
    gate = vault.issue("gate_signing")
    if gate.get("issued"):
        os.environ["GATE_SIGNING_SECRET"] = gate["raw_key"]
        print(f"[BOOT] gate_signing issued. HMAC={gate['hmac'][:16]}...")
    else:
        print(f"[BOOT] gate_signing already issued. HMAC={gate['hmac'][:16]}...")
    api = vault.issue("internal_api")
    if api.get("issued"):
        os.environ["INTERNAL_API_KEY"] = api["raw_key"]
        print(f"[BOOT] internal_api issued. HMAC={api['hmac'][:16]}...")
    else:
        print(f"[BOOT] internal_api already issued.")
    print(f"[BOOT] GATE set: {bool(os.getenv('GATE_SIGNING_SECRET'))}")
    print(f"[BOOT] STRIPE set: {bool(os.getenv('STRIPE_SECRET_KEY'))}")
    print(f"[BOOT] SMTP set: {bool(os.getenv('SMTP_PASSWORD'))}")
    return True

if __name__ == "__main__":
    bootstrap()
    os.execv(sys.executable, [sys.executable, "-m", "uvicorn", "full_sales_engine:app", "--host", "0.0.0.0", "--port", "8080"])
