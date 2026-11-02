import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from gateway import Gateway
from simulator import simulate_line
from telemetry_freshness import assess_freshness


class RestartRecoveryTests(unittest.TestCase):
    def test_reopen_preserves_events_receipts_and_sequence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "telemetry.db"
            gateway = Gateway(path)
            events = simulate_line(4, alarm_at=2)
            for event in events[:4]:
                gateway.ingest(event)
            receipts_before = gateway.receipt_times()
            gateway.close()

            gateway = Gateway(path)
            self.assertEqual(gateway.summary()["event_count"], 4)
            self.assertEqual(gateway.receipt_times(), receipts_before)
            for event in events[4:]:
                gateway.ingest(event)
            self.assertEqual(gateway.summary()["event_count"], 8)
            self.assertEqual(gateway.summary()["equipment_count"], 2)
            self.assertEqual(assess_freshness(gateway.receipt_times(), now=max(gateway.receipt_times().values()))["KUKA-VIRTUAL-01"]["telemetry_state"], "fresh")
            gateway.close()

    def test_legacy_rows_remain_unknown_after_repeated_restarts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.db"
            event = simulate_line(1)[0]
            connection = sqlite3.connect(path)
            connection.execute("CREATE TABLE telemetry (equipment_id TEXT NOT NULL, sequence INTEGER NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(equipment_id, sequence))")
            connection.execute("INSERT INTO telemetry VALUES (?, ?, ?)", (event["equipment_id"], event["sequence"], json.dumps(event)))
            connection.commit()
            connection.close()

            for _ in range(2):
                gateway = Gateway(path)
                self.assertEqual(gateway.summary()["event_count"], 1)
                self.assertIsNone(gateway.receipt_times()[event["equipment_id"]])
                self.assertEqual(assess_freshness(gateway.receipt_times(), now=100)["KUKA-VIRTUAL-01"]["telemetry_state"], "unknown")
                gateway.close()
