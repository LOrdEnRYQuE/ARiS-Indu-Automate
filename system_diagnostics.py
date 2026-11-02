"""Read-only local storage diagnostics; never a physical equipment safety check."""
import sqlite3

from gateway import Gateway


def diagnose_database(path):
    """Inspect persisted simulated telemetry without claiming machine health."""
    gateway = None
    try:
        gateway = Gateway(path)
        integrity = gateway.connection.execute("PRAGMA quick_check").fetchone()
        if integrity is None or integrity[0] != "ok":
            return {"storage_state": "degraded", "reason": "sqlite_integrity_error", "event_count": None, "physical_safety_verified": False}
        count = len(gateway.events())
        return {"storage_state": "ready", "reason": None, "event_count": count, "physical_safety_verified": False}
    except (sqlite3.DatabaseError, ValueError, OSError):
        return {"storage_state": "degraded", "reason": "telemetry_integrity_error", "event_count": None, "physical_safety_verified": False}
    finally:
        if gateway is not None:
            gateway.close()
