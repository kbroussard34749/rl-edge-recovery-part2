"""Check learned commands and unseen-state metrics against saved policies.

Each command must match greedy selection from its actual saved Q-table. Entire
policy evaluations must also match retained CSV records, including unseen-state
counts. This verifies evidence consistency; it does not improve the policy.
"""

import csv
import json
from pathlib import Path

from .controllers import greedy
from .environment import ACTIONS
from .evaluation import evaluate
from .paths import protect_original
from .scenarios import manifest, state_from


def verify_policy(run_dir: Path, write: bool = False) -> dict:
    """Verify all saved learned decisions, optionally writing a new-run record."""
    run_dir = run_dir.resolve()
    if write:
        protect_original(run_dir)
    cache = {}
    checked = 0
    for line in (run_dir / "traces.jsonl").read_text().splitlines():
        decision = json.loads(line)
        if decision["controller"] == "rule":
            continue
        key = (decision["controller"], decision["seed"])
        if key not in cache:
            path = run_dir / "final" / key[0] / str(key[1]) / "policy.json"
            cache[key] = {state_from(entry["state"]): entry["values"]
                          for entry in json.loads(path.read_text())}
        q = cache[key]
        state = state_from(decision["state"])
        assert ACTIONS[greedy(q.get(state, [0.] * 9))] == decision["proposed"]
        checked += 1

    # Re-evaluate each policy instead of trusting its aggregate report. This
    # independently verifies unseen-state counts as well as recovery metrics.
    with (run_dir / "evaluation.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    for (controller, seed), q in cache.items():
        for split in ("test", "train"):
            actual, _ = evaluate(q, manifest(), controller, seed, split, False)
            for episode in actual:
                saved = next(row for row in rows if
                             row["controller"] == controller and row["seed"] == str(seed)
                             and row["scenario"] == episode["scenario"] and row["split"] == split)
                assert all(str(saved[key]) == str(value) for key, value in episode.items())
    result = dict(policy_decisions_checked=checked, policies_loaded=len(cache),
                  policy_and_unseen_metrics_verified=True)
    if write:
        (run_dir / "policy_checks.json").write_text(json.dumps(result, indent=2))
    return result
