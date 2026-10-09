"""Read-only compatibility command for analysis of the retained original run."""

import json
import recovery
from edge_recovery.evidence import analyze

if __name__ == "__main__":
    artifacts = analyze(recovery.ORIGINAL_RUN)
    print(json.dumps(artifacts["summary.json"], indent=2))
    print("VERIFIED", artifacts["evidence_checks.json"])
