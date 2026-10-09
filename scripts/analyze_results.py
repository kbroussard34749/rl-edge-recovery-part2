"""Replay and summarize a run; retained original evidence is read-only."""

import argparse
import json
from pathlib import Path
import _bootstrap
from edge_recovery.evidence import analyze
from edge_recovery.paths import ORIGINAL_RUN


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=ORIGINAL_RUN)
    parser.add_argument("--write", action="store_true", help="Write summaries to a reproduction run only")
    arguments = parser.parse_args()
    result = analyze(arguments.run_dir, arguments.write)
    print(json.dumps(result["summary.json"], indent=2))
    print("VERIFIED", result["evidence_checks.json"])
