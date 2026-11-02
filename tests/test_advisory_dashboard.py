import unittest
from dashboard import render_dashboard
from simulator import simulate
from ai_engineer import analyze

class AdvisoryDashboardTests(unittest.TestCase):
    def test_alarm_advice_is_visible_and_read_only(self):
        events = simulate(4, alarm_at=2)
        summary = {"equipment_count":1,"event_count":4,"produced_units":2,"alarm_events":2}
        page = render_dashboard(summary, events)
        self.assertIn("AI Engineer", page)
        self.assertIn("Simulated feed blockage", page)
        self.assertIn("advisory only", page.lower())
        self.assertNotIn("Execute robot command", page)

    def test_unknown_alarm_is_not_assigned_cause(self):
        event = {**simulate(1, alarm_at=0)[0], "alarm_code":"UNMAPPED"}
        summary = {"equipment_count":1,"event_count":1,"produced_units":0,"alarm_events":1}
        page = render_dashboard(summary, [event])
        self.assertIn("Unknown simulator alarm code", page)

if __name__ == "__main__":
    unittest.main()
