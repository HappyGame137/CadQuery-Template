"""Export and validate the model independently of the viewer."""
from pathlib import Path
import json
import struct
import cadquery as cq
from model import build

out = Path(__file__).with_name("exports")
out.mkdir(exist_ok=True)
part = build()
shape = part.val()
assert shape.isValid() and len(shape.Solids()) == 1
b = shape.BoundingBox()  # Compute before STL tessellation adds triangulation tolerances.
cq.exporters.export(part, str(out / "model.step"))
cq.exporters.export(part, str(out / "model.stl"), tolerance=0.05, angularTolerance=0.1)
restored = cq.importers.importStep(str(out / "model.step")).val()
assert restored.isValid()
assert abs(restored.Volume() - shape.Volume()) < 1e-5
stl = (out / "model.stl").read_bytes()
triangles = struct.unpack_from("<I", stl, 80)[0]
assert len(stl) == 84 + 50 * triangles and triangles > 0
report = {"valid": True, "solids": len(shape.Solids()),
          "size_mm": [b.xlen, b.ylen, b.zlen], "volume_mm3": shape.Volume(),
          "step_roundtrip_valid": True, "stl_triangles": triangles}
(out / "validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))

