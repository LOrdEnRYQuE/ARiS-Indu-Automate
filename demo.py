"""Run a local end-to-end simulator -> gateway -> SQLite demonstration."""
import json
import tempfile
from pathlib import Path
from gateway import Gateway
from simulator import simulate

with tempfile.TemporaryDirectory() as directory:
    gateway = Gateway(Path(directory) / "telemetry.db")
    for event in simulate(10, alarm_at=7):
        gateway.ingest(event)
    print(json.dumps(gateway.summary(), indent=2))
    gateway.close()
