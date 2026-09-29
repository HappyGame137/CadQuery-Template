"""Keep Python warm; refresh on saved model.py changes (including AI edits)."""
import argparse
import hashlib
from pathlib import Path
import runpy
import time
import traceback
import cadquery  # Warm up the CAD kernel once.
from ocp_vscode import show, set_port, Camera

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=3939)
args = parser.parse_args()
set_port(args.port)
source = Path(__file__).with_name("model.py")
previous = None
print(f"Watching {source.name}; viewer port {args.port}. Ctrl+C to stop.", flush=True)
try:
    while True:
        try:
            content = source.read_bytes()
            fingerprint = hashlib.sha256(content).digest()
            if fingerprint != previous:
                time.sleep(0.2)
                if source.read_bytes() != content:
                    continue
                started = time.perf_counter()
                namespace = runpy.run_path(str(source), run_name="cad_model")
                part = namespace["build"]()
                if not part.val().isValid():
                    raise ValueError("Invalid solid")
                show(part, names=["Mounting plate"], colors=["#58a6ff"],
                     reset_camera=Camera.KEEP)
                previous = fingerprint
                print(f"Updated {time.strftime('%H:%M:%S')} in {time.perf_counter()-started:.2f}s", flush=True)
        except Exception:
            previous = fingerprint if 'fingerprint' in locals() else None
            traceback.print_exc()
            print("Fix and save model.py to retry; last good preview is retained.", flush=True)
        time.sleep(0.3)
except KeyboardInterrupt:
    print("Preview stopped.")
