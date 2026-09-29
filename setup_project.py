"""Initialize an isolated Python 3.12 environment beside this file."""
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent
ENV = ROOT / ".venv"
PYTHON = ENV / "Scripts" / "python.exe"

def run(*args):
    subprocess.run([str(a) for a in args], cwd=ROOT, check=True)

def main():
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError("Use Python 3.12: py -3.12 setup_project.py")
    if not ENV.exists():
        print("Creating project .venv ...", flush=True)
        venv.EnvBuilder(with_pip=True).create(ENV)
    elif not PYTHON.is_file():
        raise RuntimeError("Existing .venv is incomplete. Rename it, then run setup again.")
    run(PYTHON, "-c", "import sys; assert sys.version_info[:2] == (3,12); assert sys.prefix != sys.base_prefix")
    print("Installing locked dependencies into project .venv ...", flush=True)
    run(PYTHON, "-m", "pip", "install", "-r", ROOT / "requirements-lock.txt")
    run(PYTHON, "-m", "pip", "check")
    run(PYTHON, "-c", "from model import build; p=build(); assert p.val().isValid(); print('CAD model validation passed.')")
    print("Setup complete. Open Design.code-workspace, then follow README.md.")

if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, OSError) as error:
        print(f"Setup failed: {error}", file=sys.stderr)
        sys.exit(1)
