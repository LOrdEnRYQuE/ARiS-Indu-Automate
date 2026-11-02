import tempfile
import unittest
from pathlib import Path
from dashboard import render_dashboard
from gateway import Gateway


class DiagnosticsDashboardTests(unittest.TestCase):
    def test_dashboard_displays_storage_diagnostics_separately(self):
        summary = {"equipment_count": 0, "event_count": 0, "produced_units": 0, "alarm_events": 0}
        diagnostics = {"storage_state": "ready", "reason": None, "event_count": 0, "physical_safety_verified": False}
        html = render_dashboard(summary, [], {}, diagnostics)
        self.assertIn("System diagnostics", html)
        self.assertIn("ready", html)
        self.assertIn("Not a physical safety check", html)
