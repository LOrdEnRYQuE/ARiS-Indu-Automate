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


class SystemApiTests(unittest.TestCase):
    def _request(self, server, path):
        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read()
        status = response.status
        connection.close()
        return status, body

    def test_system_endpoint_reports_ready_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "telemetry.db"
            gateway = Gateway(path)
            gateway.ingest(simulate(1)[0])
            gateway.close()
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(path))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                status, raw = self._request(server, "/api/system")
                self.assertEqual(status, 200)
                data = json.loads(raw)
                self.assertEqual(data["storage_state"], "ready")
                self.assertEqual(data["event_count"], 1)
                self.assertFalse(data["physical_safety_verified"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)

    def test_system_endpoint_reports_degraded_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "telemetry.db"
            gateway = Gateway(path)
            gateway.ingest(simulate(1)[0])
            gateway.close()
            connection = sqlite3.connect(path)
            connection.execute("UPDATE telemetry SET payload=?", ("{broken",))
            connection.commit()
            connection.close()
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(path))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                status, raw = self._request(server, "/api/system")
                self.assertEqual(status, 200)
                data = json.loads(raw)
                self.assertEqual(data["storage_state"], "degraded")
                self.assertEqual(data["reason"], "telemetry_integrity_error")
                self.assertNotIn("{broken", raw.decode())
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)
