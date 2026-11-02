import json
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from dashboard import make_handler
from gateway import Gateway
from simulator import simulate


class FreshnessApiTests(unittest.TestCase):
    def test_freshness_api_reads_persisted_receipts(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'telemetry.db'
            gateway = Gateway(path)
            gateway.ingest(simulate(1)[0])
            gateway.close()
            server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(path))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                connection = HTTPConnection('127.0.0.1', server.server_port, timeout=3)
                connection.request('GET', '/api/freshness')
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                body = json.loads(response.read())
                self.assertEqual(body['KUKA-VIRTUAL-01']['telemetry_state'], 'fresh')
                self.assertFalse(body['KUKA-VIRTUAL-01']['communication_loss_confirmed'])
                connection.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)
