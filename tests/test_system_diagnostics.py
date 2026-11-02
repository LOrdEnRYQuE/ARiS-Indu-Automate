import sqlite3
import tempfile
import unittest
from pathlib import Path

from system_diagnostics import diagnose_database
from gateway import Gateway
from simulator import simulate


class SystemDiagnosticsTests(unittest.TestCase):
    def test_empty_valid_database_is_ready_not_machine_safe(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.db"
            gateway = Gateway(path)
            gateway.close()
            result = diagnose_database(path)
            self.assertEqual(result["storage_state"], "ready")
            self.assertEqual(result["event_count"], 0)
            self.assertFalse(result["physical_safety_verified"])

    def test_valid_database_reports_event_count(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.db"
            gateway = Gateway(path)
            gateway.ingest(simulate(2)[0])
            gateway.close()
            result = diagnose_database(path)
            self.assertEqual(result["storage_state"], "ready")
            self.assertEqual(result["event_count"], 1)

    def test_corrupted_payload_is_reported_without_exposing_content(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.db"
            gateway = Gateway(path)
            gateway.ingest(simulate(1)[0])
            gateway.close()
            connection = sqlite3.connect(path)
            connection.execute("UPDATE telemetry SET payload=?", ("{broken",))
            connection.commit()
            connection.close()
            result = diagnose_database(path)
            self.assertEqual(result["storage_state"], "degraded")
            self.assertEqual(result["reason"], "telemetry_integrity_error")
            self.assertNotIn("{broken", str(result))
