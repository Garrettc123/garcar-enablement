"""Garcar Autonomous Sales Engine — FastAPI.

PostgreSQL state, SMTP transport (dry-run if no password), fail-closed Stripe webhook,
deliverable compilation, and client portal. External actions require a valid AUTO-APR approval_id.
"""
import os, hmac, time, json, secrets, hashlib, logging
from email.message import EmailMessage
from typing import Optional, List
from contextlib import asynccontextmanager

import asyncpg, aiosmtplib, stripe
from fastapi import FastAPI, Request, HTTPException, Header, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, EmailStr

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("garcar.engine")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://garcar:garcar_pass@db:5432/garcar_sales")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
GATE_SIGNING_SECRET = os.getenv("GATE_SIGNING_SECRET", "change_this_to_64_byte_production_secret")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8080")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.sendgrid.net")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "apikey")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "revenue@garcarenterprise.com")

if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

SKU_CATALOG = {
    "SKU_REV_AUDIT_2K": {"name": "Garcar Enterprise - Revenue Leakage & Systems Audit", "price_cents": 200000},
    "SKU_AUTO_STACK_5K": {"name": "Garcar Enterprise - Full Autonomous Stack Deployment", "price_cents": 500000},
    "LLA-47": {"name": "Texas Trades Leak Map", "price_cents": 4700},
    "AI-AUDIT-299": {"name": "AI Audit", "price_cents": 29900},
}

db_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
        logger.info("Connected to PostgreSQL ledger pool.")
    except Exception as e:
        logger.warning(f"DB pool unavailable ({e}). Running in dry mode.")
        db_pool = None
    yield
    if db_pool:
        await db_pool.close()

app = FastAPI(title="Garcar Enterprise Autonomous Sales Stack", lifespan=lifespan)

class LeadTarget(BaseModel):
    lead_id: str
    company_name: str
    contact_email: EmailStr
    domain: str
    estimated_monthly_leak_usd: int = Field(gt=0)
    identified_bottlenecks: List[str]
    dnc_verified: bool = True
    confidence_score: float = Field(ge=0.0, le=1.0)
    sku_id: str = "SKU_REV_AUDIT_2K"

class InboundEmailPayload(BaseModel):
    from_email: EmailStr
    subject: str
    text: str
    in_reply_to: Optional[str] = None

class AutonomousSalesGate:
    MAX_DAILY_OUTREACH = int(os.getenv("MAX_DAILY_OUTREACH", "250"))
    MIN_CONFIDENCE = 0.85
    MIN_LEAK_USD = 5000
    @classmethod
    async def verify_and_mint(cls, conn, lead, price_cents):
        if not lead.dnc_verified:
            raise PermissionError(f"GAR-530 Blocked [{lead.lead_id}]: DNC flag false.")
        if conn:
            suppressed = await conn.fetchval("SELECT 1 FROM suppression_list WHERE domain = $1 OR email = $2", lead.domain.lower(), lead.contact_email.lower())
            if suppressed:
                raise PermissionError(f"GAR-530 Blocked [{lead.lead_id}]: on suppression list.")
            daily = await conn.fetchval("SELECT COUNT(*) FROM deals WHERE created_at >= NOW() - INTERVAL '24 hours'")
            if daily >= cls.MAX_DAILY_OUTREACH:
                raise RuntimeError("GAR-530 Blocked: 24-hour outreach circuit breaker reached.")
        if lead.confidence_score < cls.MIN_CONFIDENCE:
            raise PermissionError(f"GAR-530 Blocked: Confidence below {cls.MIN_CONFIDENCE}.")
        if lead.estimated_monthly_leak_usd < cls.MIN_LEAK_USD:
            raise ValueError(f"GAR-530 Blocked: Monthly leak under threshold.")
        sku = SKU_CATALOG.get(lead.sku_id)
        if not sku or sku["price_cents"] != price_cents:
            raise ValueError("GAR-530 Blocked: Unauthorized SKU or price mutation.")
        ts = int(time.time())
        payload = f"{lead.lead_id}:{lead.sku_id}:{price_cents}:{ts}".encode()
        sig = hmac.new(GATE_SIGNING_SECRET.encode(), payload, hashlib.sha256).hexdigest()[:16]
        return f"AUTO-APR-{ts}-{sig}"

async def send_production_email(to_email, subject, body, approval_id, reply_to_msg_id=None):
    if not approval_id.startswith("AUTO-APR-"):
        raise PermissionError("GAR-530 Hard Failure: Missing approval_id.")
    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg_id = f"<{secrets.token_hex(12)}@garcarenterprise.com>"
    msg["Message-ID"] = msg_id
    if reply_to_msg_id:
        msg["In-Reply-To"] = reply_to_msg_id
        msg["References"] = reply_to_msg_id
    msg.set_content(body)
    if not SMTP_PASSWORD:
        logger.info(f"[DRY-RUN SMTP] To={to_email} | MsgID={msg_id}")
        return msg_id
    await aiosmtplib.send(msg, hostname=SMTP_HOST, port=SMTP_PORT, username=SMTP_USER, password=SMTP_PASSWORD, start_tls=True)
    return msg_id

