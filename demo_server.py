"""Compatibility command for the modular simulation demonstration."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from edge_recovery.demo_web import main

if __name__ == "__main__":
    main()
