"""Create a persistent demo database then launch the localhost-only dashboard."""
from pathlib import Path
from dashboard import make_handler
from gateway import Gateway
from demo_seed import seed_demo
from http.server import ThreadingHTTPServer

path = Path("telemetry.db")
gateway = Gateway(path)
try:
    seed_demo(gateway)
finally:
    gateway.close()
print("ARiS demo: http://127.0.0.1:8765 (Ctrl+C to stop)", flush=True)
ThreadingHTTPServer(("127.0.0.1", 8765), make_handler(path)).serve_forever()
