"""Entry point required by the subject: python3 pac-man.py <config.json>."""

import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "src"),
                   run_name="__main__")
