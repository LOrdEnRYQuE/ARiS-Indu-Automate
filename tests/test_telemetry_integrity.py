import sqlite3
import tempfile
import unittest
from pathlib import Path

from gateway import Gateway
from simulator import simulate


class TelemetryIntegrityTests(unittest.TestCase):
    def test_corrupt_json_is_reported_as_data_integrity_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "telemetry.db"
            gateway = Gateway(path)
            gateway.ingest(simulate(1)[0])
            gateway.close()
            connection = sqlite3.connect(path)
            connection.execute("UPDATE telemetry SET payload = ?", ("{invalid",))
            connection.commit()
            connection.close()
            gateway = Gateway(path)
            try:
                with self.assertRaisesRegex(ValueError, "corrupt telemetry"):
                    gateway.events()
            finally:
                gateway.close()

    def test_payload_identity_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "telemetry.db"
            gateway = Gateway(path)
            gateway.ingest(simulate(1)[0])
            gateway.close()
            connection = sqlite3.connect(path)
            connection.execute("UPDATE telemetry SET equipment_id = ?", ("KUKA-VIRTUAL-99",))
            connection.commit()
            connection.close()
            gateway = Gateway(path)
            try:
                with self.assertRaisesRegex(ValueError, "corrupt telemetry"):
                    gateway.events()
            finally:
                gateway.close()
