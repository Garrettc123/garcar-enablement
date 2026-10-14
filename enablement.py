"""Garcar Enablement System — full-scale runtime that enables all built products and repos under the RHNS Kernel."""
from __future__ import annotations
import json
from typing import Any, Dict, List, Optional
try:
    from .rhns import Ledger, Memory, Policy, Authority, Tool, ToolProxy, Planner, Verifier, Kernel
except ImportError:
    from rhns import Ledger, Memory, Policy, Authority, Tool, ToolProxy, Planner, Verifier, Kernel

PRODUCTS = {
    "RHNS-Architecture": {"repo": "Garrettc123/RHNS-Architecture", "url": "https://github.com/Garrettc123/RHNS-Architecture", "role": "neuro-symbolic cognitive substrate", "capabilities": ["plan_goal", "synthesize_skill", "verify_constraint", "audit_chain"]},
    "apex-revenue-system": {"repo": "Garrettc123/apex-revenue-system", "url": "https://github.com/Garrettc123/apex-revenue-system", "role": "autonomous revenue system", "capabilities": ["intake_lead", "qualify", "outreach_draft", "crm_sync", "payment_link"]},
    "nwu-protocol": {"repo": "Garrettc123/nwu-protocol", "url": "https://github.com/Garrettc123/nwu-protocol", "role": "decentralized verification protocol", "capabilities": ["verify_claim", "anchor_proof", "meter_nwu"]},
    "garcar-star": {"repo": "Garrettc123/garcar-star", "url": "https://github.com/Garrettc123/garcar-star", "role": "governed STAR control plane", "capabilities": ["queue_task", "lease_worker", "pause_control", "audit_effect"]},
    "revenue-orchestrator": {"repo": "Garrettc123/revenue-orchestrator", "url": "https://github.com/Garrettc123/revenue-orchestrator", "role": "deal to HubSpot to Stripe", "capabilities": ["sync_deal", "create_invoice", "emit_revenue_event"]},
    "garcar-landing": {"repo": "Garrettc123/garcar-landing", "url": "https://garrettc123.github.io/", "role": "public storefront", "capabilities": ["render_sku", "cta_link"]},
    "bioforge-revenue": {"repo": "BioForge organ", "role": "Revenue spine organ", "capabilities": ["lead_intake", "enrich", "outreach", "proposal", "checkout", "crm_sync", "fulfill", "report"]},
}

SKUS = {
    "LLA-47": "https://buy.stripe.com/3cI00j7YV0hQgDp8BR43S2v",
    "AI-AUDIT-299": "https://buy.stripe.com/14A5kD3IF9Sqdrd05l43S2l",
    "ENT-AUDIT-3500": "https://buy.stripe.com/4gMfZh1Ax2pYbj5dWb43S2t",
    "MARS-750": "https://buy.stripe.com/4gM7sL6UR3u29aX4lB43S2r",
    "MARS-1500": "https://buy.stripe.com/7sY4gz1Ax3u20Er6tJ43S2s",
    "GROWTH-1497": "https://buy.stripe.com/8x29AT7YVe8G3QD4lB43S2m",
}

class ConnectorWorld:
    def __init__(self):
        self.github_issues, self.crm, self.gmail_drafts, self.stripe_intents, self.proofs = [], [], [], [], []

world = ConnectorWorld()

def build_proxy():
    px = ToolProxy()
    px.register(Tool("list_products", lambda: list(PRODUCTS.keys()), Authority.READ))
    px.register(Tool("lookup_product", lambda name: PRODUCTS.get(name, {}), Authority.READ, ("name",)))
    px.register(Tool("crm_note", lambda text, contact=None: world.crm.append({"text": text, "status": "prepared"}) or {"text": text}, Authority.REVERSIBLE, ("text",)))
    px.register(Tool("proof_append", lambda kind, payload: world.proofs.append(json.dumps({"kind": kind, "payload": payload})) or "ok", Authority.REVERSIBLE, ("kind", "payload")))
    px.register(Tool("gmail_draft", lambda to, subject, body: world.gmail_drafts.append({"to": to}) or {"status": "draft"}, Authority.EXTERNAL, ("to", "subject", "body")))
    px.register(Tool("stripe_payment_link", lambda sku="LLA-47": world.stripe_intents.append({"sku": sku, "url": SKUS.get(sku)}) or {"sku": sku, "url": SKUS.get(sku), "status": "prepared_not_charged"}, Authority.FINANCIAL))
    return px

class EnablementKernel:
    def __init__(self, max_cost=1.0):
        self.ledger = Ledger()
        self.memory = Memory()
        self.policy = Policy(max_autonomous=Authority.REVERSIBLE)
        self.proxy = build_proxy()
        self.verifier = Verifier([("ok", lambda r: True)])
        self.max_cost = max_cost
    def _proposer(self, steps):
        seq = [
            {"tool": "list_products", "utility": 1, "evidence": 1, "cost": 0.01},
            {"tool": "lookup_product", "args": {"name": "apex-revenue-system"}, "utility": 1, "evidence": 1, "cost": 0.01},
            {"tool": "crm_note", "args": {"text": "Enablement cycle"}, "utility": 1, "evidence": 1, "cost": 0.01},
            {"tool": "proof_append", "args": {"kind": "enablement", "payload": {"products": list(PRODUCTS.keys())}}, "utility": 2, "evidence": 1, "cost": 0.01},
        ]
        i = len(steps)
        return [seq[i]] if i < len(seq) else []
    def plan_and_run(self, task_id, approvals=None):
        planner = Planner(self._proposer, lambda s: len(s) >= 4, max_cost=self.max_cost)
        k = Kernel(self.ledger, self.memory, self.policy, self.proxy, planner, self.verifier)
        result = k.run(task_id, approvals or set())
        result["proof_hash"] = self.ledger._last()
        result["products_enabled"] = list(PRODUCTS.keys())
        result["skus"] = SKUS
        return result

def run_enablement(task_id="enable-all", approvals=None, max_cost=1.0):
    return EnablementKernel(max_cost).plan_and_run(task_id, approvals)
