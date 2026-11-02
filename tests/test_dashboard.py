import unittest
from dashboard import render_dashboard

class DashboardTests(unittest.TestCase):
    def test_empty_state(self):
        summary = {"equipment_count": 0, "event_count": 0, "produced_units": 0, "alarm_events": 0}
        page = render_dashboard(summary, [])
        self.assertIn("SIMULATION ONLY", page)
        self.assertIn("Produced units", page)

    def test_escapes_untrusted_telemetry(self):
        summary = {"equipment_count": 1, "event_count": 1, "produced_units": 0, "alarm_events": 1}
        event = {"equipment_id": "<script>alert(1)</script>", "sequence": 0, "status": "alarm",
                 "produced_units": 0, "alarm_code": "<img src=x>"}
        page = render_dashboard(summary, [event])
        self.assertNotIn("<script>", page)
        self.assertNotIn("<img src=x>", page)
        self.assertIn("&lt;script&gt;", page)

if __name__ == "__main__":
    unittest.main()
