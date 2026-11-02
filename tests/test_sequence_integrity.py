import tempfile
import unittest
from pathlib import Path

from gateway import Gateway
from simulator import simulate


class SequenceIntegrityTests(unittest.TestCase):
    def test_rejects_sequence_gap_without_changing_database(self):
        gateway = Gateway(":memory:")
        try:
            events = simulate(3)
            self.assertTrue(gateway.ingest(events[0]))
            with self.assertRaisesRegex(ValueError, "out-of-order"):
                gateway.ingest(events[2])
            self.assertEqual(gateway.summary()["event_count"], 1)
            self.assertTrue(gateway.ingest(events[1]))
            self.assertTrue(gateway.ingest(events[2]))
            self.assertEqual(gateway.summary()["event_count"], 3)
        finally:
            gateway.close()

    def test_identical_duplicate_is_idempotent_but_conflicting_duplicate_rejected(self):
        gateway = Gateway(":memory:")
        try:
            event = simulate(1)[0]
            self.assertTrue(gateway.ingest(event))
            self.assertFalse(gateway.ingest(dict(event)))
            conflicting = dict(event, produced_units=99)
            with self.assertRaisesRegex(ValueError, "conflicting duplicate"):
                gateway.ingest(conflicting)
            self.assertEqual(gateway.summary()["event_count"], 1)
        finally:
            gateway.close()

    def test_sequence_validation_survives_restart(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "telemetry.db"
            events = simulate(3)
            gateway = Gateway(path)
            gateway.ingest(events[0])
            gateway.close()
            gateway = Gateway(path)
            try:
                with self.assertRaisesRegex(ValueError, "out-of-order"):
                    gateway.ingest(events[2])
                gateway.ingest(events[1])
                self.assertEqual(gateway.summary()["event_count"], 2)
            finally:
                gateway.close()
