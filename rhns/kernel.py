from .tools import PreconditionError
class Kernel:
    def __init__(self, ledger, memory, policy, proxy, planner, verifier):
        self.ledger, self.memory, self.policy, self.proxy, self.planner, self.verifier = ledger, memory, policy, proxy, planner, verifier
    def run(self, task_id, approvals=()):
        approvals = set(approvals)
        plan = self.planner.plan()
        if plan is None:
            self.ledger.append("plan_failed", {"task": task_id})
            return {"status": "no_plan", "receipts": []}
        self.ledger.append("plan", {"task": task_id, "steps": [s["tool"] for s in plan]})
        receipts = []
        for i, s in enumerate(plan):
            tool = self.proxy.tools[s["tool"]]
            d = self.policy.decide(tool.name, tool.authority)
            if d == "deny" or (d == "needs_approval" and tool.name not in approvals):
                st = "blocked" if d == "deny" else "awaiting_approval"
                self.ledger.append(st, {"task": task_id, "tool": tool.name})
                return {"status": st, "pending": tool.name, "receipts": receipts}
            try:
                r = self.proxy.call(tool.name, s.get("args", {}), f"{task_id}:{i}:{tool.name}")
            except PreconditionError as e:
                self.ledger.append("blocked", {"task": task_id, "tool": tool.name, "why": str(e)})
                return {"status": "blocked", "pending": tool.name, "receipts": receipts}
            self.ledger.append("action", {"task": task_id, "receipt": r})
            self.memory.add(r)
            receipts.append(r)
        ok, detail = self.verifier.run(receipts)
        self.ledger.append("verify", {"task": task_id, "ok": ok, "detail": detail})
        return {"status": "verified" if ok else "failed", "receipts": receipts, "detail": detail}
