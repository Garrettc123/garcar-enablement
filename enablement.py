"""Garcar Enablement System — full-scale runtime that enables all built products and repos under the RHNS Kernel.

Substrate: the verified stdlib RHNS Kernel (planner, policy, idempotent tools, tiered memory, verifier, hash-chained ledger).
Products registered: RHNS-Architecture, apex-revenue-system, nwu-protocol, garcar-star, revenue-orchestrator, garcar-landing, BioForge organs.
All external actions stay behind Policy + Ledger. Money/reputation hops require approval (CMC commit).
"""
from __future__ import annotations
import json
from typing import Any, Callable, Dict, List, Optional
try:
    from .rhns import Ledger, Memory, Policy, Authority, Tool, ToolProxy, Planner, Verifier, Kernel, PreconditionError
except ImportError:
    from rhns import Ledger, Memory, Policy, Authority, Tool, ToolProxy, Planner, Verifier, Kernel, PreconditionError

PRODUCTS: Dict[str, Dict[str, Any]] = {
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
        self.github_issues, self.hubspot_notes, self.crm, self.gmail_drafts, self.stripe_intents, self.proofs, self.outbox = [], [], [], [], [], [], []

world = ConnectorWorld()

def _safe_github_issue(title, body, repo="Garrettc123/garcar-enablement"):
    rec = {"title": title, "body": body, "repo": repo, "status": "prepared"}
    world.github_issues.append(rec)
    return rec

def build_proxy():
    px = ToolProxy()
    px.register(Tool("list_products", lambda: list(PRODUCTS.keys()), Authority.READ))
    px.register(Tool("lookup_product", lambda name: PRODUCTS.get(name, {}), Authority.READ, ("name",)))
    px.register(Tool("crm_note", lambda text, contact=None: (world.crm.append({"text": text, "status": "prepared"}) or {"text": text}), Authority.REVERSIBLE, ("text",)))
    px.register(Tool("github_issue_prepare", lambda title, body, repo="Garrettc123/garcar-enablement": _safe_github_issue(title, body, repo), Authority.REVERSIBLE, ("title", "body")))
    px.register(Tool("github_issue_live", lambda title, body, repo="Garrettc123/garcar-enablement": _safe_github_issue(title, body + " [LIVE_INTENT]", repo), Authority.EXTERNAL, ("title", "body")))
    px.register(Tool("proof_append", lambda kind, payload: (world.proofs.append(json.dumps({"kind": kind, "payload": payload})) or "ok"), Authority.REVERSIBLE, ("kind", "payload")))
    px.register(Tool("gmail_draft", lambda to, subject, body: (world.gmail_drafts.append({"to": to}) or {"status": "draft"}), Authority.EXTERNAL, ("to", "subject", "body")))
    px.register(Tool("stripe_payment_link", lambda sku="LLA-47": (world.stripe_intents.append({"sku": sku, "url": SKUS.get(sku)}) or {"sku": sku, "url": SKUS.get(sku), "status": "prepared_not_charged"}), Authority.FINANCIAL))
    return px

class LLMProposer:
    def __init__(self, llm_fn=None):
        self.llm_fn = llm_fn
    def __call__(self, steps, approvals, products):
        if self.llm_fn:
            try:
                cands = self.llm_fn({"steps": [s.get("tool") for s in steps], "approvals": list(approvals), "products": list(products.keys())})
                if cands: return cands
            except Exception:
                pass
        done = {s.get("tool") for s in steps}
        cands = []
        if "list_products" not in done:
            cands.append({"tool": "list_products", "utility": 1.0, "evidence": 1.0, "cost": 0.01, "risk": 0.0})
        if "lookup_product" not in done:
            cands.append({"tool": "lookup_product", "args": {"name": "apex-revenue-system"}, "utility": 0.9, "evidence": 1.0, "cost": 0.01, "risk": 0.0})
        if "crm_note" not in done:
            cands.append({"tool": "crm_note", "args": {"text": "Enablement cycle"}, "utility": 0.8, "evidence": 1.0, "cost": 0.01, "risk": 0.0})
        if "proof_append" not in done:
            cands.append({"tool": "proof_append", "args": {"kind": "enablement", "payload": {"products": list(products.keys())}}, "utility": 1.2, "evidence": 1.0, "cost": 0.01, "risk": 0.0})
        if "github_issue_live" in approvals and "github_issue_live" not in done:
            cands.append({"tool": "github_issue_live", "args": {"title": "RHNS Enablement", "body": "Proof-linked."}, "utility": 0.7, "evidence": 1.0, "cost": 0.02, "risk": 0.1})
        elif "github_issue_prepare" not in done:
            cands.append({"tool": "github_issue_prepare", "args": {"title": "RHNS Enablement", "body": "Proof-linked."}, "utility": 0.7, "evidence": 1.0, "cost": 0.02, "risk": 0.0})
        scored = sorted(cands, key=lambda c: c.get("utility",0)+0.5*c.get("evidence",0)-c.get("risk",0)-c.get("cost",0), reverse=True)
        return scored[:2]

class EnablementKernel:
    def __init__(self, max_cost=1.0, max_autonomous=Authority.REVERSIBLE, ledger_path=":memory:", llm_fn=None):
        self.ledger = Ledger(path=ledger_path)
        self.memory = Memory(active_limit=8)
        self.policy = Policy(max_autonomous=max_autonomous, prohibited={"purchase"})
        self.proxy = build_proxy()
        self.verifier = Verifier([("ledger_ok", lambda r: self.ledger.verify())])
        self.max_cost = max_cost
        self.approvals = set()
        self.llm_proposer = LLMProposer(llm_fn)
    def _proposer(self, steps):
        return self.llm_proposer(steps, self.approvals, PRODUCTS)
    def plan_and_run(self, task_id, approvals=None):
        self.approvals = approvals or set()
        def complete(s):
            tools = {x.get("tool") for x in s}
            return {"list_products", "proof_append"}.issubset(tools) and len(s) >= 4
        planner = Planner(self._proposer, complete, max_cost=self.max_cost)
        k = Kernel(self.ledger, self.memory, self.policy, self.proxy, planner, self.verifier)
        result = k.run(task_id, self.approvals)
        result["proof_hash"] = self.ledger._last()
        result["products_enabled"] = list(PRODUCTS.keys())
        result["skus"] = SKUS
        result["approvals_used"] = list(self.approvals)
        result["world_summary"] = {"github_issues": len(world.github_issues), "crm_notes": len(world.crm), "drafts": len(world.gmail_drafts), "stripe_prepared": len(world.stripe_intents), "proofs": len(world.proofs)}
        return result
    def status(self):
        return {"products": list(PRODUCTS.keys()), "skus": list(SKUS.keys()), "ledger_ok": self.ledger.verify(), "policy_max": self.policy.max_autonomous.name}

def run_enablement(task_id="enable-all", approvals=None, max_cost=1.0, ledger_path=":memory:", llm_fn=None):
    return EnablementKernel(max_cost=max_cost, ledger_path=ledger_path, llm_fn=llm_fn).plan_and_run(task_id, approvals)
