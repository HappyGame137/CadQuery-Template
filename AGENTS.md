# CAD project instructions

- Use `.venv/Scripts/python.exe`; do not install into global Python.
- Edit `model.py` for geometry. Dimensions are millimetres; expose important dimensions as named parameters.
- Preserve `build()` returning a valid CadQuery Workplane containing the model.
- `preview.py` watches saved changes to model.py. Keep it running during iteration; do not start duplicate watchers.
- The watcher watches model.py only. If splitting the model into modules, extend dependency watching/reloading first.
- Run `export.py` after an accepted geometry change to regenerate and validate STEP and STL.
- Avoid opening a second viewer on a different port unintentionally. Default viewer port is 3939.
