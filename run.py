import subprocess
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
PYTHON = VENV / "Scripts" / "python.exe"
REQUIREMENTS = ROOT / "requirements.txt"
INSTALLED = VENV / "installed_req"
PY = str(PYTHON)


def run(command):
    result = subprocess.run(command, cwd=ROOT)
    return result.returncode


def ensure_venv():
    if not PYTHON.exists():
        print("Creating virtual environment...")
        run([sys.executable, "-m", "venv", str(VENV)])

    if REQUIREMENTS.exists():
        needs_install = not INSTALLED.exists() or (REQUIREMENTS.stat().st_mtime > INSTALLED.stat().st_mtime)

        if needs_install:
            print("Installing or updating requirements...")
            run([PY, "-m", "pip", "install", "--upgrade", "pip"])
            run([PY, "-m", "pip", "install", "-r", str(REQUIREMENTS)])
            INSTALLED.parent.mkdir(parents=True, exist_ok=True)
            INSTALLED.touch()

    return PY


def main():
    python = ensure_venv()
    parser = argparse.ArgumentParser()
    parser.add_argument("script", help="The Python script or module to run")
    parser.add_argument("script_args", nargs=argparse.REMAINDER, help="Arguments to pass to the script")
    args = parser.parse_args()

    cmd = [python, args.script] + args.script_args
    sys.exit(run(cmd))


if __name__ == "__main__":
    main()