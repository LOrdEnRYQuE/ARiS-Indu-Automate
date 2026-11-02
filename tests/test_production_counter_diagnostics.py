import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from system_diagnostics import diagnose_database
from simulator import simulate


class ProductionCounterDiagnosticsTests(unittest.TestCase):
    def test_decreasing_simulator_production_counter_is_degraded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.db"
            connection = sqlite3.connect(path)
            connection.execute("CREATE TABLE telemetry (equipment_id TEXT NOT NULL, sequence INTEGER NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(equipment_id, sequence))")
            events = simulate(3)
            events[2]["produced_units"] = 0
            for event in events:
                connection.execute("INSERT INTO telemetry VALUES (?, ?, ?)", (event["equipment_id"], event["sequence"], json.dumps(event)))
            connection.commit()
            connection.close()
            result = diagnose_database(path)
            self.assertEqual(result["storage_state"], "degraded")
            self.assertEqual(result["reason"], "telemetry_integrity_error")

    def test_alarm_plateau_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.db"
            connection = sqlite3.connect(path)
            connection.execute("CREATE TABLE telemetry (equipment_id TEXT NOT NULL, sequence INTEGER NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(equipment_id, sequence))")
            for event in simulate(4, alarm_at=2):
                connection.execute("INSERT INTO telemetry VALUES (?, ?, ?)", (event["equipment_id"], event["sequence"], json.dumps(event)))
            connection.commit()
            connection.close()
            self.assertEqual(diagnose_database(path)["storage_state"], "ready")
