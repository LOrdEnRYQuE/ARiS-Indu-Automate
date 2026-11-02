import tempfile
import unittest
from pathlib import Path
from gateway import Gateway
from simulator import simulate

class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "telemetry.db"
        self.gateway = Gateway(self.db)

    def tearDown(self):
        self.gateway.close()
        self.tmp.cleanup()

    def test_ingest_and_summary(self):
        for event in simulate(5, alarm_at=3):
            self.assertTrue(self.gateway.ingest(event))
        self.assertEqual(self.gateway.summary(), {
            "equipment_count": 1, "event_count": 5,
            "produced_units": 3, "alarm_events": 2,
        })

    def test_duplicate_is_idempotent(self):
        event = simulate(1)[0]
        self.assertTrue(self.gateway.ingest(event))
        self.assertFalse(self.gateway.ingest(event))

    def test_conflicting_duplicate_rejected(self):
        event = simulate(1)[0]
        self.gateway.ingest(event)
        changed = {**event, "produced_units": 99}
        with self.assertRaises(ValueError):
            self.gateway.ingest(changed)

    def test_out_of_order_rejected(self):
        with self.assertRaises(ValueError):
            self.gateway.ingest(simulate(2)[1])

    def test_rejects_non_simulated_equipment(self):
        event = {**simulate(1)[0], "source": "plc"}
        with self.assertRaises(ValueError):
            self.gateway.ingest(event)

    def test_persistence_after_reopen(self):
        self.gateway.ingest(simulate(1)[0])
        self.gateway.close()
        self.gateway = Gateway(self.db)
        self.assertEqual(self.gateway.summary()["produced_units"], 1)

if __name__ == "__main__":
    unittest.main()
