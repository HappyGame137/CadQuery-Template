"""Export standalone parts, an optional assembly, and a validation report."""
import json
import math
from pathlib import Path
import struct

import cadquery as cq

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "exports"
LINEAR_TOLERANCE = 0.05
ANGULAR_TOLERANCE = 0.1


def filename(name):
    """Require one portable filename component; Unicode names are supported."""
    reserved = {"CON", "PRN", "AUX", "NUL"}
    reserved.update(f"{prefix}{i}" for prefix in ("COM", "LPT") for i in range(1, 10))
    if (not isinstance(name, str) or not name or name in (".", "..")
            or any(c in name for c in '<>:"/\\|?*')
            or any(ord(c) < 32 for c in name) or name.endswith((".", " "))
            or name.split(".")[0].upper() in reserved):
        raise ValueError(f"Invalid export name: {name!r}")
    return name


def as_shape(part):
    if isinstance(part, cq.Workplane):
        shapes = part.vals()
        if not shapes or not all(isinstance(s, cq.Shape) for s in shapes):
            raise ValueError("Expected a Workplane containing solid shapes")
        return cq.Compound.makeCompound(shapes)
    if isinstance(part, cq.Shape):
        return part
    raise TypeError("Expected a CadQuery Workplane or Shape")


def export_shape(shape, directory, name, assembly=None):
    solids = len(shape.Solids())
    if not shape.isValid() or solids == 0 or shape.Volume() <= 0:
        raise ValueError(f"Invalid or empty solid: {name}")
    if assembly is None and solids != 1:
        raise ValueError("Each standalone part must contain exactly one solid")
    bounds = shape.BoundingBox()  # Measure before STL tessellation.
    step = directory / f"{name}.step"
    stl = directory / f"{name}.stl"
    if assembly is None:
        cq.exporters.export(shape, str(step))
    else:
        assembly.export(str(step))  # Preserve component names, colours and placement.
    cq.exporters.export(shape, str(stl), tolerance=LINEAR_TOLERANCE,
                        angularTolerance=ANGULAR_TOLERANCE)
    restored = as_shape(cq.importers.importStep(str(step)))
    if (not restored.isValid() or len(restored.Solids()) != solids
            or not math.isclose(restored.Volume(), shape.Volume(), rel_tol=1e-8, abs_tol=1e-5)):
        raise ValueError(f"STEP round-trip failed: {step}")
    data = stl.read_bytes()
    if len(data) < 84:
        raise ValueError(f"Truncated STL: {stl}")
    triangles = struct.unpack_from("<I", data, 80)[0]
    if triangles == 0 or len(data) != 84 + 50 * triangles:
        raise ValueError(f"Invalid binary STL structure: {stl}")
    return {
        "valid": True, "solids": solids,
        "size_mm": [bounds.xlen, bounds.ylen, bounds.zlen],
        "volume_mm3": shape.Volume(), "step_roundtrip_valid": True,
        "stl_triangles": triangles,
        "step": step.relative_to(OUT).as_posix(),
        "stl": stl.relative_to(OUT).as_posix(),
    }


def main():
    for folder in ("parts", "assemblies", "reports"):
        (OUT / folder).mkdir(parents=True, exist_ok=True)
    report_path = OUT / "reports" / "validation.json"
    # A failed run must not leave an earlier success report looking current.
    report_path.write_text(json.dumps({"valid": False, "status": "in_progress"}), encoding="utf-8")
    try:
        import model

        parts = model.build_parts() if hasattr(model, "build_parts") else {
            getattr(model, "MODEL_NAME", "model"): model.build()}
        if not isinstance(parts, dict) or not parts:
            raise ValueError("build_parts() must return a non-empty name-to-part dictionary")
        names = [filename(name) for name in parts]
        if len({name.casefold() for name in names}) != len(names):
            raise ValueError("Part names must be unique on Windows")
        report = {"valid": True, "units": "mm", "parts": {}, "assemblies": {}}
        for name, part in parts.items():
            report["parts"][name] = export_shape(as_shape(part), OUT / "parts", name)
        if hasattr(model, "build_assembly"):
            assembly = model.build_assembly()
            if not isinstance(assembly, cq.Assembly):
                raise TypeError("build_assembly() must return a CadQuery Assembly")
            name = filename(getattr(model, "ASSEMBLY_NAME", "assembly"))
            report["assemblies"][name] = export_shape(
                assembly.toCompound(), OUT / "assemblies", name, assembly)
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(report, indent=2, ensure_ascii=False))
    except Exception as error:
        report_path.write_text(json.dumps({"valid": False, "error": str(error)},
                                         indent=2, ensure_ascii=False), encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
