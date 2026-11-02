import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from system_diagnostics import diagnose_database
from simulator import simulate


class HistoricalSequenceDiagnosticsTests(unittest.TestCase):
    def test_missing_historical_sequence_is_degraded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.db"
            connection = sqlite3.connect(path)
            connection.execute("CREATE TABLE telemetry (equipment_id TEXT NOT NULL, sequence INTEGER NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(equipment_id, sequence))")
            events = simulate(3)
            for event in (events[0], events[2]):
                connection.execute("INSERT INTO telemetry VALUES (?, ?, ?)", (event["equipment_id"], event["sequence"], json.dumps(event)))
            connection.commit()
            connection.close()
            result = diagnose_database(path)
            self.assertEqual(result["storage_state"], "degraded")
            self.assertEqual(result["reason"], "telemetry_integrity_error")
