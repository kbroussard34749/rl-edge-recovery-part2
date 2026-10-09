"""Locate source configuration and retained evidence from this source checkout."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Updated in the evidence-relocation increment after file identity is checked.
ORIGINAL_RUN = ROOT / "outputs"
CONFIG_PATH = ROOT / "config.json"
SCENARIOS_PATH = ROOT / "scenarios.json"


def protect_original(destination: Path):
    """Reject writes anywhere inside the retained original evidence tree."""
    destination = destination.resolve()
    original = ORIGINAL_RUN.resolve()
    if destination == original or original in destination.parents:
        raise ValueError("The original run is read-only; choose a reproduction directory")
