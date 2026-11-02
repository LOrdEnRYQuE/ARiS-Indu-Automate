"""Simulation-only status snapshots; not physical safety monitoring."""


def equipment_health(events):
    latest = {}
    for event in events:
        machine = event['equipment_id']
        if machine not in latest or event['sequence'] > latest[machine]['sequence']:
            latest[machine] = event
    return {
        machine: {
            'health': event.get('status') if event.get('status') in ('running', 'alarm', 'stopped', 'idle') else 'unknown',
            'last_sequence': event['sequence'],
            'alarm_code': event.get('alarm_code'),
            'source': 'simulator',
            'physical_safety_verified': False,
        }
        for machine, event in sorted(latest.items())
    }
