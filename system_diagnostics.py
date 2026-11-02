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
        last_sequences = {}
        last_production = {}
        for equipment_id, sequence, payload in rows:
            previous = last_sequences.get(equipment_id)
            if sequence != (0 if previous is None else previous + 1):
                raise ValueError("historical sequence gap")
            last_sequences[equipment_id] = sequence
            event = json.loads(payload)
            validate(event)
            if event["equipment_id"] != equipment_id or event["sequence"] != sequence:
                raise ValueError("stored identity mismatch")
            previous_units = last_production.get(equipment_id)
            if previous_units is not None and event["produced_units"] < previous_units:
                raise ValueError("simulated production counter regressed")
            last_production[equipment_id] = event["produced_units"]
        return {"storage_state": "ready", "reason": None,
                "event_count": len(rows), "physical_safety_verified": False}
    except (sqlite3.DatabaseError, ValueError, TypeError, KeyError, OSError):
        return {**result, "reason": "telemetry_integrity_error"}
    finally:
        if connection is not None:
            connection.close()
