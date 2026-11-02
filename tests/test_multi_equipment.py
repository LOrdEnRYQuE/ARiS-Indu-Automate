import unittest
from simulator import simulate_line
from gateway import Gateway

class MultiEquipmentTests(unittest.TestCase):
    def test_independent_equipment_sequences(self):
        events = simulate_line(cycles=4, alarm_at=2)
        self.assertEqual(len(events), 8)
        machines = {e["equipment_id"] for e in events}
        self.assertEqual(machines, {"KUKA-VIRTUAL-01", "KUKA-VIRTUAL-02"})
        for machine in machines:
            group = [e for e in events if e["equipment_id"] == machine]
            self.assertEqual([e["sequence"] for e in group], [0,1,2,3])
        self.assertEqual([e["produced_units"] for e in events if e["equipment_id"] == "KUKA-VIRTUAL-02"], [1,2,3,4])

    def test_gateway_counts_distinct_machines(self):
        gateway = Gateway(":memory:")
        try:
            for event in simulate_line(cycles=4, alarm_at=2):
                gateway.ingest(event)
            summary = gateway.summary()
            self.assertEqual(summary["equipment_count"], 2)
            self.assertEqual(summary["event_count"], 8)
            self.assertEqual(summary["produced_units"], 6)
            self.assertEqual(summary["alarm_events"], 2)
        finally:
            gateway.close()

if __name__ == "__main__":
    unittest.main()
