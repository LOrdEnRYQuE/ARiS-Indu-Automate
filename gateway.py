"""Local read-only telemetry gateway. No industrial control or network listeners."""
import json
import sqlite3
from pathlib import Path

REQUIRED = {"equipment_id", "source", "sequence", "status", "cycle_time_ms", "produced_units", "alarm_code"}

def validate(event):
    if not isinstance(event, dict) or set(event) != REQUIRED:
        raise ValueError("invalid event fields")
    if event["source"] != "simulator":
        raise ValueError("only simulated events are accepted in v0.1")
    if not isinstance(event["equipment_id"], str) or not event["equipment_id"].startswith("KUKA-VIRTUAL-"):
        raise ValueError("only virtual equipment is accepted")
    if event["status"] not in ("running", "stopped", "alarm"):
        raise ValueError("invalid status")
    for field in ("sequence", "cycle_time_ms", "produced_units"):
        if type(event[field]) is not int or event[field] < 0:
            raise ValueError("invalid nonnegative integer: " + field)
    if event["alarm_code"] is not None and not isinstance(event["alarm_code"], str):
        raise ValueError("invalid alarm code")
    if (event["status"] == "alarm") != (event["alarm_code"] is not None):
        raise ValueError("alarm status and code must agree")
    return event

class Gateway:
    def __init__(self, path):
        self.connection = sqlite3.connect(str(Path(path)))
        self.connection.execute("""CREATE TABLE IF NOT EXISTS telemetry (
            equipment_id TEXT NOT NULL,
            sequence INTEGER NOT NULL,
            payload TEXT NOT NULL,
            PRIMARY KEY(equipment_id, sequence)
        )""")
        self.connection.commit()

    def ingest(self, event):
        event = validate(event)
        payload = json.dumps(event, sort_keys=True)
        with self.connection:
            existing = self.connection.execute(
                "SELECT payload FROM telemetry WHERE equipment_id=? AND sequence=?",
                (event["equipment_id"], event["sequence"])
            ).fetchone()
            if existing is not None:
                if existing[0] != payload:
                    raise ValueError("conflicting duplicate event")
                return False
            last = self.connection.execute(
                "SELECT MAX(sequence) FROM telemetry WHERE equipment_id=?",
                (event["equipment_id"],)
            ).fetchone()[0]
            if last is not None and event["sequence"] != last + 1:
                raise ValueError("out-of-order event")
            if last is None and event["sequence"] != 0:
                raise ValueError("first sequence must be zero")
            self.connection.execute(
                "INSERT INTO telemetry VALUES (?, ?, ?)",
                (event["equipment_id"], event["sequence"], payload)
            )
        return True

    def events(self):
        rows = self.connection.execute(
            "SELECT payload FROM telemetry ORDER BY equipment_id, sequence"
        ).fetchall()
        return [json.loads(row[0]) for row in rows]

    def summary(self):
        events = self.events()
        if not events:
            return {"equipment_count": 0, "event_count": 0, "produced_units": 0, "alarm_events": 0}
        latest = {}
        for event in events:
            latest[event["equipment_id"]] = event
        return {
            "equipment_count": len(latest),
            "event_count": len(events),
            "produced_units": sum(e["produced_units"] for e in latest.values()),
            "alarm_events": sum(e["status"] == "alarm" for e in events),
        }

    def close(self):
        self.connection.close()
