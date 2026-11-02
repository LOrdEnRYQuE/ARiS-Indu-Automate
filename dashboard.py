"""Local-only, read-only HTML dashboard for simulated factory telemetry."""
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import time
from gateway import Gateway
from ai_engineer import analyze
from metrics import equipment_metrics
from equipment_health import equipment_health
from telemetry_freshness import assess_freshness
from system_diagnostics import diagnose_database

def render_dashboard(summary, events, freshness=None, diagnostics=None):
    cards = [
        ("Virtual machines", summary["equipment_count"]),
        ("Telemetry events", summary["event_count"]),
        ("Produced units", summary["produced_units"]),
        ("Alarm events", summary["alarm_events"]),
    ]
    blocks = "".join(
        f'<section class="card"><small>{escape(label)}</small><strong>{value}</strong></section>'
        for label, value in cards
    )
    rows = "".join(
        "<tr>" + "".join(f"<td>{escape(str(e[field]))}</td>" for field in
        ("equipment_id", "sequence", "status", "produced_units", "alarm_code")) + "</tr>"
        for e in reversed(events[-100:])
    )
    metric_rows = "".join(
        "<tr><td>" + escape(machine) + "</td><td>" +
        str(item["produced_units"]) + "</td><td>" +
        str(item["alarm_events"]) + "</td><td>" +
        escape(item["latest_status"]) + "</td><td>" +
        escape(item["oee_status"]) + "</td></tr>"
        for machine, item in sorted(equipment_metrics(events).items())
    )
    health_rows = "".join(
        "<tr><td>" + escape(machine) + "</td><td>" +
        escape(str(item["health"])) + "</td><td>" +
        escape(str(item["alarm_code"])) + "</td></tr>"
        for machine, item in equipment_health(events).items()
    )
    freshness_rows = "".join(
        "<tr><td>" + escape(machine) + "</td><td>" +
        escape(str(item["telemetry_state"])) + "</td><td>" +
        ("unknown" if item["age_seconds"] is None else str(round(item["age_seconds"], 1))) +
        "</td></tr>" for machine, item in sorted((freshness or {}).items())
    )
    diagnostics = diagnostics or {"storage_state": "unknown", "reason": None}
    diagnostics_panel = "<p>Storage: " + escape(str(diagnostics["storage_state"])) + " | Reason: " + escape(str(diagnostics.get("reason"))) + "</p>"
    advice = ""
    if events:
        latest = {}
        for event in events:
            latest[event["equipment_id"]] = event
        entries = []
        for event in latest.values():
            try:
                result = analyze(event)
            except (ValueError, TypeError):
                result = {"equipment_id": str(event.get("equipment_id", "UNKNOWN")), "explanation": "Telemetry validation failed.", "recommendation": "Review input data.", "basis": "unverified_event"}
            entries.append(
                "<article class=\"card\"><h3>" + escape(result["equipment_id"]) +
                "</h3><p>" + escape(result["explanation"]) +
                "</p><p>" + escape(result["recommendation"]) +
                "</p><small>Evidence: " + escape(result["basis"]) +
                " | Advisory only — no machine commands</small></article>"
            )
        advice = "".join(entries)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="5">
<title>ARiS Industrial | Simulation Dashboard</title>
<style>
body{{font:16px system-ui;background:#101826;color:#f2f5fb;margin:0;padding:2rem}}
header{{margin-bottom:2rem}}h1{{margin:0}}p,small{{color:#aebbd0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:1rem}}
.card{{background:#1b2940;border:1px solid #324461;border-radius:12px;padding:1.2rem}}
strong{{display:block;font-size:2rem;margin-top:.5rem}}
table{{width:100%;border-collapse:collapse;margin-top:1rem}}
th,td{{text-align:left;padding:.75rem;border-bottom:1px solid #324461}}
.wrapper{{overflow-x:auto}}.notice{{color:#ffd58a}}
</style></head><body><header><h1>ARiS Industrial Automation</h1>
<p class="notice">SIMULATION ONLY — No industrial hardware connected</p>
<p>Local read-only dashboard · refreshes every 5 seconds</p></header>
<main><div class="grid">{blocks}</div>
<h2>Equipment performance</h2><div class="wrapper"><table><thead><tr>
<th>Equipment</th><th>Produced units</th><th>Alarm events</th><th>Latest status</th><th>OEE</th>
</tr></thead><tbody>{metric_rows}</tbody></table></div>
<h2>Equipment health</h2><p>SIMULATION STATUS — not physical safety verification</p><div class="wrapper"><table><thead><tr><th>Equipment</th><th>Health</th><th>Alarm</th></tr></thead><tbody>{health_rows}</tbody></table></div>
<h2>System diagnostics</h2><p>Not a physical safety check</p>{diagnostics_panel}
<h2>Telemetry freshness</h2><p>Not proof of communication loss or physical safety</p><div class="wrapper"><table><thead><tr><th>Equipment</th><th>Freshness</th><th>Age (seconds)</th></tr></thead><tbody>{freshness_rows}</tbody></table></div>
<h2>AI Engineer — advisory only</h2><div class="grid">{advice}</div><h2>Recent telemetry</h2>
<div class="wrapper"><table><thead><tr><th>Equipment</th><th>Sequence</th>
<th>Status</th><th>Units</th><th>Alarm</th></tr></thead><tbody>{rows}</tbody>
</table></div></main></body></html>"""

def make_handler(database_path):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in ("/", "/api/summary", "/api/events", "/api/metrics", "/api/health", "/api/freshness", "/api/system"):
                self.send_error(404)
                return
            try:
                gateway = Gateway(database_path)
                try:
                    summary, events = gateway.summary(), gateway.events()
                    receipts = gateway.receipt_times()
                finally:
                    gateway.close()
                if self.path == "/":
                    body = render_dashboard(summary, events, assess_freshness(receipts, now=time.time()), diagnose_database(database_path)).encode("utf-8")
                    content_type = "text/html; charset=utf-8"
                else:
                    data = summary if self.path == "/api/summary" else (equipment_metrics(events) if self.path == "/api/metrics" else (equipment_health(events) if self.path == "/api/health" else (assess_freshness(receipts, now=time.time()) if self.path == "/api/freshness" else (diagnose_database(database_path) if self.path == "/api/system" else events))))
                    body = json.dumps(data).encode("utf-8")
                    content_type = "application/json"
                self.send_response(200)
                self.send_header("Content-Type", content_type)
                self.send_header("Cache-Control", "no-store")
                self.send_header("X-Content-Type-Options", "nosniff")
                self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'")
                self.end_headers()
                self.wfile.write(body)
            except Exception:
                self.send_error(500, "Unable to read simulation telemetry")
        def do_POST(self):
            self.send_error(405, "Read-only dashboard")
    return Handler

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", default="telemetry.db")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    print(f"Read-only simulator dashboard: http://127.0.0.1:{args.port}")
    ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(Path(args.database))).serve_forever()
