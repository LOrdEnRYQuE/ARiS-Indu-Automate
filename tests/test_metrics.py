import unittest
from metrics import equipment_metrics
from simulator import simulate_line

class MetricsTests(unittest.TestCase):
    def test_simulated_counts_are_separate(self):
        result = equipment_metrics(simulate_line(10, alarm_at=7))
        self.assertEqual(result["KUKA-VIRTUAL-01"]["produced_units"], 7)
        self.assertEqual(result["KUKA-VIRTUAL-02"]["produced_units"], 10)
        self.assertEqual(result["KUKA-VIRTUAL-01"]["alarm_events"], 3)

    def test_oee_unavailable_without_time_and_quality(self):
        result = equipment_metrics(simulate_line(2))
        for item in result.values():
            self.assertIsNone(item["oee"])
            self.assertEqual(item["oee_status"], "insufficient_data")

    def test_empty(self):
        self.assertEqual(equipment_metrics([]), {})

if __name__ == "__main__":
    unittest.main()
