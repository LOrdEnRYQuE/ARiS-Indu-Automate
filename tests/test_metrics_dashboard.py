import unittest
from dashboard import render_dashboard
from simulator import simulate_line
from metrics import equipment_metrics

class MetricsDashboardTests(unittest.TestCase):
    def test_metrics_are_displayed_for_each_machine(self):
        events = simulate_line(4, alarm_at=2)
        summary = {"equipment_count":2,"event_count":8,"produced_units":6,"alarm_events":2}
        html = render_dashboard(summary, events)
        self.assertIn("Equipment performance", html)
        self.assertIn("KUKA-VIRTUAL-01", html)
        self.assertIn("KUKA-VIRTUAL-02", html)
        self.assertIn("insufficient_data", html)
        self.assertIn("OEE", html)

    def test_metric_contract(self):
        data = equipment_metrics(simulate_line(4, alarm_at=2))
        self.assertEqual(data["KUKA-VIRTUAL-01"]["produced_units"],2)
        self.assertIsNone(data["KUKA-VIRTUAL-01"]["oee"])

if __name__ == "__main__":
    unittest.main()
