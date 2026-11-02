import json
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from dashboard import make_handler, render_dashboard
from gateway import Gateway
from simulator import simulate_line


class EquipmentHealthApiTests(unittest.TestCase):
    def test_health_api_is_read_only_and_machine_specific(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'telemetry.sqlite'
            gateway = Gateway(path)
            for event in simulate_line(5, alarm_at=2):
                gateway.ingest(event)
            gateway.close()
            server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(path))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                conn = HTTPConnection('127.0.0.1', server.server_port, timeout=3)
                conn.request('GET', '/api/health')
                response = conn.getresponse()
                self.assertEqual(response.status, 200)
                payload = json.loads(response.read())
                self.assertEqual(payload['KUKA-VIRTUAL-01']['health'], 'alarm')
                self.assertEqual(payload['KUKA-VIRTUAL-02']['health'], 'running')
                self.assertFalse(payload['KUKA-VIRTUAL-01']['physical_safety_verified'])
                conn.request('POST', '/api/health')
                response = conn.getresponse()
                self.assertEqual(response.status, 405)
                response.read()
                conn.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)

    def test_health_visible_in_dashboard(self):
        events = simulate_line(5, alarm_at=2)
        summary = {'equipment_count': 2, 'event_count': 10, 'produced_units': 7, 'alarm_events': 4}
        html = render_dashboard(summary, events)
        self.assertIn('Equipment health', html)
        self.assertIn('SIMULATION STATUS', html)
