import unittest
from equipment_health import equipment_health


class HealthReliabilityTests(unittest.TestCase):
    def test_unknown_status_is_not_reported_as_healthy(self):
        event = {'equipment_id': 'VIRTUAL-1', 'sequence': 1, 'status': 'unexpected', 'alarm_code': None}
        self.assertEqual(equipment_health([event])['VIRTUAL-1']['health'], 'unknown')

    def test_missing_alarm_code_does_not_crash(self):
        event = {'equipment_id': 'VIRTUAL-1', 'sequence': 1, 'status': 'running'}
        self.assertIsNone(equipment_health([event])['VIRTUAL-1']['alarm_code'])
