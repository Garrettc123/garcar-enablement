import unittest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from revenue.layer import RevenueLayer, COVERAGE, AutonomyGovernor

class TestRevenue(unittest.TestCase):
    def test_coverage(self):
        self.assertIn("LLA-47", COVERAGE)
        self.assertGreaterEqual(len(COVERAGE), 6)
    def test_autokey_idempotent(self):
        rl = RevenueLayer()
        e1 = rl.quote("LLA-47", "abc123")
        e2 = rl.quote("LLA-47", "abc123")
        self.assertFalse(e1["idempotent"])
        self.assertTrue(e2["idempotent"])
        self.assertEqual(e1["autokey"], e2["autokey"])
    def test_governor_verbs(self):
        g = AutonomyGovernor()
        self.assertEqual(g.decide("high", False), "hold")
        self.assertEqual(g.decide("low", True, True), "execute")
        self.assertEqual(g.decide("medium", False, False), "simulate")
        self.assertEqual(g.decide("high", True, True), "escalate")
    def test_quote_has_url(self):
        e = RevenueLayer().quote("AI-AUDIT-299", "def456")
        self.assertIn("buy.stripe.com", e["url"])
        self.assertFalse(e["cash"])

if __name__ == "__main__":
    unittest.main()
