import json
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from dashboard import make_handler
from gateway import Gateway
from simulator import simulate_line

class MetricsApiTests(unittest.TestCase):
    def test_read_only_metrics_endpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "telemetry.sqlite"
            gateway = Gateway(path)
            for event in simulate_line(4, alarm_at=2):
                gateway.ingest(event)
            gateway.close()
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(path))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                connection = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
                connection.request("GET", "/api/metrics")
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                data = json.loads(response.read())
                self.assertEqual(data["KUKA-VIRTUAL-01"]["produced_units"], 2)
                self.assertEqual(data["KUKA-VIRTUAL-02"]["produced_units"], 4)
                self.assertIsNone(data["KUKA-VIRTUAL-01"]["oee"])
                connection.request("POST", "/api/metrics")
                response = connection.getresponse()
                self.assertEqual(response.status, 405)
                response.read()
                connection.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)

if __name__ == "__main__":
    unittest.main()
