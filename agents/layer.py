"""Agent layer — role registry, task routing, and policy-gated handoff under the RHNS Kernel."""
from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional
from enablement import EnablementKernel, PRODUCTS, SKUS

ROLES = {
    "research": {"purpose": "Lookup products, enrich leads, prepare briefs.", "tools": ["list_products", "lookup_product", "crm_note", "notion_page", "proof_append"], "max_authority": "REVERSIBLE"},
    "outreach": {"purpose": "Draft consented outreach. Never send without approval.", "tools": ["gmail_draft", "crm_note", "proof_append"], "max_authority": "EXTERNAL"},
    "crm": {"purpose": "Authoritative contact and deal notes.", "tools": ["crm_note", "hubspot_note", "linear_issue", "proof_append"], "max_authority": "REVERSIBLE"},
    "billing": {"purpose": "Prepare payment links. Never charge without approval.", "tools": ["stripe_payment_link", "proof_append"], "max_authority": "FINANCIAL"},
    "governance": {"purpose": "Plan, verify, audit. Holds external/financial.", "tools": ["list_products", "proof_append", "revenue_spine", "github_issue_prepare"], "max_authority": "REVERSIBLE"},
    "fulfillment": {"purpose": "Mark spine hops after paid=true. Same-day deliverable.", "tools": ["revenue_spine", "crm_note", "proof_append"], "max_authority": "REVERSIBLE"},
}

BOT_HANDOFF = {
    "revenue": "d5e73ea6-31d5-4c85-8f55-b85dc930f3f0",
    "control": "7f199824-7a00-40cf-b760-2f73c91d6f39",
    "all_in_one": "14d501c9-def0-48e0-9c0a-5efc976c68b1",
}

class AgentLayer:
    def __init__(self, ledger_path=":memory:", llm_fn=None):
        self.kernel = EnablementKernel(ledger_path=ledger_path, llm_fn=llm_fn)
        self.roles = ROLES
        self.handoff = BOT_HANDOFF
    def route(self, task, role="governance", approvals=None):
        if role not in self.roles: role = "governance"
        approvals = approvals or set()
        result = self.kernel.plan_and_run(f"{role}:{task}", approvals)
        result["role"] = role
        result["role_purpose"] = self.roles[role]["purpose"]
        result["allowed_tools"] = self.roles[role]["tools"]
        return result
    def handoff_prompt(self, role, task, proof_hash):
        key = "revenue" if role in ("outreach", "billing", "fulfillment") else "control" if role == "governance" else "all_in_one"
        agent_id = self.handoff.get(key)
        if not agent_id: return None
        return {"agent_id": agent_id, "prompt": f"Role={role} task={task} proof_hash={proof_hash}. Policy gate is active. Do not send, charge, or ship without explicit approval.", "mode": "async"}
    def status(self):
        return {"roles": list(self.roles.keys()), "handoffs": list(self.handoff.keys()), "kernel": self.kernel.status()}

def run_agent(task, role="governance", approvals=None, ledger_path=":memory:"):
    return AgentLayer(ledger_path=ledger_path).route(task, role, approvals)
