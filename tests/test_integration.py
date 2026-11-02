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

class IntegrationTests(unittest.TestCase):
    def test_simulator_to_http_dashboard(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "events.sqlite3"
            gateway = Gateway(db)
            try:
                for event in simulate(10, alarm_at=7):
                    gateway.ingest(event)
            finally:
                gateway.close()
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(db))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                conn = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
                conn.request("GET", "/api/summary")
                response = conn.getresponse()
                self.assertEqual(response.status, 200)
                self.assertEqual(json.loads(response.read()), {
                    "equipment_count": 1, "event_count": 10,
                    "produced_units": 7, "alarm_events": 3,
                })
                conn.request("GET", "/")
                page = conn.getresponse()
                self.assertEqual(page.status, 200)
                self.assertIn(b"SIMULATION ONLY", page.read())
                conn.request("POST", "/api/summary")
                denied = conn.getresponse()
                self.assertEqual(denied.status, 405)
                denied.read()
                conn.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)

if __name__ == "__main__":
    unittest.main()
