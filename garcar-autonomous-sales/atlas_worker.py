"""ATLAS Discovery Worker — 24/7 target discovery daemon."""
import os, time, json, logging, urllib.request
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] atlas: %(message)s")
logger = logging.getLogger("atlas")

ENGINE_URL = os.getenv("ENGINE_URL", "http://localhost:8080")
POLL_SECONDS = int(os.getenv("ATLAS_POLL_SECONDS", "300"))

SEED_TARGETS = [{
    "lead_id": "LEAD-DFW-901",
    "company_name": "Apex Commercial Roofing",
    "contact_email": "ops@apexroofing-example.com",
    "domain": "apexroofing-example.com",
    "estimated_monthly_leak_usd": 14500,
    "identified_bottlenecks": [
        "Unanswered inbound webhook leads after 5 PM CST",
        "Missing automated follow-up on $18k+ commercial quotes"
    ],
    "dnc_verified": True,
    "confidence_score": 0.94,
    "sku_id": "SKU_REV_AUDIT_2K",
}]

def post_lead(lead):
    data = json.dumps(lead).encode("utf-8")
    req = urllib.request.Request(f"{ENGINE_URL}/api/v1/sales/initiate", data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.error(f"Post failed for {lead.get('lead_id')}: {e}")
        return {"status": "ERROR", "error": str(e)}

def run_once():
    logger.info(f"ATLAS cycle start. Engine={ENGINE_URL}")
    for lead in SEED_TARGETS:
        result = post_lead(lead)
        logger.info(f"Lead {lead['lead_id']} -> {result.get('status')}")
    logger.info("ATLAS cycle complete.")

if __name__ == "__main__":
    logger.info("ATLAS worker starting.")
    while True:
        run_once()
        time.sleep(POLL_SECONDS)