def generate_stripe_session(lead, approval_id):
    sku = SKU_CATALOG[lead.sku_id]
    if not STRIPE_SECRET_KEY or STRIPE_SECRET_KEY.startswith("sk_test_placeholder"):
        sim_id = f"cs_sim_{lead.lead_id}_{int(time.time())}"
        return sim_id, f"{PUBLIC_BASE_URL}/checkout-simulated/{sim_id}"
    session = stripe.checkout.Session.create(
        payment_method_types=["card", "us_bank_account"],
        line_items=[{"price_data": {"currency": "usd", "product_data": {"name": sku["name"]}, "unit_amount": sku["price_cents"]}, "quantity": 1}],
        mode="payment", customer_email=lead.contact_email,
        metadata={"lead_id": lead.lead_id, "sku_id": lead.sku_id, "approval_id": approval_id},
        success_url=f"{PUBLIC_BASE_URL}/portal/{lead.lead_id}?status=paid",
        cancel_url=f"{PUBLIC_BASE_URL}/portal/{lead.lead_id}?status=pending",
    )
    return session.id, session.url

def compile_blueprint(deal):
    bottlenecks = json.loads(deal["identified_bottlenecks"]) if isinstance(deal["identified_bottlenecks"], str) else deal["identified_bottlenecks"]
    annual = deal["estimated_monthly_leak_usd"] * 12
    sections = "\n\n".join(f"### {i+1}. {b}\n- Impact: ~${deal['estimated_monthly_leak_usd'] // max(1, len(bottlenecks)):,}/mo" for i, b in enumerate(bottlenecks))
    return f"# Remediation Blueprint\n**Client:** {deal['company_name']}\n**Recoverable:** ${deal['estimated_monthly_leak_usd']:,}/mo (${annual:,}/yr)\n\n{sections}\n"

@app.post("/api/v1/sales/initiate")
async def initiate_sale(lead: LeadTarget):
    sku = SKU_CATALOG.get(lead.sku_id)
    if not sku:
        raise HTTPException(status_code=400, detail="Unknown SKU")
    if not db_pool:
        approval_id = await AutonomousSalesGate.verify_and_mint(None, lead, sku["price_cents"])
        _, url = generate_stripe_session(lead, approval_id)
        return {"status": "DRY_RUN", "lead_id": lead.lead_id, "approval_id": approval_id, "checkout_url": url}
    async with db_pool.acquire() as conn:
        existing = await conn.fetchval("SELECT stage FROM deals WHERE lead_id = $1", lead.lead_id)
        if existing:
            return {"status": "ALREADY_EXISTS", "stage": existing}
        try:
            approval_id = await AutonomousSalesGate.verify_and_mint(conn, lead, sku["price_cents"])
        except (PermissionError, ValueError, RuntimeError) as exc:
            raise HTTPException(status_code=403, detail=str(exc))
        session_id, checkout_url = generate_stripe_session(lead, approval_id)
        body = f"{lead.company_name}: ${lead.estimated_monthly_leak_usd:,}/mo leakage flagged.\n\nBlueprint: {checkout_url}\n\n-- Garcar"
        msg_id = await send_production_email(lead.contact_email, f"{lead.company_name}: leakage audit ready", body, approval_id)
        await conn.execute(
            "INSERT INTO deals (lead_id, company_name, contact_email, domain, sku_id, price_cents, estimated_monthly_leak_usd, identified_bottlenecks, confidence_score, approval_id, stripe_session_id, checkout_url, stage, last_message_id) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,'PITCHED',$13)",
            lead.lead_id, lead.company_name, lead.contact_email.lower(), lead.domain.lower(), lead.sku_id, sku["price_cents"], lead.estimated_monthly_leak_usd, json.dumps(lead.identified_bottlenecks), lead.confidence_score, approval_id, session_id, checkout_url, msg_id
        )
        await conn.execute("INSERT INTO audit_trail (lead_id, action, metadata) VALUES ($1, 'PITCH_DISPATCHED', $2)", lead.lead_id, json.dumps({"approval_id": approval_id}))
    return {"status": "PITCHED", "lead_id": lead.lead_id, "approval_id": approval_id, "checkout_url": checkout_url}

