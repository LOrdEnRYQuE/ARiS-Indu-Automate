import json
import sqlite3
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path

from dashboard import make_handler
from gateway import Gateway
from simulator import simulate


class CorruptDatabaseHttpTests(unittest.TestCase):
    def test_corrupt_telemetry_returns_controlled_error_for_all_read_endpoints(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "telemetry.db"
            gateway = Gateway(path)
            gateway.ingest(simulate(1)[0])
            gateway.close()
            connection = sqlite3.connect(path)
            connection.execute("UPDATE telemetry SET payload = ?", ("{bad json",))
            connection.commit()
            connection.close()

            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(path))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                for endpoint in ("/", "/api/events", "/api/summary", "/api/metrics", "/api/health", "/api/freshness"):
                    connection = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
                    connection.request("GET", endpoint)
                    response = connection.getresponse()
                    body = response.read().decode("utf-8")
                    self.assertEqual(response.status, 500, endpoint)
                    self.assertIn("Unable to read simulation telemetry", body)
                    self.assertNotIn("{bad json", body)
                    self.assertNotIn("Traceback", body)
                    connection.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)
