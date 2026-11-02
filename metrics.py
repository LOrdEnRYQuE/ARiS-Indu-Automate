"""Transparent equipment-level metrics from simulation events.

OEE is intentionally unavailable: the simulator has no verified planned
production time, ideal cycle-time baseline, or good/reject counts.
"""
def equipment_metrics(events):
    latest = {}
    counts = {}
    for event in events:
        machine = event["equipment_id"]
        previous = latest.get(machine)
        if previous is None or event["sequence"] > previous["sequence"]:
            latest[machine] = event
        if machine not in counts:
            counts[machine] = {"alarm_events": 0, "event_count": 0}
        counts[machine]["event_count"] += 1
        if event["status"] == "alarm":
            counts[machine]["alarm_events"] += 1
    return {
        machine: {
            "produced_units": event["produced_units"],
            "latest_status": event["status"],
            "alarm_events": counts[machine]["alarm_events"],
            "event_count": counts[machine]["event_count"],
            "oee": None,
            "oee_status": "insufficient_data",
        }
        for machine, event in latest.items()
    }
