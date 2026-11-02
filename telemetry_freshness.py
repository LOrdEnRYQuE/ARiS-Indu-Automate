"""Advisory freshness checks from explicit observation times, never simulated event age."""
import math


def assess_freshness(last_seen_by_equipment, *, now, timeout_seconds=30.0):
    """Classify observation freshness; stale does not prove physical communication loss.

    Timestamps must be from the same clock and supplied by the caller.
    Existing simulator telemetry has no timestamp; do not fabricate one.
    """
    if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool) or not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be finite and positive")
    if not isinstance(now, (int, float)) or isinstance(now, bool) or not math.isfinite(now):
        raise ValueError("now must be a finite number")
    result = {}
    for equipment, last_seen in last_seen_by_equipment.items():
        valid = isinstance(last_seen, (int, float)) and not isinstance(last_seen, bool) and math.isfinite(last_seen) and last_seen <= now
        age = now - last_seen if valid else None
        result[equipment] = {
            "telemetry_state": "unknown" if age is None else ("stale" if age > timeout_seconds else "fresh"),
            "age_seconds": age,
            "communication_loss_confirmed": False,
            "physical_safety_verified": False,
        }
    return result
