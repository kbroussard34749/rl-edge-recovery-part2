"""Run the retained design in a fresh directory chosen with --output."""

import argparse
from pathlib import Path
import _bootstrap
from edge_recovery.experiment import run


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--episodes", type=int, default=20000,
                        help="20,000 for the full study; smaller values are development only")
    arguments = parser.parse_args()
    run(arguments.output, arguments.episodes)
