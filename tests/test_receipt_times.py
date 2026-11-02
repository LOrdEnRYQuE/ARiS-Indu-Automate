import tempfile
import unittest
from pathlib import Path
from gateway import Gateway
from simulator import simulate


class ReceiptTimestampTests(unittest.TestCase):
    def test_receipt_persists_after_reopen(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'events.db'
            gateway = Gateway(path)
            gateway.ingest(simulate(1)[0])
            first = gateway.receipt_times()
            self.assertIsInstance(first['KUKA-VIRTUAL-01'], float)
            gateway.close()
            gateway = Gateway(path)
            self.assertEqual(gateway.receipt_times(), first)
            gateway.close()

    def test_legacy_rows_remain_readable_without_fabricated_receipts(self):
        import sqlite3
        import json
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'legacy.db'
            connection = sqlite3.connect(path)
            connection.execute('CREATE TABLE telemetry (equipment_id TEXT NOT NULL, sequence INTEGER NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(equipment_id, sequence))')
            event = simulate(1)[0]
            connection.execute('INSERT INTO telemetry VALUES (?, ?, ?)', (event['equipment_id'], event['sequence'], json.dumps(event)))
            connection.commit()
            connection.close()
            gateway = Gateway(path)
            self.assertEqual(gateway.events()[0]['equipment_id'], event['equipment_id'])
            self.assertIsNone(gateway.receipt_times()[event['equipment_id']])
            gateway.close()
