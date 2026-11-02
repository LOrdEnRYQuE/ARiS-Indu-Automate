import tempfile
import unittest
from pathlib import Path

from system_diagnostics import diagnose_database


class DiagnosticsMissingDatabaseTests(unittest.TestCase):
    def test_missing_database_is_not_created_or_reported_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.db"
            result = diagnose_database(path)
            self.assertFalse(path.exists())
            self.assertEqual(result["storage_state"], "degraded")
            self.assertEqual(result["reason"], "database_missing")
            self.assertFalse(result["physical_safety_verified"])
