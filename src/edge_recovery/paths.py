"""Locate source configuration and retained evidence from this source checkout."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL_RUN = ROOT / "results/original_run"
CONFIG_PATH = ROOT / "config/experiment.json"
SCENARIOS_PATH = ROOT / "config/scenarios.json"


def protect_original(destination: Path):
    """Reject writes anywhere inside the retained original evidence tree."""
    destination = destination.resolve()
    original = ORIGINAL_RUN.resolve()
    if destination == original or original in destination.parents:
        raise ValueError("The original run is read-only; choose a reproduction directory")
