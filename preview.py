"""Keep Python warm; refresh on saved model.py changes (including AI edits)."""
import argparse
import hashlib
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import runpy
import time
import cadquery  # Warm up the CAD kernel once.
from ocp_vscode import show, set_port, Camera

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=3939)
args = parser.parse_args()
set_port(args.port)
source = Path(__file__).with_name("model.py")
log_dir = source.parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    handlers=[logging.StreamHandler(), RotatingFileHandler(
                        log_dir / "preview.log", maxBytes=2_000_000, backupCount=2, encoding="utf-8")])
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
                if (not isinstance(part, cadquery.Workplane) or not part.vals()
                        or not all(isinstance(shape, cadquery.Shape) and shape.isValid()
                                   and shape.Solids() for shape in part.vals())):
                    raise ValueError("Invalid solid")
                if "build_assembly" in namespace:
                    display = namespace["build_assembly"]()
                    if (not isinstance(display, cadquery.Assembly)
                            or not display.toCompound().isValid()
                            or not display.toCompound().Solids()):
                        raise ValueError("Invalid assembly")
                    show(display, reset_camera=Camera.KEEP)
                else:
                    show(part, names=[namespace.get("MODEL_NAME", "model")],
                         colors=["#58a6ff"], reset_camera=Camera.KEEP)
                previous = fingerprint
                logging.info("Preview updated in %.2fs", time.perf_counter() - started)
        except Exception:
            previous = fingerprint if 'fingerprint' in locals() else None
            logging.exception("Preview update failed; last good preview is retained")
            print("Fix and save model.py to retry; last good preview is retained.", flush=True)
        time.sleep(0.3)
except KeyboardInterrupt:
    print("Preview stopped.")
