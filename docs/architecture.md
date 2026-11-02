# ARiS Industrial Automation v0.1

## Scope
Simulation-only telemetry. No robot, PLC, OT network, or production integration.

## Event contract
Fields: equipment_id, source, sequence, status, cycle_time_ms, produced_units, alarm_code.
The source is always `simulator`; equipment IDs are explicitly virtual.

## Roadmap
1. Deterministic simulation with automated tests.
2. Local read-only ingestion API, persistence, monitoring dashboard, and audit logs.
3. Optional AI explanations grounded in alarm evidence; no autonomous machine actions.
4. Authorized real-device pilot only after vendor-specific interface and safety review.

## Safety boundary
No control-plane writes, robot motion commands, safety circuit access, or remote execution.
Industrial deployment requires site-specific risk assessment and authorization.
