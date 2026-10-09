"""Compatibility entry point for the modular simulation-only project.

Existing demo commands remain available. A new experiment requires --output
and never overwrites retained evidence. The original implementation is preserved
under tests/reference solely for behavioral comparisons.
"""

import argparse
from dataclasses import asdict, replace
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from edge_recovery.controllers import greedy, rule, update
from edge_recovery.environment import ACTIONS, DEMAND, State, loads, physical, available, success, transition
from edge_recovery.evaluation import evaluate, score
from edge_recovery.experiment import load_design, run, write_csv
from edge_recovery.paths import ROOT, ORIGINAL_RUN, SCENARIOS_PATH
from edge_recovery.runtime import peak_rss_bytes
from edge_recovery.safety_filter import step
from edge_recovery.scenarios import state_from, manifest, feasible
from edge_recovery.training import train


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["run", "demo", "validate"])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--episodes", type=int, default=20000)
    parser.add_argument("--scenario", default="cpu_4")
    parser.add_argument("--controller", choices=["filtered", "unshielded", "rule"], default="filtered")
    parser.add_argument("--seed", type=int, default=1000)
    args = parser.parse_args()
    if args.command == "run":
        if args.output is None:
            parser.error("run requires --output pointing to a fresh reproduction directory")
        run(args.output, args.episodes)
    elif args.command == "validate":
        print(json.dumps([dict(id=x["id"], **feasible(state_from(x["initial"])))
                          for x in manifest()], indent=2))
    else:
        _, scenarios = load_design()
        scenario = next(x for x in scenarios if x["id"] == args.scenario)
        if args.controller == "rule":
            q = {}
        else:
            path = ORIGINAL_RUN / "final" / args.controller / str(args.seed) / "policy.json"
            q = {state_from(x["state"]): x["values"] for x in json.loads(path.read_text())}
        rows, traces = evaluate(q, [scenario], args.controller, args.seed, scenario["split"])
        for row in traces:
            print(json.dumps(row, indent=2))
        print("SUMMARY", json.dumps(rows[0], indent=2))