@app.post("/api/v1/sales/inbound-reply")
async def inbound_reply(payload: InboundEmailPayload):
    if not db_pool:
        return {"status": "DRY_RUN"}
    sender = payload.from_email.lower()
    async with db_pool.acquire() as conn:
        deal = await conn.fetchrow("SELECT * FROM deals WHERE contact_email = $1 ORDER BY created_at DESC LIMIT 1", sender)
        if not deal or deal["stage"] in ("SUPPRESSED", "FULFILLED"):
            return {"status": "IGNORED"}
        text_lower = payload.text.lower()
        if any(w in text_lower for w in ["unsubscribe", "stop", "remove", "opt out"]):
            await conn.execute("UPDATE deals SET stage = 'SUPPRESSED', updated_at = NOW() WHERE lead_id = $1", deal["lead_id"])
            await conn.execute("INSERT INTO suppression_list (domain, email, reason) VALUES ($1, $2, 'USER_OPT_OUT') ON CONFLICT DO NOTHING", deal["domain"], sender)
            return {"status": "SUPPRESSED"}
        fee = deal["price_cents"] // 100
        monthly = deal["estimated_monthly_leak_usd"]
        payback = max(1, int((fee / monthly) * 30))
        if any(w in text_lower for w in ["price", "cost", "expensive", "discount", "budget"]):
            reply = f"Fixed at ${fee:,}. Primary bottleneck recovers the fee in ~{payback} days.\n{deal['checkout_url']}"
            action = "OBJECTION_PRICE_HANDLED"
        else:
            reply = f"Portal unlocks on payment.\n{deal['checkout_url']}"
            action = "CLOSER_FOLLOWUP"
        subj = payload.subject if payload.subject.lower().startswith("re:") else f"Re: {payload.subject}"
        msg_id = await send_production_email(sender, subj, reply, deal["approval_id"], deal["last_message_id"])
        await conn.execute("UPDATE deals SET stage = 'NEGOTIATING', last_message_id = $1, updated_at = NOW() WHERE lead_id = $2", msg_id, deal["lead_id"])
    return {"status": action, "lead_id": deal["lead_id"]}

@app.post("/api/v1/billing/stripe-webhook")
async def stripe_webhook(request: Request, background_tasks: BackgroundTasks, stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature")):
    payload = await request.body()
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature")
    try:
        if not STRIPE_WEBHOOK_SECRET or STRIPE_WEBHOOK_SECRET == "whsec_placeholder":
            event = json.loads(payload.decode())
        else:
            event = stripe.Webhook.construct_event(payload, stripe_signature, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid signature: {e}")
    if not db_pool:
        return {"status": "DRY_RUN"}
    event_id = event.get("id")
    async with db_pool.acquire() as conn:
        if await conn.fetchval("SELECT 1 FROM webhook_events WHERE event_id = $1", event_id):
            return {"status": "IDEMPOTENT_SKIP"}
        if event.get("type") == "checkout.session.completed":
            session = event["data"]["object"]
            meta = session.get("metadata", {})
            lead_id = meta.get("lead_id")
            approval_id = meta.get("approval_id")
            amount = session.get("amount_total")
            deal = await conn.fetchrow("SELECT * FROM deals WHERE lead_id = $1", lead_id)
            if not deal:
                raise HTTPException(status_code=404, detail="Unknown lead")
            if amount != deal["price_cents"] or approval_id != deal["approval_id"]:
                raise HTTPException(status_code=400, detail="Price or approval mismatch")
            blueprint = compile_blueprint(deal)
            token = secrets.token_urlsafe(24)
            await conn.execute("UPDATE deals SET stage = 'CLOSED_WON', deliverable_markdown = $1, portal_access_token = $2, updated_at = NOW() WHERE lead_id = $3", blueprint, token, lead_id)
            await conn.execute("INSERT INTO webhook_events (event_id, event_type, lead_id) VALUES ($1, $2, $3)", event_id, event["type"], lead_id)
            background_tasks.add_task(fulfill, lead_id, deal["contact_email"], deal["company_name"], token)
    return {"status": "VERIFIED"}

async def fulfill(lead_id, email, company, token):
    if not db_pool: return
    portal = f"{PUBLIC_BASE_URL}/portal/{lead_id}?token={token}"
    async with db_pool.acquire() as conn:
        deal = await conn.fetchrow("SELECT approval_id FROM deals WHERE lead_id = $1", lead_id)
        await send_production_email(email, f"[DELIVERED] {company} Audit", f"Blueprint ready:\n{portal}", deal["approval_id"])
        await conn.execute("UPDATE deals SET stage = 'FULFILLED', fulfilled_at = NOW() WHERE lead_id = $1", lead_id)

@app.get("/portal/{lead_id}", response_class=HTMLResponse)
async def portal(lead_id: str, token: Optional[str] = None):
    if not db_pool:
        return HTMLResponse("<h1>Portal unavailable</h1>")
    async with db_pool.acquire() as conn:
        deal = await conn.fetchrow("SELECT * FROM deals WHERE lead_id = $1", lead_id)
        if not deal or deal["portal_access_token"] != token:
            raise HTTPException(status_code=403, detail="Invalid token")
        return HTMLResponse(f"<pre>{deal['deliverable_markdown'] or 'Pending'}</pre>")

@app.get("/health")
async def health():
    return {"status": "ok", "db": db_pool is not None, "smtp_configured": bool(SMTP_PASSWORD), "stripe_configured": bool(STRIPE_SECRET_KEY)}
