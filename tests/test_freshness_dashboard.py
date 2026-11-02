import unittest
from dashboard import render_dashboard


class FreshnessDashboardTests(unittest.TestCase):
    def test_freshness_status_rendered_without_claiming_hardware_safety(self):
        summary = {'equipment_count': 0, 'event_count': 0, 'produced_units': 0, 'alarm_events': 0}
        freshness = {'KUKA-VIRTUAL-01': {'telemetry_state': 'stale', 'age_seconds': 45.0, 'communication_loss_confirmed': False, 'physical_safety_verified': False}}
        html = render_dashboard(summary, [], freshness)
        self.assertIn('Telemetry freshness', html)
        self.assertIn('KUKA-VIRTUAL-01', html)
        self.assertIn('stale', html)
        self.assertIn('Not proof of communication loss', html)

    def test_legacy_timestamp_shows_unknown(self):
        summary = {'equipment_count': 0, 'event_count': 0, 'produced_units': 0, 'alarm_events': 0}
        freshness = {'KUKA-VIRTUAL-01': {'telemetry_state': 'unknown', 'age_seconds': None, 'communication_loss_confirmed': False, 'physical_safety_verified': False}}
        self.assertIn('unknown', render_dashboard(summary, [], freshness))
