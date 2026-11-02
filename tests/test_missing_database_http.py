import json
import tempfile
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path

from dashboard import make_handler


class MissingDatabaseHttpTests(unittest.TestCase):
    def test_system_diagnostics_does_not_create_missing_database(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "absent.db"
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(path))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                connection = HTTPConnection("127.0.0.1", server.server_port, timeout=3)
                connection.request("GET", "/api/system")
                response = connection.getresponse()
                data = json.loads(response.read())
                self.assertEqual(response.status, 200)
                self.assertEqual(data["storage_state"], "degraded")
                self.assertEqual(data["reason"], "database_missing")
                self.assertFalse(path.exists())
                connection.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)
