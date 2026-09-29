# CAD project instructions

- Use `.venv/Scripts/python.exe`; do not install into global Python.
- Edit `model.py` for geometry. Dimensions are millimetres; expose important dimensions as named parameters.
- Preserve `build()` returning a valid CadQuery Workplane containing the model.
- `preview.py` watches saved changes to model.py. Keep it running during iteration; do not start duplicate watchers.
- The watcher watches model.py only. If splitting the model into modules, extend dependency watching/reloading first.
- Run `export.py` after an accepted geometry change to regenerate and validate STEP and STL.
- Avoid opening a second viewer on a different port unintentionally. Default viewer port is 3939.
- Open the project folder directly in VS Code; do not add a .code-workspace file.
- Keep geometry and optional build_parts()/build_assembly() functions in model.py.
- Optional build_parts() returns a non-empty dictionary mapping unique filename-safe names to single-solid Workplanes or Shapes in standalone coordinates.
- Optional build_assembly() returns a named CadQuery Assembly; build() must still return a Workplane representing the same model. Define ASSEMBLY_NAME for the export filename.
- Store standalone STEP/STL in exports/parts/, assemblies in exports/assemblies/, validation.json in exports/reports/, and runtime logs in logs/.
- Generated exports, logs and .venv are ignored by Git. Keep the .gitkeep files for the template directory structure.
- Export validation checks shape validity, solid count, STEP volume round-trip and binary STL structure. Add project-specific assembly interference checks when needed.
