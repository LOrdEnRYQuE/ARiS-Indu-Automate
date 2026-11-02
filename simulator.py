"""Simulation-only industrial telemetry. Never connects to hardware."""
from dataclasses import asdict, dataclass
import json

@dataclass(frozen=True)
class Event:
    equipment_id: str
    source: str
    sequence: int
    status: str
    cycle_time_ms: int
    produced_units: int
    alarm_code: str | None

def simulate(cycles: int = 10, alarm_at: int | None = None) -> list[dict]:
    if type(cycles) is not int or not 0 <= cycles <= 100000:
        raise ValueError("cycles must be an integer from 0 to 100000")
    if alarm_at is not None and (type(alarm_at) is not int or not 0 <= alarm_at < cycles):
        raise ValueError("alarm_at must identify a valid cycle")
    events = []
    for i in range(cycles):
        alarm = alarm_at is not None and i >= alarm_at
        events.append(asdict(Event(
            equipment_id="KUKA-VIRTUAL-01", source="simulator", sequence=i,
            status="alarm" if alarm else "running", cycle_time_ms=12500,
            produced_units=alarm_at if alarm else i + 1,
            alarm_code="SIM_FEED_BLOCKED" if alarm else None,
        )))
    return events

if __name__ == "__main__":
    print(json.dumps(simulate(10, alarm_at=7), indent=2))

def simulate_line(cycles: int = 10, alarm_at: int | None = None) -> list[dict]:
    """Simulate two independent virtual machines, one with optional feed alarm.

    The second machine continues producing when the first enters alarm.
    These are equipment-level counts, not verified finished-line output.
    """
    primary = simulate(cycles, alarm_at)
    secondary = [
        {**event, "equipment_id": "KUKA-VIRTUAL-02"}
        for event in simulate(cycles)
    ]
    return [event for pair in zip(primary, secondary) for event in pair]
