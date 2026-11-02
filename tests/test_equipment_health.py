import unittest
from simulator import simulate_line
from equipment_health import equipment_health


class EquipmentHealthTests(unittest.TestCase):
    def test_alarm_and_running_equipment_are_separate(self):
        report = equipment_health(simulate_line(5, alarm_at=2))
        self.assertEqual(report['KUKA-VIRTUAL-01']['health'], 'alarm')
        self.assertEqual(report['KUKA-VIRTUAL-02']['health'], 'running')
        self.assertEqual(report['KUKA-VIRTUAL-01']['last_sequence'], 4)
        self.assertFalse(report['KUKA-VIRTUAL-01']['physical_safety_verified'])

    def test_empty_telemetry_has_no_health_assertions(self):
        self.assertEqual(equipment_health([]), {})

    def test_latest_sequence_wins_for_unsorted_input(self):
        events = simulate_line(3, alarm_at=1)
        self.assertEqual(equipment_health(list(reversed(events)))['KUKA-VIRTUAL-01']['health'], 'alarm')
