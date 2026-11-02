"""Populate missing simulated equipment without rewriting stored telemetry."""
from simulator import simulate_line


def seed_demo(gateway, cycles=10, alarm_at=7):
    existing = {event["equipment_id"] for event in gateway.events()}
    inserted = 0
    for event in simulate_line(cycles, alarm_at):
        if event["equipment_id"] not in existing:
            inserted += int(gateway.ingest(event))
    return inserted
