import unittest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.layer import run_agent, AgentLayer, ROLES

class TestAgents(unittest.TestCase):
    def test_roles(self):
        self.assertIn("research", ROLES)
        self.assertGreaterEqual(len(ROLES), 5)
    def test_route_governance(self):
        r = run_agent("enable", role="governance")
        self.assertIn(r["status"], ("verified", "awaiting_approval", "no_plan", "blocked"))
        self.assertEqual(r["role"], "governance")
        self.assertIn("proof_hash", r)
    def test_handoff_payload(self):
        payload = AgentLayer().handoff_prompt("outreach", "draft", "abc123")
        self.assertIsNotNone(payload)
        self.assertIn("agent_id", payload)

if __name__ == "__main__":
    unittest.main()
