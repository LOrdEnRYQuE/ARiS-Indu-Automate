"""Read-only local SQLite diagnostics; never physical equipment safety verification."""
import json
import sqlite3
from pathlib import Path

from gateway import validate


def diagnose_database(path):
    """Inspect an existing database without schema migrations or writes."""
    result = {"storage_state": "degraded", "reason": "database_missing",
              "event_count": None, "physical_safety_verified": False}
    if not Path(path).is_file():
        return result
    connection = None
    try:
        connection = sqlite3.connect(f"file:{Path(path).resolve().as_posix()}?mode=ro", uri=True)
        integrity = connection.execute("PRAGMA quick_check").fetchone()
        if integrity is None or integrity[0] != "ok":
            return {**result, "reason": "sqlite_integrity_error"}
        rows = connection.execute(
            "SELECT equipment_id, sequence, payload FROM telemetry ORDER BY equipment_id, sequence"
        ).fetchall()
        for equipment_id, sequence, payload in rows:
            event = json.loads(payload)
            validate(event)
            if event["equipment_id"] != equipment_id or event["sequence"] != sequence:
                raise ValueError("stored identity mismatch")
        return {"storage_state": "ready", "reason": None,
                "event_count": len(rows), "physical_safety_verified": False}
    except (sqlite3.DatabaseError, ValueError, TypeError, KeyError, OSError):
        return {**result, "reason": "telemetry_integrity_error"}
    finally:
        if connection is not None:
            connection.close()
