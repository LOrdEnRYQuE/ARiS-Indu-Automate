"""Evidence-grounded simulator alarm advisor. Not a live LLM or control agent."""
from typing import Any

_KNOWN = {
    "SIM_FEED_BLOCKED": {
        "severity": "warning",
        "explanation": "Simulated feed blockage alarm; the simulator stops incrementing produced units.",
        "recommendation": "Review the simulated feed stage and event sequence. In a real facility, follow site-approved procedures and qualified personnel instructions.",
    }
}

def analyze(event: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(event, dict) or event.get("source") != "simulator":
        raise ValueError("Only simulator evidence is supported")
    equipment = event.get("equipment_id")
    if not isinstance(equipment, str) or not equipment.startswith("KUKA-VIRTUAL-"):
        raise ValueError("Only virtual KUKA identifiers are supported")
    status = event.get("status")
    alarm = event.get("alarm_code")
    if status not in ("running", "stopped", "alarm"):
        raise ValueError("Invalid equipment status")
    if status == "alarm" and (not isinstance(alarm, str) or not alarm):
        raise ValueError("Alarm status requires a code")
    if status != "alarm" and alarm is not None:
        raise ValueError("Non-alarm status must not contain an alarm code")
    if status != "alarm":
        severity, basis = "info", "observed_status"
        explanation = "Simulator reports status: " + status
        recommendation = "Continue observing simulated telemetry."
    elif alarm in _KNOWN:
        entry = _KNOWN[alarm]
        severity, basis = entry["severity"], "known_simulator_alarm"
        explanation, recommendation = entry["explanation"], entry["recommendation"]
    else:
        severity, basis = "warning", "unknown_alarm"
        explanation = "Unknown simulator alarm code; root cause cannot be determined from this event."
        recommendation = "Inspect simulated event history; do not assume a physical cause."
    return {
        "equipment_id": equipment, "alarm_code": alarm, "severity": severity,
        "basis": basis, "explanation": explanation, "recommendation": recommendation,
        "machine_command_allowed": False, "mode": "advisory_only",
    }
