"""Verify policy decisions and unseen-state metrics without changing originals."""

import argparse
import json
from pathlib import Path
import _bootstrap
from edge_recovery.paths import ORIGINAL_RUN
from edge_recovery.policy_verification import verify_policy


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=ORIGINAL_RUN)
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    print(json.dumps(verify_policy(arguments.run_dir, arguments.write), indent=2))
