import sqlite3
import tempfile
import unittest
from pathlib import Path

from system_diagnostics import diagnose_database
from gateway import Gateway
from simulator import simulate


class DiagnosticsReadOnlyTests(unittest.TestCase):
    def test_diagnostics_does_not_migrate_legacy_schema(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy.db"
            connection = sqlite3.connect(path)
            connection.execute("CREATE TABLE telemetry (equipment_id TEXT NOT NULL, sequence INTEGER NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(equipment_id, sequence))")
            connection.commit()
            connection.close()
            result = diagnose_database(path)
            self.assertEqual(result["storage_state"], "ready")
            connection = sqlite3.connect(path)
            columns = [row[1] for row in connection.execute("PRAGMA table_info(telemetry)")]
            connection.close()
            self.assertNotIn("received_at", columns)

    def test_diagnostics_does_not_update_existing_database(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.db"
            gateway = Gateway(path)
            gateway.ingest(simulate(1)[0])
            gateway.close()
            before = path.read_bytes()
            self.assertEqual(diagnose_database(path)["storage_state"], "ready")
            self.assertEqual(path.read_bytes(), before)
